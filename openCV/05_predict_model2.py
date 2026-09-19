import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT /
    "H2S_total_exposure_random_forest_datasetNew.joblib"
)

FEATURE_PATH = (
    PROJECT_ROOT /
    "output" /
    "features" /
    "extracted_features.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "output" / "prediction"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HISTORY_DIR = PROJECT_ROOT / "output" / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

PREDICTION_PATH = OUTPUT_DIR / "prediction_result.csv"

HISTORY_PATH = HISTORY_DIR / "exposure_history.csv"


# ============================================================
# MODEL FEATURE ORDER
# ============================================================

EXPECTED_FEATURES = [
    "S1_Hue",
    "S1_Saturation",
    "S1_Value",
    "S1_DeltaE",
    "S1_Gradient",

    "S2_Hue",
    "S2_Saturation",
    "S2_Value",
    "S2_DeltaE",
    "S2_Gradient",

    "S3_Hue",
    "S3_Saturation",
    "S3_Value",
    "S3_DeltaE",
    "S3_Gradient",

    "Temperature_C",
    "Humidity_Percent"
]


# ============================================================
# CURRENT-SHIFT CONFIGURATION
# ============================================================

TWA_REFERENCE_HOURS = 8.0

# These are configurable project reference values.
# Verify the applicable standard for your deployment location
# before treating them as regulatory limits.

CEILING_PPM = 20.0
PEAK_PPM = 50.0
PEAK_DURATION_MINUTES = 10.0
IDLH_PPM = 100.0

# Leave None unless a verified TWA limit is intentionally used.
TWA_LIMIT_PPM = None


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading model...")

if not MODEL_PATH.exists():
    print("\nERROR: Model file not found:")
    print(MODEL_PATH)
    raise SystemExit

try:
    loaded_object = joblib.load(MODEL_PATH)

    # Model may be saved directly or inside a dictionary
    if hasattr(loaded_object, "predict"):
        model = loaded_object

    elif isinstance(loaded_object, dict):

        print("Model file contains a dictionary.")

        # Try common keys used when saving the model
        possible_keys = [
            "model",
            "rf_model",
            "random_forest",
            "regressor",
            "estimator"
        ]

        model = None

        for key in possible_keys:

            if key in loaded_object:

                candidate = loaded_object[key]

                if hasattr(candidate, "predict"):
                    model = candidate
                    print(f"Random Forest found under key: '{key}'")
                    break

        if model is None:

            print("\nERROR: Could not find a prediction model")
            print("inside the joblib dictionary.")

            print("\nAvailable keys:")

            for key in loaded_object.keys():
                print(" -", key)

            raise SystemExit

    else:

        print(
            "\nERROR: Unsupported object stored in model file."
        )

        print(
            "Loaded object type:",
            type(loaded_object)
        )

        raise SystemExit

except Exception as e:

    print("\nERROR loading model:")
    print(e)
    raise SystemExit

print("Model loaded successfully.")


# ============================================================
# LOAD FEATURES
# ============================================================

if not FEATURE_PATH.exists():
    print("\nERROR: Feature file not found:")
    print(FEATURE_PATH)
    raise SystemExit

try:
    features_df = pd.read_csv(FEATURE_PATH)
except Exception as e:
    print("\nERROR reading feature file:")
    print(e)
    raise SystemExit


# ============================================================
# CHECK FEATURES
# ============================================================

missing_features = [
    feature
    for feature in EXPECTED_FEATURES
    if feature not in features_df.columns
]

if missing_features:

    print("\nERROR: Missing required features:")

    for feature in missing_features:
        print(" -", feature)

    raise SystemExit


# ============================================================
# PREPARE MODEL INPUT
# ============================================================

X = features_df[EXPECTED_FEATURES].copy()

# Use the latest row if multiple rows exist
X_latest = X.iloc[[-1]]


# ============================================================
# MODEL PREDICTION
# ============================================================

try:
    prediction = model.predict(X_latest)
except Exception as e:

    print("\nERROR during prediction:")
    print(e)

    raise SystemExit


h2s_ppm = float(prediction[0])

# Prevent tiny negative predictions due to numerical behavior
h2s_ppm = max(0.0, h2s_ppm)


# ============================================================
# DISPLAY PREDICTION
# ============================================================

print("\n----------------------------------------------")
print("H2S CONCENTRATION")
print("----------------------------------------------")

print(f"Predicted H2S : {h2s_ppm:.2f} ppm")


# ============================================================
# GET EXPOSURE INFORMATION
# ============================================================

print("\n----------------------------------------------")
print("EXPOSURE INFORMATION")
print("----------------------------------------------")

while True:

    try:

        exposure_hours = float(
            input("Enter worker exposure duration (hours): ")
        )

        if exposure_hours <= 0:
            print("Exposure duration must be greater than 0.")
            continue

        break

    except ValueError:

        print("Please enter a valid number.")


# ============================================================
# SHIFT EXPOSURE
# ============================================================

shift_exposure = h2s_ppm * exposure_hours


# ============================================================
# 8-HOUR TWA EQUIVALENT
# ============================================================

twa_8hr = shift_exposure / TWA_REFERENCE_HOURS


# ============================================================
# ALERT SYSTEM
# ============================================================

alerts = []

highest_alert_level = "NORMAL"


# ------------------------------------------------------------
# IDLH
# ------------------------------------------------------------

if h2s_ppm >= IDLH_PPM:

    alerts.append(
        f"H2S concentration {h2s_ppm:.2f} ppm "
        f"is at or above the {IDLH_PPM:.0f} ppm IDLH reference."
    )

    highest_alert_level = "CRITICAL"


# ------------------------------------------------------------
# CEILING
# ------------------------------------------------------------

if h2s_ppm > CEILING_PPM:

    alerts.append(
        f"H2S concentration {h2s_ppm:.2f} ppm "
        f"exceeds the {CEILING_PPM:.0f} ppm ceiling criterion."
    )

    if highest_alert_level != "CRITICAL":
        highest_alert_level = "WARNING"


# ------------------------------------------------------------
# PEAK
# ------------------------------------------------------------

if h2s_ppm > PEAK_PPM:

    alerts.append(
        f"H2S concentration {h2s_ppm:.2f} ppm "
        f"exceeds the {PEAK_PPM:.0f} ppm peak criterion."
    )

    highest_alert_level = "CRITICAL"


# ------------------------------------------------------------
# PEAK DURATION
# ------------------------------------------------------------

if (
    h2s_ppm > PEAK_PPM
    and exposure_hours * 60 > PEAK_DURATION_MINUTES
):

    alerts.append(
        f"Exposure above {PEAK_PPM:.0f} ppm "
        f"exceeded {PEAK_DURATION_MINUTES:.0f} minutes."
    )

    highest_alert_level = "CRITICAL"


# ------------------------------------------------------------
# OPTIONAL TWA
# ------------------------------------------------------------

if TWA_LIMIT_PPM is not None:

    if twa_8hr > TWA_LIMIT_PPM:

        alerts.append(
            f"8-hour TWA {twa_8hr:.2f} ppm "
            f"exceeds the configured TWA limit of "
            f"{TWA_LIMIT_PPM:.2f} ppm."
        )

        if highest_alert_level == "NORMAL":
            highest_alert_level = "WARNING"


# ============================================================
# DISPLAY EXPOSURE
# ============================================================

print("\n----------------------------------------------")
print("SHIFT EXPOSURE")
print("----------------------------------------------")

print(f"H2S concentration : {h2s_ppm:.2f} ppm")
print(f"Exposure duration : {exposure_hours:.2f} hr")
print(f"Shift exposure    : {shift_exposure:.2f} ppm.hr")
print(f"8-hour TWA        : {twa_8hr:.2f} ppm")


# ============================================================
# DISPLAY ALERTS
# ============================================================

print("\n----------------------------------------------")
print("CURRENT-SHIFT ALERTS")
print("----------------------------------------------")

if not alerts:

    print("\n[NORMAL]")
    print("No configured current-shift alert condition detected.")

else:

    for message in alerts:

        if "IDLH" in message:
            print("\n[CRITICAL] IDLH")

        elif "peak criterion" in message:
            print("\n[CRITICAL] PEAK")

        elif "ceiling criterion" in message:
            print("\n[WARNING] CEILING")

        elif "TWA" in message:
            print("\n[WARNING] TWA")

        else:
            print("\n[ALERT]")

        print(message)


# ============================================================
# TIMESTAMP
# ============================================================

timestamp = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)


