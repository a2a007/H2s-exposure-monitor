import cv2
import numpy as np
import os
import json
import sys


# ============================================================
# H2S BAND - REFERENCE COLOUR CALIBRATION
# ============================================================
#
# INPUT:
#
# output/regions/reference_purple.png
# output/regions/reference_amber.png
# output/regions/reference_yellow.png
# output/regions/reference_white.png
# output/regions/reference_gray.png
#
# AND:
#
# output/regions/S1.png
# output/regions/S2.png
# output/regions/S3.png
#
#
# PURPOSE:
#
# 1. Measure the five printed reference colours.
# 2. Compare them with their expected colours.
# 3. Calculate a colour correction transformation.
# 4. Apply the transformation to S1, S2 and S3.
# 5. Save calibrated sensing regions.
#
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

REGION_DIR = "output/regions"

OUTPUT_DIR = "output/calibrated"

CALIBRATION_FILE = (
    "output/calibrated/"
    "colour_calibration.json"
)


# ============================================================
# REFERENCE COLOURS
# ============================================================
#
# IMPORTANT:
#
# These values correspond to the CURRENT SYNTHETIC TEST BAND.
#
# When the real Cu-PAN band is manufactured, these reference
# values should be replaced by the actual target/reference
# colours selected for the printed calibration patches.
#
# OpenCV uses BGR order.
#
# ============================================================

TARGET_COLORS_BGR = {

    "reference_purple": np.array(
        [105, 20, 115],
        dtype=np.float64
    ),

    "reference_amber": np.array(
        [60, 90, 210],
        dtype=np.float64
    ),

    "reference_yellow": np.array(
        [20, 210, 245],
        dtype=np.float64
    ),

    "reference_white": np.array(
        [245, 245, 245],
        dtype=np.float64
    ),

    "reference_gray": np.array(
        [125, 125, 125],
        dtype=np.float64
    )
}


REFERENCE_NAMES = [
    "reference_purple",
    "reference_amber",
    "reference_yellow",
    "reference_white",
    "reference_gray"
]


SENSOR_NAMES = [
    "S1",
    "S2",
    "S3"
]


# ============================================================
# LOAD IMAGE
# ============================================================

def load_image(path):

    image = cv2.imread(path)

    if image is None:

        raise RuntimeError(
            f"Could not read image: {path}"
        )

    return image


# ============================================================
# CENTRAL CROP
# ============================================================
#
# Avoid borders of the colour patch.
#
# This is important because borders may contain:
#
# - black outlines
# - printing edges
# - anti-aliasing
# - text
#
# We use only the central 70% of the crop.
#
# ============================================================

def central_crop(
    image,
    percentage=0.70
):

    h, w = image.shape[:2]

    new_w = int(
        w * percentage
    )

    new_h = int(
        h * percentage
    )

    x1 = (w - new_w) // 2
    y1 = (h - new_h) // 2

    x2 = x1 + new_w
    y2 = y1 + new_h

    return image[
        y1:y2,
        x1:x2
    ]


# ============================================================
# MEASURE COLOUR
# ============================================================

def measure_colour(
    image
):

    sample = central_crop(
        image,
        0.70
    )

    pixels = sample.reshape(
        -1,
        3
    ).astype(
        np.float64
    )

    # Median is more robust against small noise
    # than a simple mean.
    median_bgr = np.median(
        pixels,
        axis=0
    )

    mean_bgr = np.mean(
        pixels,
        axis=0
    )

    return mean_bgr, median_bgr


# ============================================================
# LOAD REFERENCE COLOURS
# ============================================================

def measure_reference_colours():

    measured = {}

    print()
    print(
        "REFERENCE COLOUR MEASUREMENTS"
    )

    print(
        "--------------------------------------------"
    )

    for name in REFERENCE_NAMES:

        path = os.path.join(
            REGION_DIR,
            name + ".png"
        )

        image = load_image(
            path
        )

        mean_bgr, median_bgr = (
            measure_colour(image)
        )

        measured[name] = (
            median_bgr
        )

        target = TARGET_COLORS_BGR[
            name
        ]

        print()
        print(name)

        print(
            f"  Camera Median BGR : "
            f"{median_bgr}"
        )

        print(
            f"  Target BGR        : "
            f"{target}"
        )

    return measured


# ============================================================
# CALCULATE COLOUR CORRECTION MATRIX
# ============================================================
#
# We use an affine colour transformation:
#
# Corrected = Camera × Matrix + Offset
#
# In matrix form:
#
# [B G R 1] × M
#
# This allows both:
#
# - colour scaling
# - colour offset
#
# ============================================================

def calculate_calibration(
    measured
):

    camera_values = []
    target_values = []

    for name in REFERENCE_NAMES:

        camera = measured[name]

        target = TARGET_COLORS_BGR[name]

        camera_values.append(
            camera
        )

        target_values.append(
            target
        )

    camera_values = np.array(
        camera_values,
        dtype=np.float64
    )

    target_values = np.array(
        target_values,
        dtype=np.float64
    )

    # Add bias/intercept term.
    #
    # [B G R 1]
    #
    X = np.hstack(
        [
            camera_values,
            np.ones(
                (camera_values.shape[0], 1)
            )
        ]
    )

    # Least-squares solution
    #
    # X × M = Target
    #
    matrix, residuals, rank, singular_values = (
        np.linalg.lstsq(
            X,
            target_values,
            rcond=None
        )
    )

    return matrix


# ============================================================
# APPLY CALIBRATION
# ============================================================

