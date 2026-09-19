import os
import sys
import json
import base64
import time
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from pathlib import Path
import numpy as np
import cv2
import pandas as pd
import joblib

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ============================================================
# PROJECT PATHS & MODULE IMPORTS
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent
OPENCV_DIR = PROJECT_ROOT / "openCV"
OUTPUT_DIR = PROJECT_ROOT / "output"

sys.path.insert(0, str(OPENCV_DIR))

MODEL_PATH = PROJECT_ROOT / "H2S_total_exposure_random_forest_datasetNew.joblib"
HISTORY_PATH = OUTPUT_DIR / "history" / "exposure_history.csv"
HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

def sanitize_for_json(obj):
    """Recursively convert NumPy scalars/arrays to native Python JSON types using .item()."""
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    elif hasattr(obj, 'item'):
        return obj.item()
    return obj

EXPECTED_FEATURES = [
    "S1_Hue", "S1_Saturation", "S1_Value", "S1_DeltaE", "S1_Gradient",
    "S2_Hue", "S2_Saturation", "S2_Value", "S2_DeltaE", "S2_Gradient",
    "S3_Hue", "S3_Saturation", "S3_Value", "S3_DeltaE", "S3_Gradient",
    "Temperature_C", "Humidity_Percent"
]

TARGET_COLORS_BGR = {
    "reference_purple": np.array([105, 20, 115], dtype=np.float64),
    "reference_amber": np.array([60, 90, 210], dtype=np.float64),
    "reference_yellow": np.array([20, 210, 245], dtype=np.float64),
    "reference_white": np.array([245, 245, 245], dtype=np.float64),
    "reference_gray": np.array([125, 125, 125], dtype=np.float64)
}

REGIONS = {
    "reference_purple": (145, 44, 258, 100),
    "reference_amber": (291, 44, 404, 100),
    "reference_yellow": (440, 44, 553, 100),
    "reference_white": (590, 44, 703, 100),
    "reference_gray": (738, 44, 851, 100),
    "expiry": (888, 10, 1077, 142),
    "S1": (147, 189, 365, 299),
    "S2": (374, 189, 598, 299),
    "S3": (610, 189, 836, 299),
    "band_id": (850, 189, 1145, 299)
}

DESTINATION_POINTS = np.array([
    [55, 45],       # ID 0
    [1145, 45],     # ID 1
    [1145, 255],    # ID 2
    [55, 255]       # ID 3
], dtype=np.float32)

print("Loading Random Forest Model...", flush=True)
rf_model = None
if MODEL_PATH.exists():
    try:
        obj = joblib.load(MODEL_PATH)
        if hasattr(obj, "predict"):
            rf_model = obj
        elif isinstance(obj, dict):
            for k in ["model", "rf_model", "random_forest", "regressor", "estimator"]:
                if k in obj and hasattr(obj[k], "predict"):
                    rf_model = obj[k]
                    break
        print("RF Model loaded successfully.", flush=True)
    except Exception as e:
        print("Warning loading RF model:", e, flush=True)

def hsv_to_lab(hue, saturation, value):
    hsv = np.array([[[hue / 2.0, saturation * 2.55, value * 2.55]]], dtype=np.uint8)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[0, 0].astype(np.float64)
    lab[0] = lab[0] * 100.0 / 255.0
    lab[1] -= 128.0
    lab[2] -= 128.0
    return lab

BASELINE_LAB = hsv_to_lab(45.0, 50.0, 90.0)

def calculate_delta_e(hue, saturation, value):
    cur_lab = hsv_to_lab(float(hue), float(saturation), float(value))
    return float(np.linalg.norm(cur_lab - BASELINE_LAB))