# ============================================================
# SAVE CURRENT PREDICTION
# ============================================================

prediction_data = {

    "Timestamp": timestamp,

    "H2S_Concentration_ppm": round(
        h2s_ppm,
        4
    ),

    "Exposure_Duration_hr": round(
        exposure_hours,
        4
    ),

    "Shift_Exposure_ppm_hr": round(
        shift_exposure,
        4
    ),

    "TWA_8hr_ppm": round(
        twa_8hr,
        4
    ),

    "Alert_Level": highest_alert_level,

    "Alert_Messages": " | ".join(alerts)
}


prediction_df = pd.DataFrame(
    [prediction_data]
)

prediction_df.to_csv(
    PREDICTION_PATH,
    index=False
)


# ============================================================
# SAVE TO LONG-TERM HISTORY
# ============================================================

history_columns = [
    "Timestamp",
    "H2S_Concentration_ppm",
    "Exposure_Duration_hr",
    "Shift_Exposure_ppm_hr",
    "TWA_8hr_ppm",
    "Alert_Level",
    "Alert_Messages"
]


if HISTORY_PATH.exists():

    try:

        history_df = pd.read_csv(
            HISTORY_PATH
        )

    except Exception:

        history_df = pd.DataFrame(
            columns=history_columns
        )

else:

    history_df = pd.DataFrame(
        columns=history_columns
    )


# Make sure required columns exist
for column in history_columns:

    if column not in history_df.columns:
        history_df[column] = None


history_df = pd.concat(
    [
        history_df[history_columns],
        prediction_df[history_columns]
    ],
    ignore_index=True
)


history_df.to_csv(
    HISTORY_PATH,
    index=False
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print("\n==============================================")
print("              RESULT SAVED")
print("==============================================")

print("\nCurrent prediction:")
print(PREDICTION_PATH)

print("\nLong-term history:")
print(HISTORY_PATH)

print("\nCurrent alert level:")
print(highest_alert_level)

print("\n==============================================\n")