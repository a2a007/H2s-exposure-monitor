import cv2
import numpy as np
import sys
import os


# ============================================================
# CONFIGURATION
# ============================================================

# Standardized measurement-panel size
#
# IMPORTANT:
# This is intentionally wide because the real H2S band is
# approximately a wide rectangular measurement panel.
#
OUTPUT_WIDTH = 1200
OUTPUT_HEIGHT = 300

ARUCO_DICT = cv2.aruco.DICT_4X4_50

REQUIRED_IDS = [0, 1, 2, 3]


# ============================================================
# DESTINATION MARKER POSITIONS
# ============================================================
#
# Standardized output:
#
# ID 0                                      ID 1
#   ●----------------------------------------●
#   |                                        |
#   |            H2S BAND PANEL              |
#   |                                        |
#   ●----------------------------------------●
# ID 3                                      ID 2
#
# Marker centers are kept away from the extreme image edges
# so the marker itself remains visible in the aligned image.
# ============================================================

DESTINATION_POINTS = np.array([
    [55, 45],       # ID 0 - Top Left
    [1145, 45],     # ID 1 - Top Right
    [1145, 255],    # ID 2 - Bottom Right
    [55, 255]       # ID 3 - Bottom Left
], dtype=np.float32)


# ============================================================
# ARUCO DETECTOR
# ============================================================

def detect_aruco(image):

    dictionary = cv2.aruco.getPredefinedDictionary(
        ARUCO_DICT
    )

    parameters = cv2.aruco.DetectorParameters()

    parameters.cornerRefinementMethod = (
        cv2.aruco.CORNER_REFINE_SUBPIX
    )

    detector = cv2.aruco.ArucoDetector(
        dictionary,
        parameters
    )

    corners, ids, rejected = detector.detectMarkers(
        image
    )

    marker_centers = {}

    if ids is None:
        return marker_centers

    for marker_corner, marker_id in zip(
        corners,
        ids.flatten()
    ):

        marker_id = int(marker_id)

        if marker_id not in REQUIRED_IDS:
            continue

        points = marker_corner[0]

        center_x = np.mean(points[:, 0])
        center_y = np.mean(points[:, 1])

        marker_centers[marker_id] = [
            float(center_x),
            float(center_y)
        ]

    return marker_centers


# ============================================================
# CALCULATE PERSPECTIVE TRANSFORMATION
# ============================================================

def calculate_transform(marker_centers):

    source_points = np.array([
        marker_centers[0],
        marker_centers[1],
        marker_centers[2],
        marker_centers[3]
    ], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(
        source_points,
        DESTINATION_POINTS
    )

    return matrix


# ============================================================
# ALIGN BAND
# ============================================================

def align_band(image):

    marker_centers = detect_aruco(image)

    # --------------------------------------------------------
    # Verify all four markers
    # --------------------------------------------------------

    missing = [
        marker_id
        for marker_id in REQUIRED_IDS
        if marker_id not in marker_centers
    ]

    if missing:

        print(
            "\nALIGNMENT FAILED"
        )

        print(
            "Missing marker IDs:",
            missing
        )

        return None, marker_centers


    # --------------------------------------------------------
    # Source points
    # --------------------------------------------------------

    source_points = np.array([
        marker_centers[0],
        marker_centers[1],
        marker_centers[2],
        marker_centers[3]
    ], dtype=np.float32)


    # --------------------------------------------------------
    # Perspective matrix
    # --------------------------------------------------------

    matrix = cv2.getPerspectiveTransform(
        source_points,
        DESTINATION_POINTS
    )


    # --------------------------------------------------------
    # Warp
    # --------------------------------------------------------

    aligned = cv2.warpPerspective(
        image,
        matrix,
        (
            OUTPUT_WIDTH,
            OUTPUT_HEIGHT
        )
    )

    return aligned, marker_centers


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) < 2:

        print(
            "\nUsage:"
        )

        print(
            "python opencv/01_align_band.py image.jpg"
        )

        return


    input_path = sys.argv[1]


    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    image = cv2.imread(
        input_path
    )

    if image is None:

        print(
            "\nERROR: Cannot open image:"
        )

        print(
            input_path
        )

        return


    height, width = image.shape[:2]


    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    print(
        "=============================================="
    )

    print(
        "       H2S BAND - OPENCV ALIGNMENT"
    )

    print(
        "=============================================="
    )

    print(
        f"Input image size: "
        f"{width} × {height}"
    )


    # --------------------------------------------------------
    # Detect markers
    # --------------------------------------------------------

    marker_centers = detect_aruco(
        image
    )


    print(
        "\nDetected ArUco markers:"
    )


    for marker_id in sorted(marker_centers):

        x, y = marker_centers[marker_id]

        print(
            f"  ID {marker_id}: "
            f"center = ({x:.1f}, {y:.1f})"
        )


    # --------------------------------------------------------
    # Check markers
    # --------------------------------------------------------

    missing = [
        marker_id
        for marker_id in REQUIRED_IDS
        if marker_id not in marker_centers
    ]


    if missing:

        print(
            "\nALIGNMENT FAILED"
        )

        print(
            "Missing marker IDs:",
            missing
        )

        return


    # --------------------------------------------------------
    # Ordered points
    # --------------------------------------------------------

    print(
        "\nOrdered marker centers:"
    )

    print(
        f"Top-left     : "
        f"{np.array(marker_centers[0])}"
    )

    print(
        f"Top-right    : "
        f"{np.array(marker_centers[1])}"
    )

    print(
        f"Bottom-right : "
        f"{np.array(marker_centers[2])}"
    )

    print(
        f"Bottom-left  : "
        f"{np.array(marker_centers[3])}"
    )


    # --------------------------------------------------------
    # Perspective transformation
    # --------------------------------------------------------

    source_points = np.array([
        marker_centers[0],
        marker_centers[1],
        marker_centers[2],
        marker_centers[3]
    ], dtype=np.float32)


    matrix = cv2.getPerspectiveTransform(
        source_points,
        DESTINATION_POINTS
    )


    # --------------------------------------------------------
    # Warp
    # --------------------------------------------------------

    aligned = cv2.warpPerspective(
        image,
        matrix,
        (
            OUTPUT_WIDTH,
            OUTPUT_HEIGHT
        )
    )


    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    output_directory = (
        "output/aligned"
    )

    os.makedirs(
        output_directory,
        exist_ok=True
    )


    # --------------------------------------------------------
    # Save clean image
    # --------------------------------------------------------

    output_path = os.path.join(
        output_directory,
        "aligned_band.jpg"
    )


    cv2.imwrite(
        output_path,
        aligned
    )


    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    print(
        "\n=============================================="
    )

    print(
        "SUCCESS"
    )

    print(
        "=============================================="
    )

    print(
        f"Output image size: "
        f"{OUTPUT_WIDTH} × {OUTPUT_HEIGHT}"
    )

    print(
        f"Saved: {output_path}"
    )


    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    cv2.imshow(
        "Aligned H2S Band",
        aligned
    )

    cv2.waitKey(0)

    cv2.destroyAllWindows()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()