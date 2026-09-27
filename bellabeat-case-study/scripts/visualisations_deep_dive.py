import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = "data"
OUTPUT_DIR = os.path.join(DATA_DIR, "visualizations_deep_dive")

os.makedirs(OUTPUT_DIR, exist_ok=True)

DAILY_FILE = os.path.join(DATA_DIR, "dailyActivity_merged.csv")
HOURLY_FILE = os.path.join(DATA_DIR, "hourlyActivity_aggregated.csv")

# ============================================================
# CHARGEMENT
# ============================================================

daily = pd.read_csv(DAILY_FILE)
hourly = pd.read_csv(HOURLY_FILE)

daily["ActivityDate"] = pd.to_datetime(daily["ActivityDate"])
hourly["ActivityHour"] = pd.to_datetime(hourly["ActivityHour"])

hourly["Hour"] = hourly["ActivityHour"].dt.hour
hourly["DayOfWeek"] = hourly["ActivityHour"].dt.day_name()

# Ordre logique des jours
day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

hourly["DayOfWeek"] = pd.Categorical(
    hourly["DayOfWeek"],
    categories=day_order,
    ordered=True
)

# Weekday / Weekend
hourly["Period"] = np.where(
    hourly["DayOfWeek"].isin(
        ["Saturday", "Sunday"]
    ),
    "Weekend",
    "Weekday"
)

# ============================================================
# UTILITAIRE POUR SAUVEGARDER LES FIGURES
# ============================================================

def save_plot(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()
    plt.close()

# ============================================================
# 1. HEATMAP : STEPS PAR JOUR ET HEURE
# ============================================================

heatmap_steps = (
    hourly
    .pivot_table(
        index="DayOfWeek",
        columns="Hour",
        values="StepTotal",
        aggfunc="mean",
        observed=False
    )
    .reindex(day_order)
)

plt.figure(figsize=(13, 5))

plt.imshow(
    heatmap_steps,
    aspect="auto",
    interpolation="nearest"
)

plt.colorbar(label="StepTotal moyen")

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(day_order)),
    day_order
)

plt.xlabel("Heure")
plt.ylabel("Jour")
plt.title("Heatmap — nombre moyen de pas par jour et par heure")

save_plot("01_heatmap_steps.png")

# ============================================================
# 2. HEATMAP : CALORIES
# ============================================================

heatmap_calories = (
    hourly
    .pivot_table(
        index="DayOfWeek",
        columns="Hour",
        values="Calories",
        aggfunc="mean",
        observed=False
    )
    .reindex(day_order)
)

plt.figure(figsize=(13, 5))

plt.imshow(
    heatmap_calories,
    aspect="auto",
    interpolation="nearest"
)

plt.colorbar(label="Calories moyennes")

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(day_order)),
    day_order
)

plt.xlabel("Heure")
plt.ylabel("Jour")
plt.title("Heatmap — calories moyennes par jour et par heure")

save_plot("02_heatmap_calories.png")

# ============================================================
# 3. HEATMAP : INTENSITY
# ============================================================

heatmap_intensity = (
    hourly
    .pivot_table(
        index="DayOfWeek",
        columns="Hour",
        values="AverageIntensity",
        aggfunc="mean",
        observed=False
    )
    .reindex(day_order)
)

plt.figure(figsize=(13, 5))

plt.imshow(
    heatmap_intensity,
    aspect="auto",
    interpolation="nearest"
)

plt.colorbar(label="AverageIntensity moyenne")

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(day_order)),
    day_order
)

plt.xlabel("Heure")
plt.ylabel("Jour")
plt.title("Heatmap — intensité moyenne par jour et par heure")

save_plot("03_heatmap_intensity.png")

# ============================================================
# 4. HEATMAP : METs
# ============================================================

heatmap_mets = (
    hourly
    .pivot_table(
        index="DayOfWeek",
        columns="Hour",
        values="METs",
        aggfunc="mean",
        observed=False
    )
    .reindex(day_order)
)

plt.figure(figsize=(13, 5))

plt.imshow(
    heatmap_mets,
    aspect="auto",
    interpolation="nearest"
)

plt.colorbar(label="METs moyens")

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(day_order)),
    day_order
)

plt.xlabel("Heure")
plt.ylabel("Jour")
plt.title("Heatmap — METs moyens par jour et par heure")

save_plot("04_heatmap_mets.png")

# ============================================================
# 5. SEMAINE VS WEEK-END
# ============================================================

