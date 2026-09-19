import cv2
import sys
import os


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print("python opencv/00_test_aruco.py <image>")
        return

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print("ERROR: Image not found:", image_path)
        return

    image = cv2.imread(image_path)

    if image is None:
        print("ERROR: Could not read image.")
        return

    print("==============================================")
    print("          ARUCO DETECTION TEST")
    print("==============================================")

    print(
        f"Image size: "
        f"{image.shape[1]} × {image.shape[0]}"
    )

    # --------------------------------------------------
    # Convert to grayscale
    # --------------------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------------------
    # ArUco dictionary
    # --------------------------------------------------

    aruco_dict = cv2.aruco.getPredefinedDictionary(
        cv2.aruco.DICT_4X4_50
    )

    parameters = cv2.aruco.DetectorParameters()

    parameters.cornerRefinementMethod = (
        cv2.aruco.CORNER_REFINE_SUBPIX
    )

    detector = cv2.aruco.ArucoDetector(
        aruco_dict,
        parameters
    )

    # --------------------------------------------------
    # Detect
    # --------------------------------------------------

    corners, ids, rejected = detector.detectMarkers(
        gray
    )

    print("\nDetected markers:")

    if ids is None:

        print("  NONE")

        print(
            "\nRejected candidates:",
            len(rejected)
        )

    else:

        ids = ids.flatten()

        print(
            f"  Number detected: {len(ids)}"
        )

        print(
            "  IDs:",
            ids.tolist()
        )

        for i, marker_id in enumerate(ids):

            pts = corners[i][0]

            center_x = pts[:, 0].mean()
            center_y = pts[:, 1].mean()

            print(
                f"\n  Marker ID {marker_id}"
            )

            print(
                f"  Center: "
                f"({center_x:.1f}, {center_y:.1f})"
            )

            print(
                "  Corners:"
            )

            for j, p in enumerate(pts):

                print(
                    f"    {j}: "
                    f"({p[0]:.1f}, {p[1]:.1f})"
                )

    # --------------------------------------------------
    # Draw detection
    # --------------------------------------------------

    debug = image.copy()

    if ids is not None:

        cv2.aruco.drawDetectedMarkers(
            debug,
            corners,
            ids
        )

    cv2.imwrite(
        "aruco_test_result.jpg",
        debug
    )

    print(
        "\nSaved:"
    )

    print(
        "  aruco_test_result.jpg"
    )

    cv2.imshow(
        "ArUco Detection Test",
        debug
    )

    print(
        "\nPress any key to close."
    )

    cv2.waitKey(0)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()