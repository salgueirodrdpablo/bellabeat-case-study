import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = "data"

HOURLY_FILE = os.path.join(
    DATA_DIR,
    "hourlyActivity_aggregated.csv"
)

DAILY_FILE = os.path.join(
    DATA_DIR,
    "dailyActivity_merged.csv"
)

OUTPUT_DIR = os.path.join(
    DATA_DIR,
    "activity_segments"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# CHARGEMENT
# ============================================================

hourly = pd.read_csv(HOURLY_FILE)
daily = pd.read_csv(DAILY_FILE)

hourly["ActivityHour"] = pd.to_datetime(
    hourly["ActivityHour"]
)

daily["ActivityDate"] = pd.to_datetime(
    daily["ActivityDate"]
)

hourly["Hour"] = hourly["ActivityHour"].dt.hour

hourly["DayOfWeek"] = (
    hourly["ActivityHour"]
    .dt.day_name()
)

hourly["IsWeekend"] = (
    hourly["DayOfWeek"]
    .isin(["Saturday", "Sunday"])
)

# ============================================================
# UTILITAIRE
# ============================================================

def save_plot(filename):

    path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

# ============================================================
# 1. PROFIL HORAIRE DE CHAQUE UTILISATEUR
# ============================================================

user_hourly = (
    hourly
    .groupby(
        ["Id", "Hour"],
        observed=True
    )
    .agg(
        Steps=("StepTotal", "mean"),
        Calories=("Calories", "mean"),
        Intensity=("AverageIntensity", "mean"),
        METs=("METs", "mean")
    )
    .reset_index()
)

# ============================================================
# 2. HEURE DU PIC POUR CHAQUE UTILISATEUR
# ============================================================

peak_idx = (
    user_hourly
    .groupby("Id")["Steps"]
    .idxmax()
)

user_peaks = (
    user_hourly
    .loc[peak_idx]
    [
        [
            "Id",
            "Hour",
            "Steps",
            "Calories",
            "Intensity",
            "METs"
        ]
    ]
    .rename(
        columns={
            "Hour": "PeakHour",
            "Steps": "PeakSteps",
            "Calories": "PeakCalories",
            "Intensity": "PeakIntensity",
            "METs": "PeakMETs"
        }
    )
    .reset_index(drop=True)
)

# ============================================================
# 3. SEGMENTATION DES UTILISATEURS
# ============================================================

def classify_peak(hour):

    if 5 <= hour <= 9:
        return "Early Movers"

    elif 10 <= hour <= 13:
        return "Midday Movers"

    elif 14 <= hour <= 16:
        return "Afternoon Movers"

    elif 17 <= hour <= 20:
        return "Evening Movers"

    else:
        return "Late Movers"

user_peaks["Segment"] = (
    user_peaks["PeakHour"]
    .apply(classify_peak)
)

# ============================================================
# 4. STATISTIQUES GLOBALES PAR UTILISATEUR
# ============================================================

user_stats = (
    hourly
    .groupby("Id")
    .agg(
        MeanHourlySteps=("StepTotal", "mean"),
        MeanHourlyCalories=("Calories", "mean"),
        MeanHourlyIntensity=(
            "AverageIntensity",
            "mean"
        ),
        MeanHourlyMETs=("METs", "mean"),
        StdHourlySteps=("StepTotal", "std"),
        ActiveHours=(
            "StepTotal",
            lambda x: (x > 100).sum()
        )
    )
    .reset_index()
)

# ============================================================
# 5. ACTIVITÉ SEMAINE VS WEEK-END
# ============================================================

weekday_weekend = (
    hourly
    .groupby(
        ["Id", "IsWeekend"],
        observed=True
    )
    .agg(
        MeanSteps=("StepTotal", "mean"),
        MeanCalories=("Calories", "mean"),
        MeanIntensity=(
            "AverageIntensity",
            "mean"
        )
    )
    .reset_index()
)

weekday = (
    weekday_weekend[
        weekday_weekend["IsWeekend"] == False
    ]
    .rename(
        columns={
            "MeanSteps": "WeekdaySteps",
            "MeanCalories": "WeekdayCalories",
            "MeanIntensity": "WeekdayIntensity"
        }
    )
    [
        [
            "Id",
            "WeekdaySteps",
            "WeekdayCalories",
            "WeekdayIntensity"
        ]
    ]
)

weekend = (
    weekday_weekend[
        weekday_weekend["IsWeekend"] == True
    ]
    .rename(
        columns={
            "MeanSteps": "WeekendSteps",
            "MeanCalories": "WeekendCalories",
            "MeanIntensity": "WeekendIntensity"
        }
    )
    [
        [
            "Id",
            "WeekendSteps",
            "WeekendCalories",
            "WeekendIntensity"
        ]
    ]
)

# ============================================================
# 6. TABLEAU FINAL PAR UTILISATEUR
# ============================================================

user_profiles = (
    user_peaks
    .merge(
        user_stats,
        on="Id",
        how="left"
    )
    .merge(
        weekday,
        on="Id",
        how="left"
    )
    .merge(
        weekend,
        on="Id",
        how="left"
    )
)

# Différence semaine / weekend
user_profiles["WeekendVsWeekday"] = (
    (
        user_profiles["WeekendSteps"]
        /
        user_profiles["WeekdaySteps"]
    ) - 1
) * 100

# ============================================================
# 7. EXPORT DU TABLEAU
# ============================================================

profile_file = os.path.join(
    OUTPUT_DIR,
    "user_activity_segments.csv"
)

user_profiles.to_csv(
    profile_file,
    index=False
)

# ============================================================
# 8. TAILLE DES SEGMENTS
# ============================================================

segment_counts = (
    user_profiles["Segment"]
    .value_counts()
)

print("\n" + "=" * 65)
print("SEGMENTATION DES UTILISATEURS")
print("=" * 65)

print(
    "\nNombre d'utilisateurs par segment :\n"
)

print(segment_counts)

# ============================================================
# VISUALISATION 1
# TAILLE DES SEGMENTS
# ============================================================

plt.figure(figsize=(9, 5))

segment_counts.sort_values().plot(
    kind="barh"
)

plt.title(
    "Répartition des utilisateurs par rythme d'activité"
)

plt.xlabel("Nombre d'utilisateurs")
plt.ylabel("Segment")

save_plot(
    "01_segment_sizes.png"
)

# ============================================================
# 9. PROFILS HORAIRES MOYENS PAR SEGMENT
# ============================================================

segment_hourly = (
    hourly
    .merge(
        user_profiles[
            ["Id", "Segment"]
        ],
        on="Id",
        how="left"
    )
    .groupby(
        ["Segment", "Hour"],
        observed=True
    )
    .agg(
        Steps=("StepTotal", "mean"),
        Calories=("Calories", "mean"),
        Intensity=(
            "AverageIntensity",
            "mean"
        )
    )
    .reset_index()
)

# ============================================================
# VISUALISATION 2
# PROFILS HORAIRES DES SEGMENTS
# ============================================================

segment_order = [
    "Early Movers",
    "Midday Movers",
    "Afternoon Movers",
    "Evening Movers",
    "Late Movers"
]

plt.figure(figsize=(11, 6))

for segment in segment_order:

    subset = segment_hourly[
        segment_hourly["Segment"] == segment
    ]

    if len(subset) == 0:
        continue

    plt.plot(
        subset["Hour"],
        subset["Steps"],
        marker="o",
        label=segment
    )

plt.title(
    "Profils horaires moyens des différents segments"
)

plt.xlabel("Heure")
plt.ylabel("StepTotal moyen")

plt.xticks(range(24))

plt.legend()

plt.grid(alpha=0.2)

save_plot(
    "02_segment_hourly_profiles.png"
)

# ============================================================
# VISUALISATION 3
# HEATMAP SEGMENT × HEURE
# ============================================================

segment_heatmap = (
    segment_hourly
    .pivot(
        index="Segment",
        columns="Hour",
        values="Steps"
    )
    .reindex(segment_order)
)

plt.figure(figsize=(13, 5))

plt.imshow(
    segment_heatmap,
    aspect="auto",
    interpolation="nearest"
)

plt.colorbar(
    label="StepTotal moyen"
)

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(segment_heatmap)),
    segment_heatmap.index
)

