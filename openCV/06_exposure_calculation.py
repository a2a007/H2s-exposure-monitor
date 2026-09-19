import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "H2S_total_exposure_random_forest_datasetNew.joblib"
)

FEATURE_PATH = (
    PROJECT_ROOT
    / "output"
    / "features"
    / "extracted_features.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "output"
    / "exposure"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "exposure_result.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

# Reference period for TWA calculation
TWA_REFERENCE_HOURS = 8.0


# ============================================================
# H2S STANDARDS
#
# IMPORTANT:
# These are separate criteria and should not be mixed.
# ============================================================

OSHA_GENERAL_INDUSTRY = {

    "name":
        "OSHA General Industry",

    # OSHA Z-2 ceiling
    "ceiling_ppm":
        20.0,

    # OSHA maximum peak
    "peak_ppm":
        50.0,

    # Maximum peak duration
    "peak_duration_minutes":
        10.0,

    # OSHA General Industry H2S does NOT specify
    # an 8-hour TWA in this Z-2 criterion.
    "twa_ppm":
        None,

    # NIOSH IDLH is included as an emergency
    # reference, not as an OSHA PEL.
    "idlh_ppm":
        100.0
}


NIOSH = {

    "name":
        "NIOSH REL",

    # NIOSH REL is a 10-minute ceiling
    "ceiling_ppm":
        10.0,

    "ceiling_duration_minutes":
        10.0,

    "peak_ppm":
        None,

    "peak_duration_minutes":
        None,

    "twa_ppm":
        None,

    "idlh_ppm":
        100.0
}


# ============================================================
# SELECT THE STANDARD USED BY YOUR APPLICATION
# ============================================================

STANDARD = OSHA_GENERAL_INDUSTRY


# ============================================================
# INPUT HELPER
# ============================================================

def get_positive_number(message):

    while True:

        try:

            value = float(
                input(message)
            )

            if value < 0:

                print(
                    "Please enter a value "
                    "greater than or equal to 0."
                )

                continue

            return value

        except ValueError:

            print(
                "Invalid input. "
                "Please enter a number."
            )


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    print(
        "\nLoading trained model..."
    )

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"\nModel not found:\n"
            f"{MODEL_PATH}\n\n"
            "Place the trained .joblib file "
            "in the project root."
        )

    package = joblib.load(
        MODEL_PATH
    )

    model = package["model"]

    model_features = package["features"]

    print(
        "Model loaded successfully."
    )

    print(
        f"Expected features: "
        f"{len(model_features)}"
    )

    return model, model_features


# ============================================================
# LOAD EXTRACTED FEATURES
# ============================================================

def load_features(model_features):

    if not FEATURE_PATH.exists():

        raise FileNotFoundError(
            f"\nFeature file not found:\n"
            f"{FEATURE_PATH}\n\n"
            "Run Step 4 first."
        )

    df = pd.read_csv(
        FEATURE_PATH
    )

    # Check all expected features
    missing = [
        feature
        for feature in model_features
        if feature not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing model features:\n"
            + "\n".join(missing)
        )

    # IMPORTANT:
    # Force exact training order
    X = df[
        model_features
    ].astype(float)

    print(
        "Feature order verified."
    )

    return X


# ============================================================
# PREDICT H2S CONCENTRATION
# ============================================================

def predict_h2s(model, X):

    prediction = model.predict(
        X
    )

    concentration_ppm = float(
        prediction[0]
    )

    # Concentration cannot physically
    # be negative.
    concentration_ppm = max(
        0.0,
        concentration_ppm
    )

    return concentration_ppm


# ============================================================
# CUMULATIVE EXPOSURE
# ============================================================

def calculate_cumulative_exposure(
        concentration_ppm,
        exposure_hours):

    cumulative_exposure = (
        concentration_ppm
        * exposure_hours
    )

    return cumulative_exposure


# ============================================================
# 8-HOUR TWA
# ============================================================

def calculate_twa(
        cumulative_exposure):

    twa = (
        cumulative_exposure
        / TWA_REFERENCE_HOURS
    )

    return twa


# ============================================================
# EVALUATE SAFETY CRITERIA
# ============================================================

