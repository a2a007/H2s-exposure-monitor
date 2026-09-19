import cv2
import numpy as np
import json
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

CALIBRATED_DIR = Path("output/calibrated")
FEATURE_DIR = Path("output/features")

FEATURE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# FRESH / UNEXPOSED BAND BASELINE
# MUST MATCH MODEL TRAINING
# ============================================================

BASELINE_HUE = 45.0
BASELINE_SATURATION = 50.0
BASELINE_VALUE = 90.0

# Prototype environmental values
# Later these can come directly from temperature/humidity sensors.
TEMPERATURE_C = 32.0
HUMIDITY_PERCENT = 65.0


# ============================================================
# HSV -> LAB
# ============================================================

def hsv_to_lab(hue, saturation, value):
    """
    Convert HSV values:
        Hue        = 0-360 degrees
        Saturation = 0-100 %
        Value      = 0-100 %

    to CIE Lab.
    """

    hsv = np.array(
        [[[
            hue / 2.0,
            saturation * 2.55,
            value * 2.55
        ]]],
        dtype=np.uint8
    )

    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    lab = cv2.cvtColor(
        bgr,
        cv2.COLOR_BGR2LAB
    )[0, 0].astype(np.float64)

    # OpenCV Lab conversion
    lab[0] = lab[0] * 100.0 / 255.0
    lab[1] -= 128.0
    lab[2] -= 128.0

    return lab


# ============================================================
# BASELINE LAB
# ============================================================

BASELINE_LAB = hsv_to_lab(
    BASELINE_HUE,
    BASELINE_SATURATION,
    BASELINE_VALUE
)


# ============================================================
# CIE76 DELTA E
# ============================================================

def calculate_delta_e(hue, saturation, value):

    current_lab = hsv_to_lab(
        float(hue),
        float(saturation),
        float(value)
    )

    delta_e = np.linalg.norm(
        current_lab - BASELINE_LAB
    )

    return float(delta_e)


# ============================================================
# COLOUR-CHANGE GRADIENT
#
# THIS MUST MATCH TRAINING EXACTLY
# ============================================================

def calculate_colour_gradient(hue, saturation, value):

    # -------------------------
    # Hue difference
    # -------------------------

    hue_difference = abs(
        float(hue) - BASELINE_HUE
    )

    # Circular hue distance
    hue_difference = min(
        hue_difference,
        360.0 - hue_difference
    )

    hue_change = hue_difference / 180.0

    # -------------------------
    # Saturation change
    # -------------------------

    saturation_change = (
        abs(
            float(saturation)
            - BASELINE_SATURATION
        ) / 100.0
    )

    # -------------------------
    # Value change
    # -------------------------

    value_change = (
        abs(
            float(value)
            - BASELINE_VALUE
        ) / 100.0
    )

    # -------------------------
    # Combined colour gradient
    # -------------------------

    gradient = np.sqrt(
        hue_change ** 2
        + saturation_change ** 2
        + value_change ** 2
    )

    return float(gradient)


# ============================================================
# EXTRACT MEDIAN HSV FROM ROI
# ============================================================