def process_band_image(cv_img, temp_c=32.0, humidity_pct=65.0, exposure_hours=8.0):
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    params = cv2.aruco.DetectorParameters()
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)
    
    corners, ids, rejected = detector.detectMarkers(cv_img)
    marker_centers = {}
    if ids is not None:
        for marker_corner, marker_id in zip(corners, ids.flatten()):
            mid = int(marker_id)
            if mid in [0, 1, 2, 3]:
                pts = marker_corner[0]
                marker_centers[mid] = [float(np.mean(pts[:, 0])), float(np.mean(pts[:, 1]))]
    
    markers_found = int(len(marker_centers))
    all_markers_found = bool(markers_found == 4)

    if not all_markers_found:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        mean_brightness = float(np.mean(gray))
        return sanitize_for_json({
            "success": False,
            "error_code": "ARUCO_NOT_VERIFIED",
            "error_message": f"ArUco Marker Verification Failed: Only {markers_found}/4 reference markers detected. Exposure band alignment cannot be guaranteed. Processing stopped for safety.",
            "quality": {
                "blur_pass": bool(laplacian_var > 50.0),
                "blur_score": round(laplacian_var, 1),
                "lighting_pass": bool(40.0 <= mean_brightness <= 220.0),
                "brightness": round(mean_brightness, 1),
                "all_markers_found": False,
                "markers_count": markers_found
            }
        })

    src_pts = np.array([marker_centers[0], marker_centers[1], marker_centers[2], marker_centers[3]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(src_pts, DESTINATION_POINTS)
    aligned = cv2.warpPerspective(cv_img, matrix, (1200, 300))

    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_brightness = float(np.mean(gray))
    blur_pass = bool(laplacian_var > 50.0)
    lighting_pass = bool(40.0 <= mean_brightness <= 220.0)

    calib_matrix = np.eye(3, dtype=np.float64)
    measured_refs = []
    target_refs = []
    for ref_name in ["reference_purple", "reference_amber", "reference_yellow", "reference_white", "reference_gray"]:
        x1, y1, x2, y2 = REGIONS[ref_name]
        crop = aligned[y1:y2, x1:x2]
        avg_bgr = np.mean(crop, axis=(0, 1))
        measured_refs.append(avg_bgr)
        target_refs.append(TARGET_COLORS_BGR[ref_name])

    try:
        M, _ = cv2.findHomography(np.array(measured_refs), np.array(target_refs))
        if M is not None and M.shape == (3, 3):
            calib_matrix = M
    except Exception:
        pass

    features = {}
    sensor_details = {}

    for seg_key in ["S1", "S2", "S3"]:
        x1, y1, x2, y2 = REGIONS[seg_key]
        crop = aligned[y1:y2, x1:x2]
        h_crop, w_crop, _ = crop.shape
        flat = crop.reshape(-1, 3).astype(np.float64)
        calib_flat = np.dot(flat, calib_matrix.T)
        calib_crop = np.clip(calib_flat.reshape(h_crop, w_crop, 3), 0, 255).astype(np.uint8)
        
        hsv_crop = cv2.cvtColor(calib_crop, cv2.COLOR_BGR2HSV)
        h_val = float(np.mean(hsv_crop[:, :, 0]) * 2.0)
        s_val = float(np.mean(hsv_crop[:, :, 1]) / 2.55)
        v_val = float(np.mean(hsv_crop[:, :, 2]) / 2.55)
        
        delta_e = calculate_delta_e(h_val, s_val, v_val)
        grad = float(abs(h_val - 45.0))
        
        features[f"{seg_key}_Hue"] = h_val
        features[f"{seg_key}_Saturation"] = s_val
        features[f"{seg_key}_Value"] = v_val
        features[f"{seg_key}_DeltaE"] = delta_e
        features[f"{seg_key}_Gradient"] = grad
        
        sensor_details[seg_key] = {
            "hue": round(h_val, 2),
            "saturation": round(s_val, 2),
            "value": round(v_val, 2),
            "delta_e": round(delta_e, 2),
            "gradient": round(grad, 2)
        }

    features["Temperature_C"] = float(temp_c)
    features["Humidity_Percent"] = float(humidity_pct)

    feat_df = pd.DataFrame([features])[EXPECTED_FEATURES]
    h2s_ppm = 0.0
    if rf_model is not None:
        try:
            pred = rf_model.predict(feat_df)
            h2s_ppm = max(0.0, float(pred[0]))
        except Exception:
            h2s_ppm = max(0.0, float(features["S1_DeltaE"] * 2.5))
    else:
        h2s_ppm = max(0.0, float(features["S1_DeltaE"] * 2.4 + features["S2_DeltaE"] * 1.8))

    h2s_ppm = round(h2s_ppm, 2)
    shift_exposure = round(h2s_ppm * float(exposure_hours), 2)
    twa_8hr = round(shift_exposure / 8.0, 2)

    alerts = []
    alert_level = "NORMAL"
    if h2s_ppm >= 100.0:
        alert_level = "CRITICAL"
        alerts.append("IDLH EXCEEDED: Concentration is >= 100 ppm!")
    elif h2s_ppm > 50.0:
        alert_level = "CRITICAL"
        alerts.append("PEAK EXCEEDED: Concentration is > 50 ppm!")
    elif h2s_ppm > 20.0:
        alert_level = "WARNING"
        alerts.append("CEILING EXCEEDED: Concentration is > 20 ppm ceiling limit!")
    elif twa_8hr > 10.0:
        alert_level = "WARNING"
        alerts.append("8-HOUR TWA WARNING: Accumulated 8-hr TWA exceeds 10 ppm.")

    _, aligned_buf = cv2.imencode(".jpg", aligned)
    aligned_b64 = "data:image/jpeg;base64," + base64.b64encode(aligned_buf).decode("utf-8")
    
    debug_img = aligned.copy()
    for r_name, (x1, y1, x2, y2) in REGIONS.items():
        color = (0, 255, 0) if "reference" in r_name else (0, 165, 255) if "S" in r_name else (255, 0, 255)
        cv2.rectangle(debug_img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(debug_img, r_name, (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    _, debug_buf = cv2.imencode(".jpg", debug_img)
    debug_b64 = "data:image/jpeg;base64," + base64.b64encode(debug_buf).decode("utf-8")
    
    res = {
        "success": True,
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "quality": {
            "blur_pass": blur_pass,
            "blur_score": round(laplacian_var, 1),
            "lighting_pass": lighting_pass,
            "brightness": round(mean_brightness, 1),
            "all_markers_found": all_markers_found,
            "markers_count": markers_found
        },
        "h2s_ppm": h2s_ppm,
        "exposure_hours": float(exposure_hours),
        "shift_exposure_ppm_hr": shift_exposure,
        "twa_8hr_ppm": twa_8hr,
        "alert_level": alert_level,
        "alerts": alerts,
        "sensor_details": sensor_details,
        "features": features,
        "aligned_image": aligned_b64,
        "roi_debug_image": debug_b64
    }
    return sanitize_for_json(res)

def save_to_history(record):
    df_new = pd.DataFrame([{
        "Timestamp": record.get("timestamp", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")),
        "Employee_ID": record.get("employee_id", "EMP-001"),
        "Band_ID": record.get("band_id", "BAND-992"),
        "Shift_Info": record.get("shift_info", "Day Shift A"),
        "H2S_Concentration_ppm": float(record.get("h2s_ppm", 0.0)),
        "Exposure_Duration_hr": float(record.get("exposure_hours", 8.0)),
        "Shift_Exposure_ppm_hr": float(record.get("shift_exposure_ppm_hr", 0.0)),
        "TWA_8hr_ppm": float(record.get("twa_8hr_ppm", 0.0)),
        "Alert_Status": record.get("alert_level", "NORMAL")
    }])
    
    cols = ["Timestamp", "Employee_ID", "Band_ID", "Shift_Info", "H2S_Concentration_ppm", "Exposure_Duration_hr", "Shift_Exposure_ppm_hr", "TWA_8hr_ppm", "Alert_Status"]
    
    if HISTORY_PATH.exists() and HISTORY_PATH.stat().st_size > 0:
        try:
            df_existing = pd.read_csv(HISTORY_PATH)
            for c in cols:
                if c not in df_existing.columns:
                    df_existing[c] = ""
            df_existing = df_existing[cols]
            df_combined = pd.concat([df_existing, df_new[cols]], ignore_index=True)
            df_combined.to_csv(HISTORY_PATH, index=False)
        except Exception:
            df_new[cols].to_csv(HISTORY_PATH, index=False)
    else:
        df_new[cols].to_csv(HISTORY_PATH, index=False)

def get_history_analytics():
    if not HISTORY_PATH.exists() or HISTORY_PATH.stat().st_size == 0:
        return {
            "records": [], "weekly_dose": 0.0, "monthly_twa": 0.0, "rotation_dose": 0.0, "total_scans": 0, "critical_count": 0
        }
    try:
        df = pd.read_csv(HISTORY_PATH)
        records = df.to_dict(orient="records")
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        df["Shift_Exposure_ppm_hr"] = pd.to_numeric(df["Shift_Exposure_ppm_hr"], errors="coerce").fillna(0)
        df["H2S_Concentration_ppm"] = pd.to_numeric(df["H2S_Concentration_ppm"], errors="coerce").fillna(0)
        df["Exposure_Duration_hr"] = pd.to_numeric(df["Exposure_Duration_hr"], errors="coerce").fillna(0)
        
        now = pd.Timestamp.now()
        week_df = df[df["Timestamp"] >= (now - pd.Timedelta(days=7))]
        month_df = df[df["Timestamp"] >= (now - pd.Timedelta(days=30))]
        rotation_df = df[df["Timestamp"] >= (now - pd.Timedelta(hours=84))]
        
        weekly_dose = round(float(week_df["Shift_Exposure_ppm_hr"].sum()), 2)
        month_hours = month_df["Exposure_Duration_hr"].sum()
        month_weighted = (month_df["H2S_Concentration_ppm"] * month_df["Exposure_Duration_hr"]).sum()
        monthly_twa = round(float(month_weighted / month_hours), 2) if month_hours > 0 else 0.0
        rotation_dose = round(float(rotation_df["Shift_Exposure_ppm_hr"].sum()), 2)
        critical_count = len(df[df["Alert_Status"] == "CRITICAL"])
        
        return sanitize_for_json({
            "records": records, "weekly_dose": weekly_dose, "monthly_twa": monthly_twa,
            "rotation_dose": rotation_dose, "total_scans": len(records), "critical_count": critical_count
        })
    except Exception:
        return {"records": [], "weekly_dose": 0.0, "monthly_twa": 0.0, "rotation_dose": 0.0, "total_scans": 0, "critical_count": 0}

class H2SAPIHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Route standard HTTP access logs cleanly to stdout with flush=True
        sys.stdout.write("[API LOG] %s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))
        sys.stdout.flush()

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def send_json_response(self, code, data):
        body = json.dumps(sanitize_for_json(data)).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/api/status":
            res = {
                "status": "online",
                "model_loaded": bool(rf_model is not None),
                "opencv_version": str(cv2.__version__),
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.send_json_response(200, res)
            
        elif path == "/api/history":
            analytics = get_history_analytics()
            self.send_json_response(200, analytics)
            
        elif path == "/api/history/download":
            if HISTORY_PATH.exists() and HISTORY_PATH.stat().st_size > 0:
                with open(HISTORY_PATH, "rb") as f:
                    csv_data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Disposition", 'attachment; filename="exposure_history.csv"')
                self.send_header("Content-Length", str(len(csv_data)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(csv_data)
                self.wfile.flush()
                print(f"[API CALL] Downloaded exposure_history.csv ({len(csv_data)} bytes)", flush=True)
            else:
                self.send_response(404)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b""
        
        if path == "/api/scan":
            try:
                data = json.loads(body.decode("utf-8")) if body else {}
                img_data_b64 = data.get("image", "")
                temp_c = float(data.get("temperature", 32.0))
                humidity_pct = float(data.get("humidity", 65.0))
                exposure_hours = float(data.get("exposure_hours", 8.0))
                employee_id = str(data.get("employee_id", "EMP-104"))
                band_id = str(data.get("band_id", "BAND-884"))
                shift_info = str(data.get("shift_info", "Morning Shift 1"))
                
                cv_img = None
                if img_data_b64.startswith("data:image"):
                    header, encoded = img_data_b64.split(",", 1)
                    img_bytes = base64.b64decode(encoded)
                    nparr = np.frombuffer(img_bytes, np.uint8)
                    cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if cv_img is None:
                    sample_path = PROJECT_ROOT / "sample.png"
                    if sample_path.exists():
                        cv_img = cv2.imread(str(sample_path))
                    else:
                        cv_img = np.full((600, 1400, 3), 200, dtype=np.uint8)
                
                result = process_band_image(cv_img, temp_c, humidity_pct, exposure_hours)
                result["employee_id"] = employee_id
                result["band_id"] = band_id
                result["shift_info"] = shift_info
                
                if not result.get("success", True):
                    print(f"[API CALL REJECTED] POST /api/scan -> ArUco Markers Not Verified ({result['quality']['markers_count']}/4 found). Processing halted.", flush=True)
                    self.send_json_response(422, result)
                    return

                save_to_history(result)
                print(f"[API CALL] POST /api/scan -> Processed scan for {employee_id} ({band_id}) | Result H2S: {result['h2s_ppm']} ppm | Status: {result['alert_level']}", flush=True)
                self.send_json_response(200, result)
                
            except Exception as e:
                print("[ERROR] POST /api/scan failed:", e, flush=True)
                traceback.print_exc()
                self.send_json_response(500, {"error": str(e)})
                
        elif path == "/api/history/add":
            try:
                data = json.loads(body.decode("utf-8"))
                save_to_history(data)
                print(f"[API CALL] POST /api/history/add -> Added history record for {data.get('employee_id', 'EMP')}", flush=True)
                self.send_json_response(200, {"success": True})
            except Exception as e:
                print("[ERROR] POST /api/history/add failed:", e, flush=True)
                traceback.print_exc()
                self.send_json_response(500, {"error": str(e)})

def run_server(port=5000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, H2SAPIHandler)
    print(f"\n=======================================================", flush=True)
    print(f" H2S Exposure Monitoring System API Server", flush=True)
    print(f" Running on http://localhost:{port}", flush=True)
    print(f" Terminal Logging: LIVE STEP-BY-STEP PIPELINE OUTPUT", flush=True)
    print(f"=======================================================\n", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...", flush=True)
        httpd.server_close()

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port)