def apply_calibration(
    image,
    matrix
):

    h, w = image.shape[:2]

    pixels = image.reshape(
        -1,
        3
    ).astype(
        np.float64
    )

    # Add bias term
    X = np.hstack(
        [
            pixels,
            np.ones(
                (pixels.shape[0], 1)
            )
        ]
    )

    corrected = X @ matrix

    corrected = np.clip(
        corrected,
        0,
        255
    )

    corrected = corrected.astype(
        np.uint8
    )

    corrected = corrected.reshape(
        h,
        w,
        3
    )

    return corrected


# ============================================================
# CALCULATE CALIBRATION ERROR
# ============================================================

def calculate_errors(
    measured,
    matrix
):

    print()
    print(
        "CALIBRATION ACCURACY"
    )

    print(
        "--------------------------------------------"
    )

    errors = {}

    for name in REFERENCE_NAMES:

        camera = measured[name]

        target = TARGET_COLORS_BGR[
            name
        ]

        X = np.array(
            [
                camera[0],
                camera[1],
                camera[2],
                1.0
            ],
            dtype=np.float64
        )

        predicted = X @ matrix

        predicted = np.clip(
            predicted,
            0,
            255
        )

        error = np.linalg.norm(
            predicted - target
        )

        errors[name] = float(
            error
        )

        print(
            f"{name:<20} "
            f"Error: {error:.3f}"
        )

    return errors


# ============================================================
# SAVE CALIBRATION
# ============================================================

def save_calibration(
    matrix,
    errors
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    data = {

        "method":
            "5-point affine BGR colour calibration",

        "reference_order":
            REFERENCE_NAMES,

        "target_colors_BGR": {

            name:
                TARGET_COLORS_BGR[
                    name
                ].tolist()

            for name in REFERENCE_NAMES
        },

        "calibration_matrix":
            matrix.tolist(),

        "reference_errors":
            errors
    }

    with open(
        CALIBRATION_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

    print()
    print(
        "Calibration saved:"
    )

    print(
        f"  {CALIBRATION_FILE}"
    )


# ============================================================
# CALIBRATE SENSOR REGIONS
# ============================================================

def calibrate_sensor_regions(
    matrix
):

    print()
    print(
        "CALIBRATING H2S SENSOR REGIONS"
    )

    print(
        "--------------------------------------------"
    )

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    calibrated_regions = {}

    for name in SENSOR_NAMES:

        input_path = os.path.join(
            REGION_DIR,
            name + ".png"
        )

        image = load_image(
            input_path
        )

        calibrated = apply_calibration(
            image,
            matrix
        )

        output_path = os.path.join(
            OUTPUT_DIR,
            name + "_calibrated.png"
        )

        cv2.imwrite(
            output_path,
            calibrated
        )

        calibrated_regions[name] = (
            output_path
        )

        print(
            f"{name} -> "
            f"{output_path}"
        )

    return calibrated_regions


# ============================================================
# CREATE CALIBRATED FULL IMAGE
# ============================================================
#
# This is only useful for visual debugging.
#
# The ML pipeline will use the individual S1/S2/S3 crops.
#
# ============================================================

def create_calibrated_preview(
    matrix
):

    aligned_path = (
        "output/aligned/"
        "aligned_band.jpg"
    )

    if not os.path.exists(
        aligned_path
    ):

        return

    image = load_image(
        aligned_path
    )

    calibrated = apply_calibration(
        image,
        matrix
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        "calibrated_band_preview.jpg"
    )

    cv2.imwrite(
        output_path,
        calibrated
    )

    print()
    print(
        "Calibrated preview:"
    )

    print(
        f"  {output_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=============================================="
    )

    print(
        "      H2S BAND - REFERENCE CALIBRATION"
    )

    print(
        "=============================================="
    )


    # --------------------------------------------------------
    # Check reference files
    # --------------------------------------------------------

    print()
    print(
        "Checking reference regions..."
    )

    for name in REFERENCE_NAMES:

        path = os.path.join(
            REGION_DIR,
            name + ".png"
        )

        if not os.path.exists(path):

            print()
            print(
                "ERROR: Missing reference region:"
            )

            print(
                path
            )

            print()
            print(
                "Run 02_detect_regions.py first."
            )

            return


    # --------------------------------------------------------
    # Measure references
    # --------------------------------------------------------

    measured = (
        measure_reference_colours()
    )


    # --------------------------------------------------------
    # Calculate calibration
    # --------------------------------------------------------

    print()
    print(
        "Calculating colour correction..."
    )

    matrix = calculate_calibration(
        measured
    )


    # --------------------------------------------------------
    # Print matrix
    # --------------------------------------------------------

    print()
    print(
        "Calibration matrix:"
    )

    print(
        matrix
    )


    # --------------------------------------------------------
    # Calculate errors
    # --------------------------------------------------------

    errors = calculate_errors(
        measured,
        matrix
    )


    # --------------------------------------------------------
    # Save calibration
    # --------------------------------------------------------

    save_calibration(
        matrix,
        errors
    )


    # --------------------------------------------------------
    # Calibrate S1/S2/S3
    # --------------------------------------------------------

    calibrate_sensor_regions(
        matrix
    )


    # --------------------------------------------------------
    # Calibrated full preview
    # --------------------------------------------------------

    create_calibrated_preview(
        matrix
    )


    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print()
    print(
        "=============================================="
    )

    print(
        "REFERENCE CALIBRATION COMPLETE"
    )

    print(
        "=============================================="
    )

    print()
    print(
        "Next step:"
    )

    print(
        "Extract colour features from:"
    )

    print(
        "  S1_calibrated.png"
    )

    print(
        "  S2_calibrated.png"
    )

    print(
        "  S3_calibrated.png"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()