def extract_hsv(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        raise FileNotFoundError(
            f"Could not read: {image_path}"
        )

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    # OpenCV HSV:
    # H = 0-179
    # S = 0-255
    # V = 0-255

    h = np.median(hsv[:, :, 0]) * 2.0
    s = np.median(hsv[:, :, 1]) * 100.0 / 255.0
    v = np.median(hsv[:, :, 2]) * 100.0 / 255.0

    return float(h), float(s), float(v)


# ============================================================
# PROCESS ONE SENSOR
# ============================================================

def process_sensor(sensor_name):

    image_path = (
        CALIBRATED_DIR
        / f"{sensor_name}_calibrated.png"
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Missing calibrated image: {image_path}"
        )

    hue, saturation, value = extract_hsv(
        image_path
    )

    delta_e = calculate_delta_e(
        hue,
        saturation,
        value
    )

    gradient = calculate_colour_gradient(
        hue,
        saturation,
        value
    )

    print(f"\n{sensor_name}")

    print(
        f"  Hue        = {hue:.4f}°"
    )

    print(
        f"  Saturation = {saturation:.4f}%"
    )

    print(
        f"  Value      = {value:.4f}%"
    )

    print(
        f"  DeltaE     = {delta_e:.4f}"
    )

    print(
        f"  Gradient   = {gradient:.4f}"
    )

    return {
        "Hue": hue,
        "Saturation": saturation,
        "Value": value,
        "DeltaE": delta_e,
        "Gradient": gradient
    }


# ============================================================
# MAIN
# ============================================================

print("=" * 60)
print("STEP 4 - FEATURE EXTRACTION")
print("=" * 60)

print("\nFresh / Unexposed Band Baseline")
print(
    f"Hue        = {BASELINE_HUE:.2f}°"
)
print(
    f"Saturation = {BASELINE_SATURATION:.2f}%"
)
print(
    f"Value      = {BASELINE_VALUE:.2f}%"
)

print("\nBaseline CIE Lab")

print(
    f"L* = {BASELINE_LAB[0]:.4f}"
)

print(
    f"a* = {BASELINE_LAB[1]:.4f}"
)

print(
    f"b* = {BASELINE_LAB[2]:.4f}"
)


# ============================================================
# S1 / S2 / S3
# ============================================================

s1 = process_sensor("S1")
s2 = process_sensor("S2")
s3 = process_sensor("S3")


# ============================================================
# CREATE EXACT 17 MODEL FEATURES
# ============================================================

features = {

    # -------------------------
    # S1
    # -------------------------

    "S1_Hue":
        s1["Hue"],

    "S1_Saturation":
        s1["Saturation"],

    "S1_Value":
        s1["Value"],

    "S1_DeltaE":
        s1["DeltaE"],

    "S1_Gradient":
        s1["Gradient"],


    # -------------------------
    # S2
    # -------------------------

    "S2_Hue":
        s2["Hue"],

    "S2_Saturation":
        s2["Saturation"],

    "S2_Value":
        s2["Value"],

    "S2_DeltaE":
        s2["DeltaE"],

    "S2_Gradient":
        s2["Gradient"],


    # -------------------------
    # S3
    # -------------------------

    "S3_Hue":
        s3["Hue"],

    "S3_Saturation":
        s3["Saturation"],

    "S3_Value":
        s3["Value"],

    "S3_DeltaE":
        s3["DeltaE"],

    "S3_Gradient":
        s3["Gradient"],


    # -------------------------
    # Environment
    # -------------------------

    "Temperature_C":
        TEMPERATURE_C,

    "Humidity_Percent":
        HUMIDITY_PERCENT
}


# ============================================================
# SAVE CSV
# ============================================================

import pandas as pd

feature_df = pd.DataFrame(
    [features]
)

csv_path = (
    FEATURE_DIR
    / "extracted_features.csv"
)

feature_df.to_csv(
    csv_path,
    index=False
)


# ============================================================
# SAVE JSON
# ============================================================

json_path = (
    FEATURE_DIR
    / "extracted_features.json"
)

with open(
    json_path,
    "w"
) as f:

    json.dump(
        {
            "baseline": {
                "Hue": BASELINE_HUE,
                "Saturation":
                    BASELINE_SATURATION,
                "Value":
                    BASELINE_VALUE,
                "Lab":
                    BASELINE_LAB.tolist()
            },

            "features": features
        },
        f,
        indent=4
    )


# ============================================================
# PRINT FINAL FEATURE ORDER
# ============================================================

print("\n" + "=" * 60)
print("FINAL 17 FEATURES")
print("=" * 60)

for i, name in enumerate(features.keys(), 1):

    print(
        f"{i:02d}. {name} = "
        f"{features[name]:.6f}"
    )


print("\nSaved:")
print(csv_path)
print(json_path)

print("\nSTEP 4 COMPLETE")