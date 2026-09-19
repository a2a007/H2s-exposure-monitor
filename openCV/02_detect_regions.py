import cv2
import os
import sys


# ============================================================
# H2S BAND - REGION DETECTOR
# ============================================================
#
# Input:
#     output/aligned/aligned_band.jpg
#
# Expected aligned image:
#     1200 x 300
#
# IMPORTANT:
# These coordinates belong to the ALIGNED image.
# Do NOT use these coordinates on the original phone image.
#
# Pipeline:
#
# Original photo
#       ↓
# ArUco alignment
#       ↓
# 1200 x 300 image
#       ↓
# Region extraction
#
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

EXPECTED_WIDTH = 1200
EXPECTED_HEIGHT = 300

DEFAULT_INPUT = "output/aligned/aligned_band.jpg"

DEBUG_OUTPUT = "output/debug/regions_detected.jpg"
REGION_OUTPUT_DIR = "output/regions"


# ============================================================
# REGION COORDINATES
# ============================================================
#
# Format:
#
# (x1, y1, x2, y2)
#
# All coordinates are for the 1200 x 300 ALIGNED image.
#
# ============================================================

REGIONS = {

    # --------------------------------------------------------
    # PRINTED REFERENCE COLOUR SCALE
    # --------------------------------------------------------
    #
    # These ROIs contain only the colour patches.
    # Text underneath is intentionally excluded.
    #

    "reference_purple": (
        145, 44,
        258, 100
    ),

    "reference_amber": (
        291, 44,
        404, 100
    ),

    "reference_yellow": (
        440, 44,
        553, 100
    ),

    "reference_white": (
        590, 44,
        703, 100
    ),

    "reference_gray": (
        738, 44,
        851, 100
    ),


    # --------------------------------------------------------
    # EXPIRY INDICATOR
    # --------------------------------------------------------
    #
    # This ROI contains the expiry colour indicator.
    #
    "expiry": (
        888, 10,
        1077, 142
    ),


    # --------------------------------------------------------
    # Cu-PAN SENSING SEGMENTS
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # Each segment is ONE COMPLETE REGION.
    #
    # S1 = complete open membrane region
    # S2 = complete 0.22 um PTFE region
    # S3 = complete 0.10 um PTFE region
    #
    # We intentionally do NOT split them into upper/lower.
    #

    "S1": (
        147, 189,
        365, 299
    ),

    "S2": (
        374, 189,
        598, 299
    ),

    "S3": (
        610, 189,
        836, 299
    ),


    # --------------------------------------------------------
    # BAND IDENTIFICATION PANEL
    # --------------------------------------------------------
    #
    # Contains:
    #
    # BAND ID
    # MFG
    # EXP
    #
    # This is kept completely outside the Cu-PAN sensing strip.
    #

    "band_id": (
        865, 161,
        1077, 299
    )
}


# ============================================================
# REGION GROUPS
# ============================================================

REFERENCE_REGIONS = [
    "reference_purple",
    "reference_amber",
    "reference_yellow",
    "reference_white",
    "reference_gray"
]

SENSING_REGIONS = [
    "S1",
    "S2",
    "S3"
]

OTHER_REGIONS = [
    "expiry",
    "band_id"
]


# ============================================================
# CREATE DIRECTORIES
# ============================================================

def create_directories():

    os.makedirs(
        REGION_OUTPUT_DIR,
        exist_ok=True
    )

    os.makedirs(
        os.path.dirname(DEBUG_OUTPUT),
        exist_ok=True
    )


# ============================================================
# CHECK REGION
# ============================================================

def validate_region(
    name,
    coordinates,
    width,
    height
):

    x1, y1, x2, y2 = coordinates

    if x1 < 0 or y1 < 0:
        return False

    if x2 > width or y2 > height:
        return False

    if x2 <= x1 or y2 <= y1:
        return False

    return True


# ============================================================
# DRAW REGION
# ============================================================