plt.xlabel("Heure")
plt.ylabel("Segment")

plt.title(
    "Heatmap — activité horaire par segment"
)

save_plot(
    "03_segment_heatmap.png"
)

# ============================================================
# VISUALISATION 4
# COMPARAISON DES MÉTRIQUES PAR SEGMENT
# ============================================================

segment_metrics = (
    user_profiles
    .groupby("Segment")
    .agg(
        Steps=("MeanHourlySteps", "mean"),
        Calories=("MeanHourlyCalories", "mean"),
        Intensity=("MeanHourlyIntensity", "mean")
    )
    .reindex(segment_order)
)

plt.figure(figsize=(10, 5))

x = np.arange(
    len(segment_metrics)
)

width = 0.25

plt.bar(
    x - width,
    segment_metrics["Steps"],
    width,
    label="Pas"
)

plt.bar(
    x,
    segment_metrics["Calories"],
    width,
    label="Calories"
)

plt.bar(
    x + width,
    segment_metrics["Intensity"] * 1000,
    width,
    label="Intensité ×1000"
)

plt.xticks(
    x,
    segment_metrics.index,
    rotation=20
)

plt.ylabel("Valeur moyenne")

plt.title(
    "Comparaison des métriques entre segments"
)

plt.legend()

save_plot(
    "04_segment_metrics.png"
)

# ============================================================
# VISUALISATION 5
# SEMAINE VS WEEK-END PAR SEGMENT
# ============================================================

segment_weekend = (
    user_profiles
    .groupby("Segment")
    .agg(
        Weekday=(
            "WeekdaySteps",
            "mean"
        ),
        Weekend=(
            "WeekendSteps",
            "mean"
        )
    )
    .reindex(segment_order)
)

plt.figure(figsize=(10, 5))

x = np.arange(
    len(segment_weekend)
)

width = 0.35

plt.bar(
    x - width / 2,
    segment_weekend["Weekday"],
    width,
    label="Semaine"
)

