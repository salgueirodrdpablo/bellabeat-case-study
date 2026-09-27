from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# CONFIGURATION
# ============================================================

DATA_FOLDER = Path("data")
OUTPUT_FOLDER = DATA_FOLDER / "visualizations"

OUTPUT_FOLDER.mkdir(exist_ok=True)

hourly_file = DATA_FOLDER / "hourlyActivity_aggregated.csv"
minute_file = DATA_FOLDER / "minuteActivity_aggregated.csv"

# ============================================================
# CHARGEMENT
# ============================================================

hourly = pd.read_csv(hourly_file)
minute = pd.read_csv(minute_file)

hourly["ActivityHour"] = pd.to_datetime(hourly["ActivityHour"])
minute["ActivityMinute"] = pd.to_datetime(minute["ActivityMinute"])

# ============================================================
# 1. PROFIL HORAIRE MOYEN DES PAS
# ============================================================

hourly["Hour"] = hourly["ActivityHour"].dt.hour

steps_by_hour = (
    hourly
    .groupby("Hour")["StepTotal"]
    .mean()
)

plt.figure(figsize=(12, 6))

plt.plot(
    steps_by_hour.index,
    steps_by_hour.values,
    marker="o"
)

plt.xlabel("Heure")
plt.ylabel("Pas moyens")
plt.title("Profil moyen des pas selon l'heure")

plt.xticks(range(24))

plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    OUTPUT_FOLDER / "01_steps_by_hour.png",
    dpi=150
)

plt.show()

# ============================================================
# 2. CALORIES MOYENNES PAR HEURE
# ============================================================

calories_by_hour = (
    hourly
    .groupby("Hour")["Calories"]
    .mean()
)

plt.figure(figsize=(12, 6))

plt.plot(
    calories_by_hour.index,
    calories_by_hour.values,
    marker="o"
)

plt.xlabel("Heure")
plt.ylabel("Calories moyennes")
plt.title("Calories moyennes selon l'heure")

plt.xticks(range(24))

plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    OUTPUT_FOLDER / "02_calories_by_hour.png",
    dpi=150
)

plt.show()

# ============================================================
# 3. INTENSITÉ MOYENNE PAR HEURE
# ============================================================

intensity_by_hour = (
    hourly
    .groupby("Hour")["AverageIntensity"]
    .mean()
)

plt.figure(figsize=(12, 6))

plt.plot(
    intensity_by_hour.index,
    intensity_by_hour.values,
    marker="o"
)

plt.xlabel("Heure")
plt.ylabel("Intensité moyenne")
plt.title("Intensité moyenne selon l'heure")

plt.xticks(range(24))

plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    OUTPUT_FOLDER / "03_intensity_by_hour.png",
    dpi=150
)

plt.show()

# ============================================================
# 4. HEATMAP JOUR × HEURE
# ============================================================

days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

hourly["DayOfWeek"] = pd.Categorical(
    hourly["ActivityHour"].dt.day_name(),
    categories=days,
    ordered=True
)

heatmap = (
    hourly
    .groupby(
        ["DayOfWeek", "Hour"],
        observed=True
    )["StepTotal"]
    .mean()
    .unstack()
)

plt.figure(figsize=(14, 6))

plt.imshow(
    heatmap,
    aspect="auto"
)

plt.colorbar(
    label="Pas moyens"
)

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(days)),
    days
)

plt.xlabel("Heure")
plt.ylabel("Jour de la semaine")
plt.title("Activité moyenne : jour × heure")

plt.tight_layout()
plt.savefig(
    OUTPUT_FOLDER / "04_heatmap_day_hour.png",
    dpi=150
)

plt.show()

# ============================================================
# 5. PROFIL MINUTE MOYEN SUR 24H
# ============================================================

minute["MinuteOfDay"] = (
    minute["ActivityMinute"].dt.hour * 60
    + minute["ActivityMinute"].dt.minute
)

minute_profile = (
    minute
    .groupby("MinuteOfDay")["Steps"]
    .mean()
)

plt.figure(figsize=(14, 6))

plt.plot(
    minute_profile.index,
    minute_profile.values
)

plt.xlabel("Minute de la journée")
plt.ylabel("Pas moyens par minute")
plt.title("Profil moyen de l'activité sur 24 heures")

plt.xticks(
    range(0, 1441, 120),
    [
        "00:00",
        "02:00",
        "04:00",
        "06:00",
        "08:00",
        "10:00",
        "12:00",
        "14:00",
        "16:00",
        "18:00",
        "20:00",
        "22:00",
        "24:00"
    ]
)

plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    OUTPUT_FOLDER / "5_minute_profile.png",
    dpi=150
)

plt.show()

# ============================================================
# 6. TOP 20 COUPLES JOUR × HEURE
# ============================================================

day_hour = (
    hourly
    .groupby(
        ["DayOfWeek", "Hour"],
        observed=True
    )["StepTotal"]
    .mean()
    .sort_values(ascending=False)
    .head(20)
)

labels = [
    f"{day} {hour:02d}:00"
    for day, hour in day_hour.index
]

plt.figure(figsize=(12, 8))

plt.barh(
    labels[::-1],
    day_hour.values[::-1]
)

plt.xlabel("Pas moyens")
plt.ylabel("Jour et heure")
plt.title("Top 20 des périodes les plus actives")

plt.tight_layout()
plt.savefig(
    OUTPUT_FOLDER / "6_top_day_hour.png",
    dpi=150
)

plt.show()

# ============================================================
# FIN
# ============================================================

print(
    f"\nVisualisations sauvegardées dans : "
    f"{OUTPUT_FOLDER}"
)
