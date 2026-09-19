import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

HISTORY_PATH = (
    PROJECT_ROOT /
    "output" /
    "history" /
    "exposure_history.csv"
)


# ============================================================
# LONG-TERM CONFIGURATION
# ============================================================

# These values correspond to the project's supplied framework.
# Verify regulatory applicability before using them as official
# occupational-health limits.

WEEKLY_REFERENCE_PPM_HR = 40.0

ROTATIONAL_REFERENCE_PPM_HR = 84.0

WEEKLY_ACTION_PPM_HR = 20.0

MONTHLY_ACTION_TWA_PPM = 0.5

ROTATIONAL_ACTION_PPM_HR = 40.0

LONG_TERM_TWA_HOURS = 30 * 24


# ============================================================
# HEADER
# ============================================================

print("\n")
print("======================================================")
print("             LONG-TERM H2S MONITOR")
print("======================================================")


# ============================================================
# CHECK HISTORY FILE
# ============================================================

if not HISTORY_PATH.exists():

    print("\nNo exposure history found.")

    print("\nExpected file:")
    print(HISTORY_PATH)

    print(
        "\nRun 05_predict_model.py at least once "
        "to create the exposure history."
    )

    raise SystemExit


# ============================================================
# LOAD HISTORY
# ============================================================

try:

    df = pd.read_csv(
        HISTORY_PATH
    )

except Exception as e:

    print("\nERROR reading exposure history:")
    print(e)

    raise SystemExit


if df.empty:

    print("\nExposure history is empty.")

    raise SystemExit


# ============================================================
# VALIDATE COLUMNS
# ============================================================