def evaluate_alerts(
        concentration_ppm,
        twa_ppm,
        exposure_hours,
        standard):

    alerts = []

    standard_name = standard["name"]

    # --------------------------------------------------------
    # IDLH
    # --------------------------------------------------------

    idlh = standard.get(
        "idlh_ppm"
    )

    if (
        idlh is not None
        and concentration_ppm >= idlh
    ):

        alerts.append({

            "level":
                "CRITICAL",

            "type":
                "IDLH",

            "message":
                (
                    f"H2S concentration "
                    f"{concentration_ppm:.2f} ppm "
                    f"is at or above the "
                    f"{idlh:.1f} ppm IDLH value."
                )
        })


    # --------------------------------------------------------
    # OSHA CEILING
    # --------------------------------------------------------

    ceiling = standard.get(
        "ceiling_ppm"
    )

    if (
        ceiling is not None
        and concentration_ppm > ceiling
    ):

        alerts.append({

            "level":
                "WARNING",

            "type":
                "CEILING",

            "message":
                (
                    f"H2S concentration "
                    f"{concentration_ppm:.2f} ppm "
                    f"exceeds the "
                    f"{ceiling:.1f} ppm "
                    f"{standard_name} ceiling criterion."
                )
        })


    # --------------------------------------------------------
    # OSHA PEAK
    # --------------------------------------------------------

    peak = standard.get(
        "peak_ppm"
    )

    peak_minutes = standard.get(
        "peak_duration_minutes"
    )

    if peak is not None:

        if concentration_ppm > peak:

            alerts.append({

                "level":
                    "CRITICAL",

                "type":
                    "PEAK",

                "message":
                    (
                        f"H2S concentration "
                        f"{concentration_ppm:.2f} ppm "
                        f"exceeds the "
                        f"{peak:.1f} ppm peak criterion."
                    )
            )

        elif (
            concentration_ppm > ceiling
            and exposure_hours * 60.0
                > peak_minutes
        ):

            alerts.append({

                "level":
                    "WARNING",

                "type":
                    "PEAK_DURATION",

                "message":
                    (
                        f"Concentration is above "
                        f"{ceiling:.1f} ppm and the "
                        f"entered exposure duration "
                        f"is longer than the "
                        f"{peak_minutes:.0f}-minute "
                        "peak allowance."
                    )
            })


    # --------------------------------------------------------
    # TWA
    #
    # Only evaluate if the selected standard
    # actually defines a TWA limit.
    # --------------------------------------------------------

    twa_limit = standard.get(
        "twa_ppm"
    )

    if twa_limit is not None:

        if twa_ppm > twa_limit:

            alerts.append({

                "level":
                    "WARNING",

                "type":
                    "TWA",

                "message":
                    (
                        f"8-hour TWA "
                        f"{twa_ppm:.2f} ppm "
                        f"exceeds the "
                        f"{twa_limit:.1f} ppm "
                        "TWA limit."
                    )
            })


    return alerts


# ============================================================
# DISPLAY ALERT
# ============================================================

def display_alerts(alerts):

    print(
        "\n" + "=" * 65
    )

    print(
        "EMPLOYEE SAFETY STATUS"
    )

    print(
        "=" * 65
    )

    if not alerts:

        print(
            "\nSTATUS: "
            "NO CONFIGURED CRITERION EXCEEDED"
        )

        print(
            "\nContinue following your "
            "site's H2S safety procedures."
        )

        return


    # Critical alerts first
    severity_order = {
        "CRITICAL": 0,
        "WARNING": 1
    }

    alerts = sorted(
        alerts,
        key=lambda x:
            severity_order.get(
                x["level"],
                99
            )
    )


    for alert in alerts:

        print(
            f"\n[{alert['level']}] "
            f"{alert['type']}"
        )

        print(
            alert["message"]
        )


    print(
        "\n*** FOLLOW SITE EMERGENCY / "
        "H2S RESPONSE PROCEDURES ***"
    )


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(
        concentration_ppm,
        exposure_hours,
        cumulative_exposure,
        twa_ppm,
        alerts,
        standard):

    alert_status = (
        "ALERT"
        if alerts
        else "NORMAL"
    )

    highest_level = (
        "NORMAL"
    )

    if alerts:

        if any(
            a["level"] == "CRITICAL"
            for a in alerts
        ):

            highest_level = "CRITICAL"

        else:

            highest_level = "WARNING"


    result = {

        "Timestamp":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "Standard":
            standard["name"],

        "H2S_Concentration_ppm":
            concentration_ppm,

        "Exposure_Duration_hr":
            exposure_hours,

        "Cumulative_Exposure_ppm_hr":
            cumulative_exposure,

        "TWA_8hr_ppm":
            twa_ppm,

        "Alert_Status":
            alert_status,

        "Alert_Level":
            highest_level,

        "Alert_Messages":
            " | ".join(
                a["message"]
                for a in alerts
            )
    }


    result_df = pd.DataFrame(
        [result]
    )

    result_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"\nResult saved to:\n"
        f"{OUTPUT_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 65
    )

    print(
        "H2S EXPOSURE MONITOR"
    )

    print(
        "=" * 65
    )

    print(
        "\nStandard:"
    )

    print(
        STANDARD["name"]
    )


    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    model, model_features = (
        load_model()
    )


    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    X = load_features(
        model_features
    )


    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    concentration_ppm = (
        predict_h2s(
            model,
            X
        )
    )


    print(
        "\n" + "=" * 65
    )

    print(
        "MODEL RESULT"
    )

    print(
        "=" * 65
    )

    print(
        f"\nPredicted H2S concentration:"
    )

    print(
        f"{concentration_ppm:.2f} ppm"
    )


    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    print(
        "\nEnter exposure duration."
    )

    exposure_hours = (
        get_positive_number(
            "Exposure duration (hours): "
        )
    )


    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    cumulative_exposure = (
        calculate_cumulative_exposure(
            concentration_ppm,
            exposure_hours
        )
    )


    # --------------------------------------------------------
    # STEP 6
    # --------------------------------------------------------

    twa_ppm = calculate_twa(
        cumulative_exposure
    )


    # --------------------------------------------------------
    # STEP 7
    # --------------------------------------------------------

    alerts = evaluate_alerts(
        concentration_ppm,
        twa_ppm,
        exposure_hours,
        STANDARD
    )


    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    print(
        "\n" + "=" * 65
    )

    print(
        "EXPOSURE RESULTS"
    )

    print(
        "=" * 65
    )

    print(
        f"\nH2S concentration:"
        f" {concentration_ppm:.2f} ppm"
    )

    print(
        f"Exposure duration:"
        f" {exposure_hours:.2f} hr"
    )

    print(
        f"Cumulative exposure:"
        f" {cumulative_exposure:.2f} ppm.hr"
    )

    print(
        f"8-hour TWA:"
        f" {twa_ppm:.2f} ppm"
    )


    # --------------------------------------------------------
    # ALERT
    # --------------------------------------------------------

    display_alerts(
        alerts
    )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    save_result(
        concentration_ppm,
        exposure_hours,
        cumulative_exposure,
        twa_ppm,
        alerts,
        STANDARD
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()