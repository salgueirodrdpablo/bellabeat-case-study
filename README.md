# Étude de cas Bellabeat : comment une entreprise de bien-être peut-elle tirer parti des données ?

![Python](https://img.shields.io/badge/Python-pandas%20%7C%20matplotlib-blue) ![Google Sheets](https://img.shields.io/badge/Google%20Sheets-vérifications-green)

> Capstone du **Google Data Analytics Professional Certificate**.
> Données : [FitBit Fitness Tracker Data](https://www.kaggle.com/datasets/arashnic/fitbit) (Kaggle, licence CC0 : domaine public).

**Structure du dépôt**

```
├── README.md      ← étude de cas complète
├── scripts/       ← scripts de visualisation
├── figures/       ← graphiques (PNG)
└── data/          ← instructions pour récupérer les données
```

> Étude de cas n° 2 : analyse des données d'objets connectés pour orienter la stratégie marketing de Bellabeat.
> Démarche suivie : **Ask → Prepare → Process → Analyze → Share → Act**.

---

## Contexte

Bellabeat est un fabricant high-tech de produits de santé destinés aux femmes. Cette étude analyse les données d'utilisateurs d'objets connectés (smart devices) pour comprendre comment ces appareils sont utilisés au quotidien. Les conclusions doivent aider l'équipe à orienter sa future stratégie marketing.

---

## 1. Ask : définir la question

### Problématique

Nous cherchons à **identifier des opportunités en dégageant des tendances dans les données**, afin d'**améliorer la stratégie marketing de l'un de nos produits**.

### Questions directrices

| Question | Réponse |
|---|---|
| Quel problème cherchons-nous à résoudre ? | Identifier des opportunités grâce aux tendances observées dans les données, pour améliorer la stratégie marketing de l'un de nos produits. |
| Comment ces tendances peuvent-elles s'appliquer aux clientes de Bellabeat ? | En exploitant des données utiles sur les utilisateurs d'autres objets connectés, nous pouvons prendre des décisions pertinentes pour nos propres clientes. |
| Comment ces tendances peuvent-elles orienter la stratégie marketing de Bellabeat ? | En fondant les décisions marketing sur les données plutôt que sur l'intuition. |
| Comment ces analyses peuvent-elles guider les décisions business ? | En analysant les données d'utilisateurs de produits du même type, et en identifiant des tendances dans leurs usages et leurs comportements. |

### Mission

- **Objectif business :** améliorer la stratégie marketing de l'un des produits Bellabeat.
- **Parties prenantes :** les cofondateurs et l'équipe d'analyse marketing.

---

## 2. Prepare : préparer les données

### 2.1 Source et organisation des données

- **Emplacement :** fichiers CSV issus de Kaggle.
- **Organisation :** chaque fichier CSV est structuré en lignes et en colonnes. Selon les fichiers, la granularité est le jour, l'heure, la minute ou la seconde.
- **Modèle conceptuel des données (MCD) :**

![Modèle conceptuel des données](figures/mcd.png)

### 2.2 Biais et crédibilité

Il s'agit de **données de troisième main (third-party)**, externes, structurées et **quantitatives**.

### 2.3 Vérification de l'intégrité des données

| # | Point de contrôle | Constat | Action |
|---|---|---|---|
| 1 | Les identifiants (`Id`) sont-ils uniques là où ils doivent l'être ? | Aucune remarque | — |
| 2 | Les dates sont-elles valides ? | Deux formats coexistent : `4/12/2016` (dates) et `4/12/2016 7:22:35 AM` (horodatages) | Normalisation au format date lors de la phase Process |
| 3 | Y a-t-il des valeurs manquantes ? | Uniquement dans `weightLogInfo_merged.csv` : la colonne `Fat` ne contient que 2 valeurs | Colonne non pertinente pour l'analyse |
| 4 | Les fréquences cardiaques sont-elles numériques ? | Aucune remarque | — |
| 5 | Les fréquences cardiaques sont-elles dans des plages plausibles ? | Entre 36 et 203 BPM | — |
| 6 | Les heures de sommeil peuvent-elles être négatives ? | Hors périmètre de l'analyse | — |
| 7 | Y a-t-il des doublons ? | Aucun doublon, mais `TotalDistance` et `TrackerDistance` sont presque identiques | Examen de l'écart entre les deux colonnes (cf. 2.4.4) |
| 8 | Chaque enregistrement d'activité correspond-il à une personne réelle ? | Aucune remarque | — |
| 9 | Les unités sont-elles cohérentes (BPM et non Hz, par exemple) ? | Aucune remarque | — |
| 10 | Existe-t-il des combinaisons impossibles ? | Aucune remarque | — |
| 11 | Y a-t-il des valeurs inattendues (« N/A », « unknown », « - », « error ») ? | `minuteMETs` : des valeurs à 0, ce qui n'a pas de sens. Il y a aussi plusieurs valeurs laissant croire à un non-port de l'appareil (ou problème de batterie) | Correction lors de la phase Process |

### 2.4 Détail des vérifications

#### 2.4.1 Inventaire des fichiers et formats de date

Tous les fichiers CSV ont d'abord été chargés pour inventorier leurs dimensions, leurs colonnes et leurs types (script A1).

Les colonnes de date ont ensuite été inspectées (script A2) :

| Fichier | Colonne | Exemple de valeur |
|---|---|---|
| `dailyActivity_merged.csv` | `ActivityDate` | `4/12/2016` |
| `heartrate_seconds_merged.csv` | `Time` | `4/12/2016 7:22:35 AM` |

La différence de format est normale, puisque la granularité diffère d'un fichier à l'autre. En revanche, ces colonnes sont stockées sous forme de texte : elles seront converties au format date lors de la phase Process.

#### 2.4.2 Valeurs manquantes

La méthode `isna()` de pandas a été appliquée à tous les fichiers (script A3). **Un seul fichier contient des valeurs manquantes :**

| Fichier | Colonne | Valeurs manquantes | % |
|---|---|---|---|
| `weightLogInfo_merged.csv` | `Fat` | 65 | 97,0 % |

La colonne `Fat` ne contient que 2 valeurs renseignées : elle n'est donc pas exploitable pour l'analyse.

#### 2.4.3 Fréquence cardiaque

Statistiques descriptives de `heartrate_seconds_merged.csv`, obtenues avec `describe()` (script A4) :

| Statistique | Valeur (BPM) |
|---|---|
| Nombre de mesures | 2 483 658 |
| Moyenne | 77,3 |
| Écart-type | 19,4 |
| Minimum | 36 |
| 1er quartile | 63 |
| Médiane | 73 |
| 3e quartile | 88 |
| Maximum | 203 |

**Les valeurs sont comprises entre 36 et 203 BPM.**

#### 2.4.4 Doublons : `TotalDistance` vs `TrackerDistance`

Ces deux colonnes semblaient contenir les mêmes données. Une comparaison ligne à ligne, faite dans Google Sheets (`=SI(D714=E714;"Identique";"DIFFÉRENT")`) puis avec pandas (script A5), montre qu'elles sont **presque identiques, mais pas tout à fait**. Extrait des écarts :

| Ligne | TotalDistance | TrackerDistance |
|---|---|---|
| 689 | 9,71 | 7,88 |
| 693 | 9,27 | 9,08 |
| 711 | 10,29 | 9,48 |
| 724 | 13,34 | 12,20 |
| 728 | 14,30 | 13,42 |

**Explication :** l'écart vient de la manière dont Fitbit mesure la distance (vérifié dans le manuel Fitbit). Une seule des deux colonnes sera conservée : `TotalDistance`.

#### 2.4.5 Volume de données par table

Pour éviter de travailler sur des données biaisées, le nombre d'utilisateurs distincts a été compté dans chaque table (script A6) :

| Fichier(s) | Utilisateurs distincts |
|---|---|
| `dailyActivity`, `dailyCalories`, `dailyIntensities`, `dailySteps` | 33 |
| `hourlyCalories`, `hourlyIntensities`, `hourlySteps` | 33 |
| `minuteCalories` / `minuteIntensities` / `minuteSteps` (Narrow et Wide), `minuteMETsNarrow` | 33 |
| `sleepDay_merged`, `minuteSleep_merged` | 24 |
| `heartrate_seconds_merged` | 14 |
| `weightLogInfo_merged` | 8 |

Les tables de poids, de sommeil et de fréquence cardiaque comptent **moins de 25 utilisateurs**. C'est trop peu pour fonder des décisions : elles sont écartées de l'analyse.

#### 2.4.6 Redondance entre tables

Dans Google Sheets, les fichiers `dailyXX_merged.csv` ont été comparés à `dailyActivity_merged.csv` (`=SI(C2=dailySteps_merged!C2;"Identique";"DIFFÉRENT")`).

**Résultat : les données sont identiques.** `dailyActivity_merged.csv` contient déjà toutes les informations des autres fichiers journaliers.

Les fichiers plus volumineux (heure, minute) ont été examinés avec pandas et NumPy.

#### 2.4.7 METs

Des valeurs de METs à 0 ont été relevées. Une valeur nulle est impossible : une personne au repos a au minimum 1 MET. De plus, la documentation Fitabase indique que **toutes les valeurs de METs exportées sont multipliées par 10** (10 = 1,0 MET ; 38 = 3,8 METs). Il faudra donc les diviser par 10.

### 2.5 Synthèse des décisions

| # | Constat | Décision |
|---|---|---|
| 02 | Formats de date différents (`4/12/2016` et `4/12/2016 7:22:35 AM`) | Conversion au format date lors de la phase Process |
| 03 | `TotalDistance` et `TrackerDistance` sont presque identiques ; l'écart vient de la méthode de mesure de Fitbit | Ne conserver que `TotalDistance` |
| 04 | `weightLogInfo`, `sleepDay`, `minuteSleep` et `heartrate_seconds` comptent moins de 25 utilisateurs | Tables non utilisées. Si besoin, chercher d'autres jeux de données sur le poids, le sommeil ou la fréquence cardiaque |
| 05 | `dailyActivity` contient toutes les données des autres fichiers `dailyXX_merged` | Ne conserver que `dailyActivity_merged.csv` |
| 06 | Valeurs de METs à 0, incohérentes | Correction de ces valeurs |
| 07 | Valeurs de METs multipliées par 10 à l'export Fitabase | Division par 10 pour obtenir les vraies valeurs |

### 2.6 Stockage

- Les fichiers CSV de taille réduite (`dailyXX_merged.csv`) ont été chargés dans **Google Sheets**.
- Tous les fichiers CSV utilisés sont traités en **Python (pandas / NumPy)**.

---

## 3. Process : nettoyer les données

### Choix de l'outil

Le traitement est réalisé en **Python avec pandas**. Les fichiers CSV comptent un grand nombre de lignes et de colonnes (plus de 1,3 million de lignes pour les tables à la minute) : un tableur n'est pas adapté à ce volume. Python suffisait pour des fichiers CSV sans base de données..

### 3.1 Suppression des lignes vides

Les lignes entièrement vides ont été recherchées et supprimées avec `dropna(how="all")` (script B1). **Aucune n'a été trouvée.**

### 3.2 Conversion des dates

Les colonnes de date, stockées sous forme de texte, ont été converties au type `datetime` (scripts B2 et B3) :

| Fichiers | Colonne | Avant | Après |
|---|---|---|---|
| `dailyActivity_merged.csv` | `ActivityDate` | `4/12/2016` | `2016-04-12` |
| Fichiers horaires et `minuteWide` | `ActivityHour` | `4/12/2016 1:00:00 AM` | `2016-04-12 01:00:00` |
| Fichiers `minuteNarrow` | `ActivityMinute` | `4/12/2016 12:00:00 AM` | `2016-04-12 00:00:00` |

### 3.3 Suppression de `TrackerDistance`

La colonne `TrackerDistance` a été supprimée de `dailyActivity_merged.csv` (script B4). `TotalDistance` fournit une donnée plus précise, d'après le manuel Fitbit.

### 3.4 Correction des METs à 0

Recherche des valeurs nulles dans `minuteMETsNarrow_merged.csv` (script B5). Sept lignes sont concernées : **57419, 279059, 713039, 1065794, 1075885, 1076219 et 1105799**.

Chaque valeur de remplacement a été choisie en fonction des données qui l'entourent :

| Lignes | Nouvelle valeur (avant division par 10) |
|---|---|
| 57419, 279059, 713039, 1076219, 1105799 | 10 |
| 1065794 | 19 |
| 1075885 | 14 |

### 3.5 Conversion des METs en valeurs réelles

Toutes les valeurs de la colonne `METs` ont été divisées par 10 (script B6).

### Bilan du nettoyage

Les données sont désormais propres. Les tables au format « Wide » ne seront pas utilisées dans l'analyse, mais elles sont conservées au cas où elles deviendraient utiles.

---

## 4. Analyze : analyser les données

### 4.1 Consolidation des tables

Les fichiers à la minute (format « Narrow ») d'une part, et les fichiers horaires d'autre part, ont été fusionnés par jointure externe sur le couple `Id` + horodatage (scripts C1 et C2).

| Table créée | Fichiers sources | Lignes | Colonnes |
|---|---|---|---|
| `minuteActivity_aggregated.csv` | `minuteCaloriesNarrow`, `minuteIntensitiesNarrow`, `minuteStepsNarrow`, `minuteMETsNarrow` (1 325 580 lignes chacun) | 1 325 580 | `Id`, `ActivityMinute`, `Calories`, `Intensity`, `Steps`, `METs` |
| `hourlyActivity_aggregated.csv` | `hourlyCalories`, `hourlyIntensities`, `hourlySteps` (22 099 lignes chacun), `hourlyMETs` (22 093 lignes) | 22 099 | `Id`, `ActivityHour`, `Calories`, `TotalIntensity`, `AverageIntensity`, `StepTotal`, `METs` |

**L'analyse repose donc sur trois tables :**
- `dailyActivity_merged.csv` : données par jour ;
- `hourlyActivity_aggregated.csv` : données par heure ;
- `minuteActivity_aggregated.csv` : données par minute.

### 4.2 Volume de données par utilisateur

Le nombre d'enregistrements par utilisateur a été contrôlé dans les trois tables (script C3).

La plupart des utilisateurs disposent de 26 à 31 jours de données. **L'utilisateur `4057192912` n'en compte que 4** (88 heures, 5 280 minutes), ce qui est largement en dessous des autres. Il a donc été retiré de l'analyse (script C4) :

| Table | Lignes supprimées |
|---|---|
| `dailyActivity_merged.csv` | 4 |
| `hourlyActivity_aggregated.csv` | 88 |
| `minuteActivity_aggregated.csv` | 5 280 |

Ce retrait permet de comparer les moyennes des utilisateurs sur des bases équivalentes.

### 4.3 Valeurs extrêmes et journées non exploitables

**Top 10 des journées avec le plus de pas** (script C5) :

| Id | Pas | Date |
|---|---|---|
| 1624580081 | 36 019 | 01/05/2016 |
| 8877689391 | 29 326 | 16/04/2016 |
| 8877689391 | 27 745 | 30/04/2016 |
| 8877689391 | 23 629 | 27/04/2016 |
| 8877689391 | 23 186 | 12/04/2016 |
| 8053475328 | 22 988 | 24/04/2016 |
| 4388161847 | 22 770 | 07/05/2016 |
| 8053475328 | 22 359 | 23/04/2016 |
| 2347167796 | 22 244 | 16/04/2016 |
| 8053475328 | 22 026 | 08/05/2016 |

**Top 10 des journées avec le plus de minutes sédentaires :** toutes affichent **1 440 minutes**, soit 24 h sur 24.

| Id | Minutes sédentaires | Date |
|---|---|---|
| 1503960366 | 1 440 | 12/05/2016 |
| 1844505072 | 1 440 | 24/04, 25/04, 26/04, 02/05, 07/05, 08/05, 09/05, 10/05, 11/05/2016 |

Ce sont des **jours où l'appareil n'a pas été porté**. Ces journées ont été supprimées, ainsi que d'autres journées non représentatives (script C6) :

| Filtre | Raison | Lignes supprimées | Lignes restantes |
|---|---|---|---|
| `SedentaryMinutes = 1440` | Appareil non porté | 78 | 858 |
| `TotalSteps < 100` | Batterie probablement déchargée | 15 | 843 |
| `Calories < 1000` | Journée non représentative | 3 | 840 |

### 4.4 Report du nettoyage sur les tables horaire et minute

Les journées supprimées de la table journalière ont également été retirées des deux autres tables. Seuls les couples `Id` + jour présents dans les trois tables ont été conservés (script C7).

| Table | Avant | Après |
|---|---|---|
| `dailyActivity_merged.csv` | 840 | 840 |
| `hourlyActivity_aggregated.csv` | 22 011 | 19 959 |
| `minuteActivity_aggregated.csv` | 1 320 300 | 1 197 180 |

**Périmètre final : 32 utilisateurs, 840 couples utilisateur-jour.**

### 4.5 Nombre de pas par jour de la semaine

Nombre moyen de pas par jour (script C8) :

| Jour | Pas moyens |
|---|---|
| Lundi | 8 566,42 |
| Mardi | 9 020,36 |
| Mercredi | 8 384,97 |
| Jeudi | 8 322,56 |
| Vendredi | 7 986,38 |
| Samedi | 9 059,63 |
| Dimanche | 7 811,85 |

### 4.6 Nombre de pas par jour et par heure

Top 20 des créneaux jour × heure, classés par nombre moyen de pas (script C9) :

| Jour | Heure | Pas moyens |
|---|---|---|
| Samedi | 13 h | 857,9 |
| Mercredi | 18 h | 824,3 |
| Mercredi | 17 h | 822,4 |
| Samedi | 14 h | 768,2 |
| Lundi | 18 h | 741,0 |
| Mardi | 12 h | 740,3 |
| Samedi | 12 h | 739,2 |
| Mardi | 18 h | 713,7 |
| Samedi | 11 h | 701,9 |
| Lundi | 19 h | 700,0 |
| Mardi | 17 h | 693,2 |
| Mercredi | 19 h | 670,5 |
| Vendredi | 19 h | 659,9 |
| Dimanche | 10 h | 659,2 |
| Dimanche | 14 h | 653,8 |
| Mardi | 19 h | 649,8 |
| Vendredi | 18 h | 641,0 |
| Samedi | 19 h | 638,2 |
| Jeudi | 19 h | 634,2 |
| Mardi | 13 h | 620,9 |

L'objectif n'étant pas de comparer les utilisateurs entre eux, l'analyse se concentre sur **les jours et les heures d'activité**. Des visualisations ont été produites pour mieux comprendre ces rythmes.

---

## 5. Share : visualiser et partager

### 5.1 Profil d'activité général

Premières visualisations des rythmes d'activité (script D1, sorties dans `data/visualizations/`) :

![Profil moyen des pas selon l'heure](figures/visualizations/01_steps_by_hour.png)

![Calories moyennes selon l'heure](figures/visualizations/02_calories_by_hour.png)

![Intensité moyenne selon l'heure](figures/visualizations/03_intensity_by_hour.png)

![Activité moyenne, jour × heure](figures/visualizations/04_heatmap_day_hour.png)

![Profil moyen de l'activité sur 24 heures (minute par minute)](figures/visualizations/5_minute_profile.png)

![Top 20 des périodes les plus actives](figures/visualizations/6_top_day_hour.png)

**Constat :** ces graphiques font apparaître les **heures d'activité et les heures creuses**, ainsi que les **jours privilégiés**. Ces rythmes sont approfondis dans la section suivante.

### 5.2 Approfondissement : jours, heures et utilisateurs

Visualisations complémentaires et synthèse chiffrée (script D2, sorties dans `data/visualizations_deep_dive/`) :

![Heatmap du nombre moyen de pas par jour et par heure](figures/visualizations_deep_dive/01_heatmap_steps.png)

![Heatmap des calories moyennes par jour et par heure](figures/visualizations_deep_dive/02_heatmap_calories.png)

![Heatmap de l'intensité moyenne par jour et par heure](figures/visualizations_deep_dive/03_heatmap_intensity.png)

![Heatmap des METs moyens par jour et par heure](figures/visualizations_deep_dive/04_heatmap_mets.png)

![Profil horaire des pas, semaine vs week-end](figures/visualizations_deep_dive/05_weekday_vs_weekend.png)

![Heatmap de l'activité horaire de chaque utilisateur](figures/visualizations_deep_dive/06_heatmap_users_hours.png)

![Distribution de l'heure du pic d'activité](figures/visualizations_deep_dive/07_peak_hour_distribution.png)

![Profils horaires des utilisateurs les moins et les plus actifs](figures/visualizations_deep_dive/08_user_profiles.png)

**Résultats chiffrés :**

| Indicateur | Résultat |
|---|---|
| Heure avec le plus de pas en moyenne | 18 h (660,5 pas) |
| Heure avec le plus de calories en moyenne | 18 h |
| Heure avec la plus forte intensité moyenne | 18 h |
| Moyenne horaire de pas en semaine | 353,55 |
| Moyenne horaire de pas le week-end | 352,91 |

**Heure du pic d'activité de chaque utilisateur :**

| Heure du pic | Utilisateurs (pas moyens à l'heure du pic) |
|---|---|
| 06 h | 4388161847 (1 100,7) · 5577150313 (1 008,1) |
| 08 h | 2873212765 (1 061,8) · 2347167796 (1 432,5) · 7007744171 (3 080,0) · 8378563200 (1 529,1) |
| 09 h | 6290855005 (733,0) · 2022484408 (1 916,2) |
| 10 h | 3372868164 (819,0) · 1624580081 (659,5) · 4319703577 (1 073,9) · 6962181067 (1 429,9) |
| 11 h | 1844505072 (438,6) · 1927972279 (260,6) · 8253242879 (1 593,8) |
| 12 h | 6775888955 (494,6) · 8877689391 (2 110,6) · 4702921684 (805,1) |
| 13 h | 6117666160 (738,9) · 7086361926 (2 378,5) |
| 15 h | 2026352035 (493,3) · 2320127002 (338,2) · 8583815059 (1 184,6) |
| 16 h | 4020332650 (624,8) · 4558609924 (882,1) |
| 17 h | 5553957443 (1 291,4) |
| 18 h | 1503960366 (1 556,1) · 4445114986 (796,6) · 8792009665 (289,0) |
| 19 h | 1644430081 (1 199,7) · 8053475328 (3 466,9) |
| 22 h | 3977333714 (1 196,0) |

**Constat :** les heures et les jours d'activité **varient fortement d'un utilisateur à l'autre**. En moyenne, le pic se situe à 18 h, mais les pics individuels s'étalent de 6 h à 22 h, et seuls 3 utilisateurs ont réellement leur pic à 18 h. Pour mieux comprendre ces différences, les utilisateurs ont été regroupés selon l'heure de leur pic d'activité.

### 5.3 Segmentation des utilisateurs selon leur rythme

Chaque utilisateur est classé selon l'heure de son pic d'activité (script D3, sorties dans `data/activity_segments/`) :

| Segment | Heure du pic |
|---|---|
| Early Movers | 5 h – 9 h |
| Midday Movers | 10 h – 13 h |
| Afternoon Movers | 14 h – 16 h |
| Evening Movers | 17 h – 20 h |
| Late Movers | 21 h – 4 h |

**Taille des segments :**

| Segment | Utilisateurs |
|---|---|
| Midday Movers | 12 |
| Early Movers | 8 |
| Evening Movers | 6 |
| Afternoon Movers | 5 |
| Late Movers | 1 |

![Répartition des utilisateurs par rythme d'activité](figures/activity_segments/01_segment_sizes.png)

**Profil des segments :**

| Segment | Heure de pic moyenne | Pas au pic (moy.) | Pas/h en semaine | Pas/h le week-end | Variation week-end vs semaine |
|---|---|---|---|---|---|
| Early Movers | 7,75 | 1 482,67 | 404,54 | 394,72 | -2,43 % |
| Midday Movers | 11,25 | 1 066,92 | 310,25 | 335,73 | +8,21 % |
| Afternoon Movers | 15,40 | 704,60 | 251,54 | 242,78 | −3,48 % |
| Evening Movers | 18,17 | 1 433,29 | 362,67 | 339,37 | −6,43 % |
| Late Movers | 22,00 | 1 196,03 | 455,18 | 514,74 | +13,08 % |

**Composition des segments :**

| Segment | Utilisateurs (heure du pic, pas au pic) |
|---|---|
| Early Movers | 4388161847 (6 h, 1 101) · 5577150313 (6 h, 1 008) · 2873212765 (8 h, 1 062) · 2347167796 (8 h, 1 432) · 8378563200 (8 h, 1 529) · 7007744171 (8 h, 3 080) · 2022484408 (9 h, 1 916) · 6290855005 (9 h, 733) |
| Midday Movers | 1624580081 (10 h, 660) · 3372868164 (10 h, 819) · 4319703577 (10 h, 1 074) · 6962181067 (10 h, 1 430) · 1927972279 (11 h, 261) · 1844505072 (11 h, 439) · 8253242879 (11 h, 1 594) · 4702921684 (12 h, 805) · 8877689391 (12 h, 2 111) · 6775888955 (12 h, 495) · 6117666160 (13 h, 739) · 7086361926 (13 h, 2 378) |
| Afternoon Movers | 2026352035 (15 h, 493) · 2320127002 (15 h, 338) · 8583815059 (15 h, 1 185) · 4020332650 (16 h, 625) · 4558609924 (16 h, 882) |
| Evening Movers | 5553957443 (17 h, 1 291) · 1503960366 (18 h, 1 556) · 4445114986 (18 h, 797) · 8792009665 (18 h, 289) · 1644430081 (19 h, 1 200) · 8053475328 (19 h, 3 467) |
| Late Movers | 3977333714 (22 h, 1 196) |

![Profils horaires moyens des différents segments](figures/activity_segments/02_segment_hourly_profiles.png)

**Constat :** chaque segment a un fonctionnement **totalement différent**. Les profils horaires présentent chacun un pic d'activité à un moment distinct de la journée : le matin, la mi-journée, l'après-midi, le soir ou tard le soir.

![Heatmap de l'activité horaire par segment](figures/activity_segments/03_segment_heatmap.png)

![Activité en semaine et le week-end selon le segment](figures/activity_segments/05_segment_weekend.png)

**Constat :** Constat : deux segments sont nettement plus actifs le week-end qu'en semaine. Les Midday Movers (12 utilisateurs) passent de 310 à 336 pas par heure. Les Late Movers passent de 455 à 515, mais ce segment ne compte qu'un seul utilisateur et ne permet aucune conclusion.

---

## 6. Act : recommandations

#### Le produit :

**Application Bellabeat :** L’application Bellabeat fournit aux utilisateurs des données de santé liées à leur activité physique, leur sommeil, leur niveau de stress, leur cycle menstruel et leurs habitudes de pleine conscience. Ces données peuvent les aider à mieux comprendre leurs habitudes actuelles et à prendre des décisions favorables à leur santé. L’application Bellabeat se connecte à leur gamme de produits intelligents dédiés au bien-être.

#### La stratégie :

L’objectif serait d’approfondir la personnalisation de l’application en s’appuyant sur les habitudes et comportements observés chez les utilisateurs. L’analyse montre en effet que des recommandations ou objectifs génériques ne sont pas nécessairement adaptés à l’ensemble des profils et peuvent ainsi présenter une pertinence variable selon les utilisateurs.

Dans cette perspective, la segmentation identifiée dans la dernière partie de l’analyse pourrait être intégrée directement à l’expérience utilisateur. Après quelques semaines d’utilisation, chaque utilisateur pourrait être automatiquement associé à un segment en fonction de ses habitudes et de son niveau d’activité. Des objectifs et recommandations spécifiques pourraient alors être définis pour chaque profil, afin de mieux correspondre à ses comportements.

Par exemple, l'analyse montre que les Midday Movers, le segment le plus représenté (12 utilisateurs sur 32), sont plus actifs le week-end qu'en semaine : environ 336 pas par heure contre 310. Pour ce type de profil, l'application pourrait proposer davantage d'incitations à l'activité durant les jours de semaine, par exemple un rappel avant la pause de midi, et des objectifs plus ambitieux ou des défis supplémentaires le week-end.

La mise en place d’une telle segmentation permettrait ainsi d’aller au-delà de recommandations standardisées en proposant une personnalisation fondée sur les comportements réels des utilisateurs. Cette approche pourrait contribuer à améliorer la pertinence des recommandations, à renforcer l’adéquation des objectifs proposés aux différents profils et, plus largement, à favoriser une expérience utilisateur davantage adaptée aux habitudes individuelles.

Limites. Ces conclusions reposent sur 32 utilisateurs suivis pendant environ un mois (avril–mai 2016), sans information démographique, et qui ne sont pas des clientes Bellabeat. Les segments comptent entre 1 et 12 utilisateurs : ils indiquent des pistes à tester, pas des résultats généralisables. Une validation sur les données propres à Bellabeat serait nécessaire avant tout déploiement.

---

## Annexe : scripts

Les trois scripts de visualisation (D1, D2 et D3) sont longs. Ils sont fournis dans des fichiers séparés :

- [`scripts/visualisations.py`](scripts/visualisations.py) (D1)
- [`scripts/visualisations_deep_dive.py`](scripts/visualisations_deep_dive.py) (D2)
- [`scripts/activity_segments.py`](scripts/activity_segments.py) (D3)

### Prepare

**A1. Inventaire des fichiers CSV**

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")
csv_files = list(DATA_FOLDER.glob("*.csv"))

print(f"Found {len(csv_files)} CSV files")

for file in csv_files:
    print("\n" + "=" * 50)
    print(f"FILE: {file.name}")
    print("=" * 50)

    df = pd.read_csv(file)

    print(f"\nShape: {df.shape[0]} rows × {df.shape[1]} columns")
    print("\nColumns and types:")
    for col, dtype in df.dtypes.items():
        print(f"- {col}: {dtype}")
```

**A2. Inspection des formats de date** (même script pour `heartrate_seconds_merged.csv`, colonne `Time`)

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")
file = DATA_FOLDER / "dailyActivity_merged.csv"

df = pd.read_csv(file)

print("Colonnes :")
print(df.columns.tolist())

print("\nValeurs de ActivityDate :")
print(df["ActivityDate"].head(20).to_string(index=False))

print("\nType de ActivityDate :")
print(df["ActivityDate"].dtype)
```

**A3. Valeurs manquantes**

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")
csv_files = list(DATA_FOLDER.glob("*.csv"))

for file in csv_files:
    print("\n" + "=" * 60)
    print(f"FILE: {file.name}")
    print("=" * 60)

    df = pd.read_csv(file)

    missing = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_percent": df.isna().mean() * 100
    })

    missing = missing[missing["missing_count"] > 0]
    print(missing)
```

**A4. Statistiques descriptives**

```python
import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    print("Usage: python name_script.py <fichier.csv>")
    sys.exit(1)

file = Path(sys.argv[1])

if not file.exists():
    print(f"Erreur : fichier introuvable : {file}")
    sys.exit(1)

if file.suffix.lower() != ".csv":
    print(f"Erreur : le fichier doit être un CSV : {file}")
    sys.exit(1)

df = pd.read_csv(file)

print(f"FILE: {file}")
print()
print(df.describe())
```

**A5. Comparaison `TotalDistance` / `TrackerDistance`**

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")
file = DATA_FOLDER / "dailyActivity_merged.csv"

df = pd.read_csv(file)

differences = df.loc[
    df["TotalDistance"] != df["TrackerDistance"],
    ["TotalDistance", "TrackerDistance"]
]

print(differences)
```

**A6. Nombre d'utilisateurs distincts par table**

```python
import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    print("Usage: python unique_ids.py <dossier>")
    sys.exit(1)

folder = Path(sys.argv[1])

if not folder.exists():
    print(f"Erreur : dossier introuvable : {folder}")
    sys.exit(1)

if not folder.is_dir():
    print(f"Erreur : ce n'est pas un dossier : {folder}")
    sys.exit(1)

files = sorted(folder.glob("*.csv"))

if not files:
    print("Aucun fichier CSV trouvé.")
    sys.exit(0)

for file in files:
    print("=" * 60)
    print(f"FILE: {file.name}")
    print("=" * 60)

    df = pd.read_csv(file)

    if "Id" not in df.columns:
        print("Colonne 'Id' absente.")
        print()
        continue

    number_of_ids = df["Id"].nunique()
    print(f"Number of unique Id: {number_of_ids}")
    print()
```

### Process

**B1. Suppression des lignes vides**

```python
import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    print("Usage: python drop_empty.py <fichier.csv>")
    sys.exit(1)

file = Path(sys.argv[1])

if not file.exists():
    print(f"Erreur : fichier introuvable : {file}")
    sys.exit(1)

df = pd.read_csv(file)

print(f"FILE: {file}")
print(f"Before: {df.shape}")

df = df.dropna(how="all")

print(f"After: {df.shape}")
```

**B2. Conversion de `ActivityDate`**

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")
file = DATA_FOLDER / "dailyActivity_merged.csv"

df = pd.read_csv(file)

# Avant conversion
print("Avant :")
print(df["ActivityDate"].head(10))
print(df["ActivityDate"].dtype)

# Conversion
df["ActivityDate"] = pd.to_datetime(
    df["ActivityDate"],
    format="%m/%d/%Y"
)

# Après conversion
print("\nAprès :")
print(df["ActivityDate"].head(10))
print(df["ActivityDate"].dtype)

# Mettre à jour le CSV original
df.to_csv(file, index=False)
print(f"CSV updated: {file}")
```

**B3. Conversion des horodatages** (appliqué aux fichiers horaires et `minuteWide` avec `ActivityHour`, et aux fichiers `minuteNarrow` avec `ActivityMinute`)

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")
file = DATA_FOLDER / "hourlyCalories_merged.csv"

df = pd.read_csv(file)

print("Avant :")
print(df["ActivityHour"].head())
print(df["ActivityHour"].dtype)

df["ActivityHour"] = pd.to_datetime(
    df["ActivityHour"],
    format="%m/%d/%Y %I:%M:%S %p"
)

print("\nAprès :")
print(df["ActivityHour"].head())
print(df["ActivityHour"].dtype)

# Mettre à jour le CSV original
df.to_csv(file, index=False)
print(f"CSV updated: {file}")
```

**B4. Suppression de `TrackerDistance`**

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")
file = DATA_FOLDER / "dailyActivity_merged.csv"

df = pd.read_csv(file)

print("Avant :")
print(df.columns.tolist())

# Nettoyer les noms de colonnes
df.columns = df.columns.str.strip()

# Supprimer la colonne
df.drop(columns=["TrackerDistance"], inplace=True)

print("\nAprès :")
print(df.columns.tolist())

print("\nInfo :")
df.info()

# Mettre à jour le CSV original
df.to_csv(file, index=False)
print(f"CSV updated: {file}")
```

**B5. Recherche et correction des METs à 0**

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")
file = DATA_FOLDER / "minuteMETsNarrow_merged.csv"

df = pd.read_csv(file)

# Repérer les valeurs nulles
print(df.index[df["METs"] == 0].tolist())

# Remplacer par 10 (les lignes 1065794 et 1075885 reçoivent 19 et 14)
df.loc[[57419, 279059, 713039, 1076219, 1105799], "METs"] = 10.0

# Mettre à jour le CSV
df.to_csv(file, index=False)
print(f"CSV updated: {file}")
```

**B6. Division des METs par 10**

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")
file = DATA_FOLDER / "minuteMETsNarrow_merged.csv"

df = pd.read_csv(file)

# Diviser toutes les valeurs de METs par 10
df["METs"] = df["METs"] / 10

# Mettre à jour le CSV original
df.to_csv(file, index=False)
print(f"CSV updated: {file}")
```

### Analyze

**C1. Fusion des tables à la minute** (C2 est identique pour les tables horaires, avec `ActivityHour` et export vers `hourlyActivity_aggregated.csv`)

```python
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path("data")

calories_file = DATA_FOLDER / "minuteCaloriesNarrow_merged.csv"
intensities_file = DATA_FOLDER / "minuteIntensitiesNarrow_merged.csv"
steps_file = DATA_FOLDER / "minuteStepsNarrow_merged.csv"
mets_file = DATA_FOLDER / "minuteMETsNarrow_merged.csv"

# 1. Charger les fichiers
calories = pd.read_csv(calories_file)
intensities = pd.read_csv(intensities_file)
steps = pd.read_csv(steps_file)
mets = pd.read_csv(mets_file)

# 2. Fusionner Calories + Intensities
df = pd.merge(calories, intensities, on=["Id", "ActivityMinute"], how="outer")

# 3. Ajouter Steps
df = pd.merge(df, steps, on=["Id", "ActivityMinute"], how="outer")

# 4. Ajouter METs
df = pd.merge(df, mets, on=["Id", "ActivityMinute"], how="outer")

# 5. Trier
df = df.sort_values(["Id", "ActivityMinute"])

# 6. Vérification
print(df.head())
print(df.shape)
print(df.columns.tolist())

# 7. Export
output_file = DATA_FOLDER / "minuteActivity_aggregated.csv"
df.to_csv(output_file, index=False)
print(f"\nSaved: {output_file}")
```

**C3. Nombre d'enregistrements par utilisateur**

```python
import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    print("Usage: python groupby_id.py <dossier>")
    sys.exit(1)

folder = Path(sys.argv[1])

if not folder.is_dir():
    print(f"Erreur : dossier introuvable : {folder}")
    sys.exit(1)

for file in sorted(folder.glob("*.csv")):
    print("=" * 70)
    print(f"FILE: {file.name}")
    print("=" * 70)

    df = pd.read_csv(file)

    if "Id" not in df.columns:
        print("Colonne Id absente.\n")
        continue

    print(df.groupby("Id").size().to_string())
    print()
```

**C4. Retrait d'un utilisateur**

```python
import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    print("Usage: python remove_id.py <dossier>")
    sys.exit(1)

folder = Path(sys.argv[1])

if not folder.is_dir():
    print(f"Erreur : dossier introuvable : {folder}")
    sys.exit(1)

target_id = 4057192912

for file in sorted(folder.glob("*.csv")):
    df = pd.read_csv(file)

    if "Id" not in df.columns:
        continue

    before = len(df)
    df = df[df["Id"] != target_id]
    removed = before - len(df)

    if removed > 0:
        df.to_csv(file, index=False)
        print(f"{file.name}: {removed:,} lignes supprimées")
```

**C5. Top 10 des valeurs** (même principe pour `SedentaryMinutes`)

```python
import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    print("Usage: python top_values.py <dossier>")
    sys.exit(1)

folder = Path(sys.argv[1])

if not folder.is_dir():
    print(f"Erreur : dossier introuvable : {folder}")
    sys.exit(1)

for file in sorted(folder.glob("*.csv")):
    print("=" * 70)
    print(f"FILE: {file.name}")
    print("=" * 70)

    df = pd.read_csv(file)

    if "TotalSteps" not in df.columns:
        print("Colonne TotalSteps absente.\n")
        continue

    print(
        df.nlargest(10, "TotalSteps")[
            ["Id", "TotalSteps", "ActivityDate"]
        ].to_string(index=False)
    )
    print()
```

**C6. Filtrage des journées** (même structure pour `TotalSteps >= 100` et `Calories >= 1000`)

```python
import pandas as pd

file = "data/dailyActivity_merged.csv"

df = pd.read_csv(file)

# Nombre de lignes avant
before = len(df)

# Supprimer les lignes avec SedentaryMinutes = 1440
df = df[df["SedentaryMinutes"] != 1440]

# Nombre de lignes supprimées
removed = before - len(df)

# Sauvegarder
df.to_csv(file, index=False)

print(f"{removed} lignes supprimées.")
print(f"{len(df)} lignes restantes.")
```

**C7. Conservation des jours communs aux trois tables**

```python
import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    print("Usage: python filter_common_days.py <dossier>")
    sys.exit(1)

folder = Path(sys.argv[1])

if not folder.is_dir():
    print(f"Erreur : dossier introuvable : {folder}")
    sys.exit(1)

files = [
    folder / "dailyActivity_merged.csv",
    folder / "hourlyActivity_aggregated.csv",
    folder / "minuteActivity_aggregated.csv",
]

dfs = {}

for file in files:
    if not file.exists():
        print(f"Fichier introuvable : {file}")
        sys.exit(1)

    df = pd.read_csv(file)

    # Trouver la colonne de date
    if "ActivityDate" in df.columns:
        date_column = "ActivityDate"
    elif "ActivityMinute" in df.columns:
        date_column = "ActivityMinute"
    elif "ActivityHour" in df.columns:
        date_column = "ActivityHour"
    else:
        print(f"Aucune colonne de date trouvée dans {file.name}")
        sys.exit(1)

    # Convertir en datetime puis garder uniquement le jour
    df["_Day"] = pd.to_datetime(df[date_column], errors="coerce").dt.date
    dfs[file] = df

# Trouver les couples Id + jour présents dans les 3 fichiers
common = None

for df in dfs.values():
    keys = df[["Id", "_Day"]].drop_duplicates()
    if common is None:
        common = keys
    else:
        common = common.merge(keys, on=["Id", "_Day"], how="inner")

print(f"Nombre de couples Id + jour communs : {len(common)}")

# Filtrer les 3 fichiers
for file, df in dfs.items():
    before = len(df)
    df = df.merge(common, on=["Id", "_Day"], how="inner")

    # Supprimer la colonne temporaire
    df = df.drop(columns=["_Day"])

    # Sauvegarder
    df.to_csv(file, index=False)
    print(f"{file.name}: {before:,} → {len(df):,} lignes")
```

**C8. Pas moyens par jour de la semaine**

```python
import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    print("Usage: python by_weekday.py <dossier>")
    sys.exit(1)

folder = Path(sys.argv[1])

if not folder.is_dir():
    print(f"Erreur : dossier introuvable : {folder}")
    sys.exit(1)

for file in sorted(folder.glob("*.csv")):
    df = pd.read_csv(file)

    if "ActivityDate" not in df.columns:
        continue

    df["ActivityDate"] = pd.to_datetime(df["ActivityDate"], errors="coerce")

    if "TotalSteps" not in df.columns:
        continue

    df["DayOfWeek"] = df["ActivityDate"].dt.day_name()

    result = df.groupby("DayOfWeek")["TotalSteps"].mean().round(2)

    print("=" * 70)
    print(file.name)
    print("=" * 70)
    print(result)
    print()
```

**C9. Pas moyens par jour et par heure**

```python
import pandas as pd

file = "data/hourlyActivity_aggregated.csv"

df = pd.read_csv(file)
df["ActivityHour"] = pd.to_datetime(df["ActivityHour"])

# Jour de la semaine et heure
df["DayOfWeek"] = df["ActivityHour"].dt.day_name()
df["Hour"] = df["ActivityHour"].dt.hour

# Moyenne des pas par jour de la semaine + heure
result = (
    df.groupby(["DayOfWeek", "Hour"])["StepTotal"]
    .mean()
    .reset_index()
)

# Ordonner les jours
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
result["DayOfWeek"] = pd.Categorical(result["DayOfWeek"], categories=days, ordered=True)

# Trier par moyenne décroissante
result = result.sort_values("StepTotal", ascending=False)

print(result.head(20).to_string(index=False))
```