def draw_region(
    image,
    name,
    coordinates,
    color=(0, 255, 0),
    thickness=2
):

    x1, y1, x2, y2 = coordinates

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        color,
        thickness
    )

    # Label position
    label_y = max(
        15,
        y1 - 6
    )

    cv2.putText(
        image,
        name,
        (x1, label_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.40,
        color,
        1,
        cv2.LINE_AA
    )


# ============================================================
# CROP REGION
# ============================================================

def crop_region(
    image,
    coordinates
):

    x1, y1, x2, y2 = coordinates

    return image[
        y1:y2,
        x1:x2
    ]


# ============================================================
# PRINT REGION INFORMATION
# ============================================================

def print_region(
    name,
    coordinates
):

    x1, y1, x2, y2 = coordinates

    width = x2 - x1
    height = y2 - y1

    print(
        f"  {name:<20} "
        f"({x1:>3}, {y1:>3}) -> "
        f"({x2:>3}, {y2:>3}) "
        f"[{width} x {height}]"
    )


# ============================================================
# MAIN DETECTOR
# ============================================================

def detect_regions(
    image_path
):

    print(
        "=============================================="
    )

    print(
        "        H2S BAND - REGION DETECTION"
    )

    print(
        "=============================================="
    )


    # --------------------------------------------------------
    # Load image
    # --------------------------------------------------------

    image = cv2.imread(
        image_path
    )

    if image is None:

        print()
        print(
            "ERROR: Could not read image:"
        )

        print(
            image_path
        )

        return False


    height, width = image.shape[:2]


    print()
    print(
        f"Input image size: "
        f"{width} × {height}"
    )


    # --------------------------------------------------------
    # Verify aligned image size
    # --------------------------------------------------------

    if (
        width != EXPECTED_WIDTH
        or
        height != EXPECTED_HEIGHT
    ):

        print()
        print(
            "ERROR: Incorrect aligned image size."
        )

        print(
            f"Expected: "
            f"{EXPECTED_WIDTH} × {EXPECTED_HEIGHT}"
        )

        print(
            f"Received: "
            f"{width} × {height}"
        )

        print()
        print(
            "Run 01_align_band.py first."
        )

        return False


    # --------------------------------------------------------
    # Create directories
    # --------------------------------------------------------

    create_directories()


    # --------------------------------------------------------
    # Create debug copy
    # --------------------------------------------------------

    debug_image = image.copy()


    # --------------------------------------------------------
    # Validate all regions
    # --------------------------------------------------------

    print()
    print(
        "Checking region coordinates..."
    )

    for name, coordinates in REGIONS.items():

        valid = validate_region(
            name,
            coordinates,
            width,
            height
        )

        if not valid:

            print()
            print(
                f"ERROR: Invalid region: {name}"
            )

            print(
                "Coordinates:",
                coordinates
            )

            return False


    print(
        "All region coordinates valid."
    )


    # --------------------------------------------------------
    # Draw and save regions
    # --------------------------------------------------------

    print()
    print(
        "Detected regions:"
    )


    for name, coordinates in REGIONS.items():

        print_region(
            name,
            coordinates
        )


        # ----------------------------------------------------
        # Choose debug colour
        # ----------------------------------------------------

        if name in SENSING_REGIONS:

            # Cyan for sensing regions
            debug_color = (
                255,
                255,
                0
            )

        elif name in REFERENCE_REGIONS:

            # Green for reference patches
            debug_color = (
                0,
                255,
                0
            )

        else:

            # Blue for metadata regions
            debug_color = (
                255,
                150,
                0
            )


        # ----------------------------------------------------
        # Draw rectangle
        # ----------------------------------------------------

        draw_region(
            debug_image,
            name,
            coordinates,
            debug_color,
            2
        )


        # ----------------------------------------------------
        # Crop
        # ----------------------------------------------------

        crop = crop_region(
            image,
            coordinates
        )


        # ----------------------------------------------------
        # Save crop
        # ----------------------------------------------------

        output_path = os.path.join(
            REGION_OUTPUT_DIR,
            name + ".png"
        )

        cv2.imwrite(
            output_path,
            crop
        )


    # --------------------------------------------------------
    # Save debug image
    # --------------------------------------------------------

    cv2.imwrite(
        DEBUG_OUTPUT,
        debug_image
    )


    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print(
        "=============================================="
    )

    print(
        "REGION DETECTION SUCCESS"
    )

    print(
        "=============================================="
    )

    print()
    print(
        "Debug image:"
    )

    print(
        f"  {DEBUG_OUTPUT}"
    )

    print()
    print(
        "Region crops:"
    )

    for name in REGIONS:

        print(
            f"  {name}: "
            f"{REGION_OUTPUT_DIR}/{name}.png"
        )


    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    cv2.imshow(
        "H2S Region Detection",
        debug_image
    )

    cv2.waitKey(0)

    cv2.destroyAllWindows()


    return True


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) >= 2:

        image_path = sys.argv[1]

    else:

        image_path = DEFAULT_INPUT


    success = detect_regions(
        image_path
    )


    if not success:

        sys.exit(1)