period_profile = (
    hourly
    .groupby(
        ["Period", "Hour"],
        observed=True
    )["StepTotal"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(10, 5))

for period in ["Weekday", "Weekend"]:

    subset = period_profile[
        period_profile["Period"] == period
    ]

    plt.plot(
        subset["Hour"],
        subset["StepTotal"],
        marker="o",
        label=period
    )

plt.title(
    "Profil horaire des pas : semaine vs week-end"
)

plt.xlabel("Heure")
plt.ylabel("StepTotal moyen")
plt.xticks(range(24))
plt.legend()
plt.grid(alpha=0.2)

save_plot("05_weekday_vs_weekend.png")

# ============================================================
# 6. HEATMAP UTILISATEUR × HEURE
# ============================================================

user_hour = (
    hourly
    .pivot_table(
        index="Id",
        columns="Hour",
        values="StepTotal",
        aggfunc="mean"
    )
)

# Trier les utilisateurs selon leur activité moyenne
user_order = (
    user_hour
    .mean(axis=1)
    .sort_values(ascending=False)
    .index
)

user_hour = user_hour.loc[user_order]

plt.figure(figsize=(13, 10))

plt.imshow(
    user_hour,
    aspect="auto",
    interpolation="nearest"
)

plt.colorbar(label="StepTotal moyen")

plt.xticks(
    range(24),
    range(24)
)

plt.yticks(
    range(len(user_hour)),
    user_hour.index
)

plt.xlabel("Heure")
plt.ylabel("Utilisateur")
plt.title(
    "Heatmap — activité horaire de chaque utilisateur"
)

save_plot("06_heatmap_users_hours.png")

# ============================================================
# 7. HEURE DU PIC D'ACTIVITÉ PAR UTILISATEUR
# ============================================================

user_hour_mean = (
    hourly
    .groupby(
        ["Id", "Hour"],
        observed=True
    )["StepTotal"]
    .mean()
    .reset_index()
)

peak_hours = (
    user_hour_mean
    .loc[
        user_hour_mean
        .groupby("Id")["StepTotal"]
        .idxmax()
    ]
)

peak_distribution = (
    peak_hours["Hour"]
    .value_counts()
    .sort_index()
)

plt.figure(figsize=(10, 5))

plt.bar(
    peak_distribution.index,
    peak_distribution.values
)

plt.title(
    "Distribution de l'heure du pic d'activité"
)

plt.xlabel("Heure du pic")
plt.ylabel("Nombre d'utilisateurs")
plt.xticks(range(24))
plt.grid(axis="y", alpha=0.2)

save_plot("07_peak_hour_distribution.png")

# ============================================================
# 8. PROFILS INDIVIDUELS — COMPARAISON
# ============================================================

# Sélection de quelques profils représentatifs :
# les utilisateurs les plus actifs et les moins actifs.

user_mean_steps = (
    hourly
    .groupby("Id")["StepTotal"]
    .mean()
    .sort_values()
)

n_profiles = 5

selected_users = list(
    user_mean_steps.head(n_profiles).index
) + list(
    user_mean_steps.tail(n_profiles).index
)

plt.figure(figsize=(11, 6))

for user_id in selected_users:

    profile = (
        hourly[
            hourly["Id"] == user_id
        ]
        .groupby("Hour")["StepTotal"]
        .mean()
    )

    plt.plot(
        profile.index,
        profile.values,
        marker="o",
        alpha=0.8,
        label=str(user_id)
    )

plt.title(
    "Profils horaires — utilisateurs les moins et les plus actifs"
)

plt.xlabel("Heure")
plt.ylabel("StepTotal moyen")
plt.xticks(range(24))

plt.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.grid(alpha=0.2)

save_plot("08_user_profiles.png")

# ============================================================
# ANALYSE NUMÉRIQUE
# ============================================================

print("\n" + "=" * 60)
print("ANALYSE DU PROFIL D'ACTIVITÉ")
print("=" * 60)

# ------------------------------------------------------------
# Heure avec le plus de pas
# ------------------------------------------------------------

hourly_profile = (
    hourly
    .groupby("Hour", observed=True)
    .agg(
        StepTotal=("StepTotal", "mean"),
        Calories=("Calories", "mean"),
        AverageIntensity=("AverageIntensity", "mean")
    )
)

peak_hour = hourly_profile["StepTotal"].idxmax()
peak_value = hourly_profile["StepTotal"].max()

print(
    f"\nHeure avec le plus de pas en moyenne : "
    f"{peak_hour:02d}:00 "
    f"({peak_value:.1f} pas)"
)

# ------------------------------------------------------------
# Heure avec le plus de calories
# ------------------------------------------------------------

peak_calories_hour = hourly_profile["Calories"].idxmax()

print(
    f"Heure avec le plus de calories en moyenne : "
    f"{peak_calories_hour:02d}:00"
)

# ------------------------------------------------------------
# Heure avec la plus forte intensité
# ------------------------------------------------------------

peak_intensity_hour = (
    hourly_profile["AverageIntensity"]
    .idxmax()
)

print(
    f"Heure avec la plus forte intensité moyenne : "
    f"{peak_intensity_hour:02d}:00"
)

# ------------------------------------------------------------
# Top 10 couples jour / heure
# ------------------------------------------------------------

day_hour = (
    hourly
    .groupby(
        ["DayOfWeek", "Hour"],
        observed=True
    )["StepTotal"]
    .mean()
    .sort_values(ascending=False)
)

print("\nTop 10 des périodes les plus actives :")

for (day, hour), value in day_hour.head(10).items():

    print(
        f"{day:10s} {hour:02d}:00 "
        f"→ {value:.1f} pas"
    )

# ------------------------------------------------------------
# Comparaison semaine / week-end
# ------------------------------------------------------------

weekday_mean = hourly.loc[
    hourly["Period"] == "Weekday",
    "StepTotal"
].mean()

weekend_mean = hourly.loc[
    hourly["Period"] == "Weekend",
    "StepTotal"
].mean()

print("\nMoyenne horaire :")

print(
    f"  Semaine  : {weekday_mean:.2f} pas"
)

print(
    f"  Week-end : {weekend_mean:.2f} pas"
)

# ------------------------------------------------------------
# Heure du pic par utilisateur
# ------------------------------------------------------------

print("\nHeure du pic par utilisateur :")

peak_hours_sorted = peak_hours.sort_values(
    "Hour"
)

for _, row in peak_hours_sorted.iterrows():

    print(
        f"  {int(row['Id'])} → "
        f"{int(row['Hour']):02d}:00 "
        f"({row['StepTotal']:.1f} pas)"
    )

print("\n" + "=" * 60)
print(
    f"Visualisations enregistrées dans : {OUTPUT_DIR}"
)
print("=" * 60)