required_columns = [
    "Timestamp",
    "H2S_Concentration_ppm",
    "Exposure_Duration_hr",
    "Shift_Exposure_ppm_hr"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print("\nERROR: Missing columns:")

    for column in missing_columns:
        print(" -", column)

    raise SystemExit


# ============================================================
# CLEAN DATA
# ============================================================

df["Timestamp"] = pd.to_datetime(
    df["Timestamp"],
    errors="coerce"
)

df["H2S_Concentration_ppm"] = pd.to_numeric(
    df["H2S_Concentration_ppm"],
    errors="coerce"
)

df["Exposure_Duration_hr"] = pd.to_numeric(
    df["Exposure_Duration_hr"],
    errors="coerce"
)

df["Shift_Exposure_ppm_hr"] = pd.to_numeric(
    df["Shift_Exposure_ppm_hr"],
    errors="coerce"
)


# Remove invalid rows

df = df.dropna(
    subset=[
        "Timestamp",
        "H2S_Concentration_ppm",
        "Exposure_Duration_hr",
        "Shift_Exposure_ppm_hr"
    ]
)


if df.empty:

    print("\nNo valid exposure records found.")

    raise SystemExit


# ============================================================
# SORT CHRONOLOGICALLY
# ============================================================

df = df.sort_values(
    "Timestamp"
).reset_index(drop=True)


# ============================================================
# CURRENT TIME
# ============================================================

now = pd.Timestamp.now()


# ============================================================
# WEEKLY WINDOW
# ============================================================

week_start = now - pd.Timedelta(
    days=7
)

weekly_df = df[
    df["Timestamp"] >= week_start
].copy()


# ============================================================
# MONTHLY WINDOW
# ============================================================

month_start = now - pd.Timedelta(
    days=30
)

monthly_df = df[
    df["Timestamp"] >= month_start
].copy()


# ============================================================
# ROTATION WINDOW
# ============================================================

# The project currently uses an 84-hour rotational reference.
# Here we calculate the accumulated exposure over the latest
# 84 hours of recorded monitoring.

rotation_start = now - pd.Timedelta(
    hours=84
)

rotation_df = df[
    df["Timestamp"] >= rotation_start
].copy()


# ============================================================
# WEEKLY EXPOSURE
# ============================================================

if not weekly_df.empty:

    weekly_dose = weekly_df[
        "Shift_Exposure_ppm_hr"
    ].sum()

    weekly_hours = weekly_df[
        "Exposure_Duration_hr"
    ].sum()

else:

    weekly_dose = 0.0
    weekly_hours = 0.0


# ============================================================
# MONTHLY TWA
# ============================================================

if not monthly_df.empty:

    weighted_exposure = (
        monthly_df[
            "H2S_Concentration_ppm"
        ]
        *
        monthly_df[
            "Exposure_Duration_hr"
        ]
    ).sum()

    monthly_hours = monthly_df[
        "Exposure_Duration_hr"
    ].sum()

    if monthly_hours > 0:

        monthly_twa = (
            weighted_exposure /
            monthly_hours
        )

    else:

        monthly_twa = 0.0

else:

    monthly_twa = 0.0
    monthly_hours = 0.0


# ============================================================
# ROTATIONAL EXPOSURE
# ============================================================

if not rotation_df.empty:

    rotation_dose = rotation_df[
        "Shift_Exposure_ppm_hr"
    ].sum()

    rotation_hours = rotation_df[
        "Exposure_Duration_hr"
    ].sum()

else:

    rotation_dose = 0.0
    rotation_hours = 0.0


# ============================================================
# WEEKLY STATUS
# ============================================================

weekly_status = "NORMAL"

if weekly_dose >= WEEKLY_ACTION_PPM_HR:
    weekly_status = "ACTION"

if weekly_dose >= WEEKLY_REFERENCE_PPM_HR:
    weekly_status = "LIMIT EXCEEDED"


# ============================================================
# MONTHLY STATUS
# ============================================================

monthly_status = "NORMAL"

if monthly_twa >= MONTHLY_ACTION_TWA_PPM:
    monthly_status = "MEDICAL REVIEW"


# ============================================================
# ROTATIONAL STATUS
# ============================================================

rotation_status = "NORMAL"

if rotation_dose >= ROTATIONAL_ACTION_PPM_HR:
    rotation_status = "ACTION"

if rotation_dose >= ROTATIONAL_REFERENCE_PPM_HR:
    rotation_status = "LIMIT EXCEEDED"


# ============================================================
# DISPLAY WEEKLY RESULTS
# ============================================================

print("\n------------------------------------------------------")
print("WEEKLY EXPOSURE")
print("------------------------------------------------------")

print(
    f"Monitoring records : {len(weekly_df)}"
)

print(
    f"Exposure duration  : {weekly_hours:.2f} hr"
)

print(
    f"Total exposure     : {weekly_dose:.2f} ppm.hr"
)

print(
    f"Reference          : "
    f"{WEEKLY_REFERENCE_PPM_HR:.2f} ppm.hr/week"
)

print(
    f"Action level       : "
    f"{WEEKLY_ACTION_PPM_HR:.2f} ppm.hr/week"
)

print(
    f"Status             : {weekly_status}"
)


# ============================================================
# DISPLAY MONTHLY RESULTS
# ============================================================

print("\n------------------------------------------------------")
print("30-DAY EXPOSURE")
print("------------------------------------------------------")

print(
    f"Monitoring records : {len(monthly_df)}"
)

print(
    f"Exposure duration  : {monthly_hours:.2f} hr"
)

print(
    f"30-day TWA         : {monthly_twa:.4f} ppm"
)

print(
    f"Action level       : "
    f"{MONTHLY_ACTION_TWA_PPM:.2f} ppm"
)

print(
    f"Status             : {monthly_status}"
)


# ============================================================
# DISPLAY ROTATIONAL RESULTS
# ============================================================

print("\n------------------------------------------------------")
print("84-HOUR ROTATIONAL WINDOW")
print("------------------------------------------------------")

print(
    f"Monitoring records : {len(rotation_df)}"
)

print(
    f"Exposure duration  : {rotation_hours:.2f} hr"
)

print(
    f"Rotation exposure  : "
    f"{rotation_dose:.2f} ppm.hr"
)

print(
    f"Reference          : "
    f"{ROTATIONAL_REFERENCE_PPM_HR:.2f} ppm.hr"
)

print(
    f"Action level       : "
    f"{ROTATIONAL_ACTION_PPM_HR:.2f} ppm.hr"
)

print(
    f"Status             : {rotation_status}"
)


# ============================================================
# OVERALL STATUS
# ============================================================

overall_status = "NORMAL"


if (
    weekly_status != "NORMAL"
    or
    monthly_status != "NORMAL"
    or
    rotation_status != "NORMAL"
):

    overall_status = "ACTION REQUIRED"


if (
    weekly_status == "LIMIT EXCEEDED"
    or
    rotation_status == "LIMIT EXCEEDED"
):

    overall_status = "LIMIT EXCEEDED"


# ============================================================
# ACTION RECOMMENDATIONS
# ============================================================

actions = []


if weekly_status == "ACTION":

    actions.append(
        "Review PPE condition and investigate "
        "possible workplace H2S sources."
    )


if weekly_status == "LIMIT EXCEEDED":

    actions.append(
        "Weekly configured exposure reference exceeded; "
        "perform workplace exposure investigation."
    )


if monthly_status == "MEDICAL REVIEW":

    actions.append(
        "Monthly configured TWA action level exceeded; "
        "refer to the site's occupational-health procedure."
    )


if rotation_status == "ACTION":

    actions.append(
        "Rotational exposure action level exceeded; "
        "review exposure controls and work assignment."
    )


if rotation_status == "LIMIT EXCEEDED":

    actions.append(
        "Rotational configured exposure reference exceeded; "
        "perform formal exposure assessment."
    )


# ============================================================
# DISPLAY OVERALL STATUS
# ============================================================

print("\n======================================================")
print("                 OVERALL STATUS")
print("======================================================")

print(
    f"\nStatus: {overall_status}"
)


if actions:

    print("\nRecommended system actions:")

    for index, action in enumerate(actions, 1):

        print(
            f"{index}. {action}"
        )

else:

    print(
        "\nNo configured long-term action "
        "condition detected."
    )


# ============================================================
# SAVE LONG-TERM SUMMARY
# ============================================================

summary_path = (
    PROJECT_ROOT /
    "output" /
    "history" /
    "long_term_summary.csv"
)


summary = {

    "Calculation_Time":
        now.strftime("%Y-%m-%d %H:%M:%S"),

    "Weekly_Records":
        len(weekly_df),

    "Weekly_Exposure_ppm_hr":
        round(weekly_dose, 4),

    "Weekly_Status":
        weekly_status,

    "Monthly_Records":
        len(monthly_df),

    "Monthly_Exposure_Hours":
        round(monthly_hours, 4),

    "Monthly_TWA_ppm":
        round(monthly_twa, 4),

    "Monthly_Status":
        monthly_status,

    "Rotation_Records":
        len(rotation_df),

    "Rotation_Exposure_ppm_hr":
        round(rotation_dose, 4),

    "Rotation_Status":
        rotation_status,

    "Overall_Status":
        overall_status,

    "Actions":
        " | ".join(actions)
}


summary_df = pd.DataFrame(
    [summary]
)


summary_df.to_csv(
    summary_path,
    index=False
)


# ============================================================
# FINAL
# ============================================================

print("\n------------------------------------------------------")
print("SUMMARY SAVED")
print("------------------------------------------------------")

print(summary_path)

print("\n======================================================\n")