plt.bar(
    x + width / 2,
    segment_weekend["Weekend"],
    width,
    label="Week-end"
)

plt.xticks(
    x,
    segment_weekend.index,
    rotation=20
)

plt.ylabel(
    "StepTotal moyen / heure"
)

plt.title(
    "Activité semaine vs week-end selon le segment"
)

plt.legend()

save_plot(
    "05_segment_weekend.png"
)

# ============================================================
# 10. DISTRIBUTION DES HEURES DE PIC
# ============================================================

plt.figure(figsize=(10, 5))

plt.hist(
    user_profiles["PeakHour"],
    bins=np.arange(
        0,
        25,
        1
    ),
    align="left"
)

plt.xlabel("Heure du pic")
plt.ylabel("Nombre d'utilisateurs")

plt.xticks(range(24))

plt.title(
    "Distribution de l'heure du pic d'activité"
)

plt.grid(
    axis="y",
    alpha=0.2
)

save_plot(
    "06_peak_hour_distribution.png"
)

# ============================================================
# 11. PIC D'ACTIVITÉ VS ACTIVITÉ MOYENNE
# ============================================================

plt.figure(figsize=(9, 6))

for segment in segment_order:

    subset = user_profiles[
        user_profiles["Segment"] == segment
    ]

    if len(subset) == 0:
        continue

    plt.scatter(
        subset["MeanHourlySteps"],
        subset["PeakSteps"],
        alpha=0.8,
        label=segment
    )

plt.xlabel(
    "Pas moyens par heure"
)

plt.ylabel(
    "Pas à l'heure du pic"
)

plt.title(
    "Intensité du pic vs activité moyenne"
)

plt.legend()

plt.grid(alpha=0.2)

save_plot(
    "07_peak_vs_average.png"
)

# ============================================================
# 12. VARIATION WEEK-END / SEMAINE
# ============================================================

plt.figure(figsize=(10, 6))

for segment in segment_order:

    subset = user_profiles[
        user_profiles["Segment"] == segment
    ]

    if len(subset) == 0:
        continue

    plt.scatter(
        subset["MeanHourlySteps"],
        subset["WeekendVsWeekday"],
        alpha=0.8,
        label=segment
    )

plt.axhline(
    0,
    linewidth=1
)

plt.xlabel(
    "Activité moyenne (pas/heure)"
)

plt.ylabel(
    "Variation week-end vs semaine (%)"
)

plt.title(
    "Variation du rythme entre semaine et week-end"
)

plt.legend()

plt.grid(alpha=0.2)

save_plot(
    "08_weekend_variation.png"
)

# ============================================================
# 13. STATISTIQUES PAR SEGMENT
# ============================================================

segment_summary = (
    user_profiles
    .groupby("Segment")
    .agg(
        Users=("Id", "nunique"),

        MeanPeakHour=(
            "PeakHour",
            "mean"
        ),

        MeanPeakSteps=(
            "PeakSteps",
            "mean"
        ),

        MeanHourlySteps=(
            "MeanHourlySteps",
            "mean"
        ),

        MeanHourlyCalories=(
            "MeanHourlyCalories",
            "mean"
        ),

        MeanHourlyIntensity=(
            "MeanHourlyIntensity",
            "mean"
        ),

        WeekdaySteps=(
            "WeekdaySteps",
            "mean"
        ),

        WeekendSteps=(
            "WeekendSteps",
            "mean"
        ),

    )
    .reindex(segment_order)
)

# Variation calculée à partir des moyennes du segment
segment_summary["WeekendVsWeekday"] = (
    segment_summary["WeekendSteps"]
    / segment_summary["WeekdaySteps"]
    - 1
) * 100

# ============================================================
# EXPORT STATISTIQUES
# ============================================================

summary_file = os.path.join(
    OUTPUT_DIR,
    "segment_summary.csv"
)

segment_summary.to_csv(
    summary_file
)

# ============================================================
# AFFICHAGE DES RÉSULTATS
# ============================================================

print("\n" + "=" * 65)
print("PROFILS DES SEGMENTS")
print("=" * 65)

print(
    segment_summary.round(2)
)

print("\n" + "=" * 65)
print("UTILISATEURS PAR SEGMENT")
print("=" * 65)

for segment in segment_order:

    users = user_profiles[
        user_profiles["Segment"] == segment
    ]

    if len(users) == 0:
        continue

    print(
        f"\n{segment} "
        f"({len(users)} utilisateurs)"
    )

    for _, row in users.sort_values(
        "PeakHour"
    ).iterrows():

        print(
            f"  {int(row['Id'])} "
            f"→ pic {int(row['PeakHour']):02d}:00 "
            f"| {row['PeakSteps']:.0f} pas"
        )

print("\n" + "=" * 65)
print("FICHIERS")
print("=" * 65)

print(
    f"\nProfils utilisateurs :\n"
    f"{profile_file}"
)

print(
    f"\nRésumé des segments :\n"
    f"{summary_file}"
)

print(
    f"\nVisualisations :\n"
    f"{OUTPUT_DIR}"
)
