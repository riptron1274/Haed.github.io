import os
import numpy as np
import pandas as pd
from datetime import date, timedelta
import csv
# =========================
# CONFIG
# =========================
SEED = 42
NUM_USERS = 25
DAYS = 180
START_DATE = date(2025, 1, 1)

WORKOUT_CATALOG_CSV = "data/cleaned/workout_catalog.csv"
FOOD_CATALOG_CSV = "data/cleaned/food_catalog.csv"
OUTPUT_DIR = "out_csv"

# Phase calorie adjustment
PHASE_CAL_ADJ = {
    "intense_cut": -0.25,
    "cut": -0.15,
    "maintain": 0.00,
    "bulk": 0.10,
    "intense_bulk": 0.20,
}


PHASE_TRAIN_DAYS = {
    "intense_cut": 4,
    "cut": 4,
    "maintain": 5,
    "bulk": 5,
    "intense_bulk": 6,
}


SPLITS = {
    "PPL": ["Push", "Pull", "Legs"],
    "UL": ["Upper", "Lower"],
    "BRO": ["Chest", "Back", "Shoulders", "Arms", "Legs"],
}


SESSION_MUSCLES = {
    "Push": ["chest", "shoulders", "triceps"],
    "Pull": ["back", "biceps"],
    "Legs": ["quads", "hamstrings", "glutes", "calves"],
    "Upper": ["chest", "back", "shoulders", "biceps", "triceps"],
    "Lower": ["quads", "hamstrings", "glutes", "calves"],
    "Chest": ["chest"],
    "Back": ["back"],
    "Shoulders": ["shoulders"],
    "Arms": ["biceps", "triceps"],
}

DIET_PREFS = ["vegetarian", "carnivore", "none"]
PHASES = ["intense_bulk", "bulk", "maintain", "cut", "intense_cut"]

MEAL_NAMES = ["Breakfast", "Lunch", "Dinner", "Snack"]
MEAL_P = [0.25, 0.30, 0.30, 0.15]


# =========================
# PHASE SAMPLING
# =========================
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def softmax(x):
    x = np.array(x, dtype=float)
    x = x - np.max(x)
    ex = np.exp(x)
    return ex / ex.sum()

def sample_phase(height_cm, weight_kg, bodyfat_pct, training_age_yrs, rng=np.random):
    """Sample goal phase with probabilities influenced by BF% + BMI + training age."""
    h_m = height_cm / 100.0
    bmi = weight_kg / (h_m * h_m)

    ta = np.clip(training_age_yrs / 8.0, 0, 1)

    cut_score = sigmoid(
        0.45 * (bodyfat_pct - 18.0) +
        0.25 * (bmi - 27.0)
    )

    logits = {
        "intense_cut":  2.8 * cut_score + 0.2 * (1 - ta),
        "cut":          2.0 * cut_score,
        "maintain":     1.2 - 3.2 * abs(cut_score - 0.5),
        "bulk":         1.7 * (1 - cut_score) * (0.5 + 0.5 * ta),
        "intense_bulk": 2.4 * (1 - cut_score) * ta,
    }

    probs = softmax([logits[p] for p in PHASES])
    phase = rng.choice(PHASES, p=probs)
    return phase, dict(zip(PHASES, probs))


# =========================
# NORMALIZATION
# =========================
def norm_text(x: str) -> str:
    return str(x).strip().lower()

def normalize_muscle_label(raw: str) -> str:
    """
    Attempts to map your catalog's muscle_group strings into the canonical set
    used in SESSION_MUSCLES.
    If no match, returns the normalized raw label.
    """
    s = norm_text(raw)

    synonyms = {
        "pec": "chest", "pecs": "chest", "chest": "chest",
        "lat": "back", "lats": "back", "back": "back",
        "delt": "shoulders", "delts": "shoulders", "shoulder": "shoulders", "shoulders": "shoulders",
        "tri": "triceps", "tricep": "triceps", "triceps": "triceps",
        "bi": "biceps", "bicep": "biceps", "biceps": "biceps",
        "quad": "quads", "quads": "quads",
        "ham": "hamstrings", "hams": "hamstrings", "hamstring": "hamstrings", "hamstrings": "hamstrings",
        "glute": "glutes", "glutes": "glutes",
        "calf": "calves", "calves": "calves",
        "abs": "abs", "core": "abs",
    }
   
    if s in synonyms:
        return synonyms[s]

    for k, v in synonyms.items():
        if k in s:
            return v

    return s


# =======================
# FOOD FILTER
# =======================
def food_filter(df_food, pref: str):
    pref = norm_text(pref)
    if pref == "vegetarian":
        banned = {"meat", "fish", "seafood"}
        return df_food[~df_food["category"].isin(banned)]
    if pref == "carnivore":
        allowed = {"meat", "eggs", "dairy", "fish", "seafood"}
        return df_food[df_food["category"].isin(allowed)]
    return df_food

def read_csv_robust(path):
    
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]
    for enc in encodings:
        try:
            # Detect delimiterq
            with open(path, "r", encoding=enc, errors="strict") as f:
                sample = f.read(4096)
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t"])
            return pd.read_csv(path, encoding=enc, sep=dialect.delimiter)
        except (UnicodeDecodeError, csv.Error):
            continue

    
    with open(path, "r", encoding="latin1", errors="replace") as f:
        sample = f.read(4096)
    delim = ";" if sample.count(";") >= sample.count(",") else ","
    return pd.read_csv(path, encoding="latin1", errors="replace", sep=delim)

# =========================
# MAIN
# =========================
def main():
    np.random.seed(SEED)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ---------- Load catalogs ----------
    workout = read_csv_robust(WORKOUT_CATALOG_CSV)
    food = read_csv_robust(FOOD_CATALOG_CSV)
    

    #Workout catalog normalization
    workout = workout.rename(columns={
        "name_exercise": "exercise_name",
        "rating_exercise": "base_rating"
    })
    workout["exercise_name"] = workout["exercise_name"].astype(str).str.strip()
    workout["muscle_group"] = workout["muscle_group"].astype(str).str.strip()
    workout["muscle_group_norm"] = workout["muscle_group"].apply(normalize_muscle_label)
    workout["base_rating"] = pd.to_numeric(workout.get("base_rating", np.nan), errors="coerce")

    workout = workout.drop_duplicates("exercise_name").reset_index(drop=True)
    workout["exercise_id"] = np.arange(1, len(workout) + 1)

    # Food catalog normalization
    food = food.rename(columns={
        "name_food": "food_name",
        "Protein_g_per_100g": "protein_g_per_100g",
        "Calories_per_100g": "calories_per_100g",
        "Fat_g_per_100g": "fat_g_per_100g",
        "Carbs_g_per_100g": "carbs_g_per_100g",
        "Fiber_g_per_100g": "fiber_g_per_100g",
        "Vitamin_A_RAE": "vitamin_a_rae",
        "Vitamin_C_mg": "vitamin_c_mg",
        "Vitamin_D_Âµg": "vitamin_d_ug",
        "Vitamin_D_µg": "vitamin_d_ug",
        "Vitamin_D_ug": "vitamin_d_ug",
        "Vitamin_B12_Âµg": "vitamin_b12_ug",
        "Vitamin_B12_µg": "vitamin_b12_ug",
        "Vitamin_B12_ug": "vitamin_b12_ug",
        "Calcium_mg": "calcium_mg",
        "Iron_mg": "iron_mg",
        "Magnesium_mg": "magnesium_mg",
        "Potassium_mg": "potassium_mg",
        "Zinc_mg": "zinc_mg",
        "Calories_per_gram_Protein": "calories_per_gram_protein",
    })

    food["food_name"] = food["food_name"].astype(str).str.strip()
    food["category"] = food["category"].astype(str).str.strip().str.lower()

    numeric_cols = [
        "protein_g_per_100g", "calories_per_100g", "fat_g_per_100g", "carbs_g_per_100g", "fiber_g_per_100g",
        "vitamin_a_rae", "vitamin_c_mg", "vitamin_d_ug", "vitamin_b12_ug", "calcium_mg", "iron_mg",
        "magnesium_mg", "potassium_mg", "zinc_mg", "calories_per_gram_protein"
    ]
    for c in numeric_cols:
        if c in food.columns:
            food[c] = pd.to_numeric(food[c], errors="coerce")

    food = food.drop_duplicates("food_name").reset_index(drop=True)
    food["food_id"] = np.arange(1, len(food) + 1)

    # ---------- dim_dates ----------
    date_rows = []
    for i in range(DAYS):
        d = START_DATE + timedelta(days=i)
        ts = pd.Timestamp(d)
        date_rows.append({
            "date_id": d.isoformat(),
            "year": d.year,
            "month": d.month,
            "day": d.day,
            "week": int(ts.isocalendar().week),
            "day_name": ts.day_name()
        })
    dim_dates = pd.DataFrame(date_rows)

    # ---------- dim_users ----------
    def choose_split(training_age_yrs: float) -> str:
        """Choose a split based on training age (for realism)."""
        if training_age_yrs < 1.0:
            return "UL"
        if training_age_yrs < 3.0:
            return np.random.choice(["UL", "PPL"], p=[0.35, 0.65])
        
        return np.random.choice(["PPL", "BRO"], p=[0.55, 0.45])

    def random_user(user_id: int):
        sex = np.random.choice(["M", "F"], p=[0.7, 0.3])
        age = int(np.clip(np.random.normal(28, 6), 18, 50))
        height = float(np.clip(np.random.normal(177 if sex == "M" else 165, 7), 150, 200))

        weight = float(np.clip(np.random.normal(84 if sex == "M" else 62, 12), 45, 145))
        bodyfat = float(np.clip(np.random.normal(18 if sex == "M" else 24, 7), 8, 40))
        training_age = float(np.clip(np.random.normal(3.0, 2.0), 0, 12))

        #Phase depends on body composition
        phase, _ = sample_phase(height, weight, bodyfat, training_age)

        diet_pref = np.random.choice(DIET_PREFS, p=[0.25, 0.20, 0.55])

        # Simple TDEE
        tdee = int(np.clip((weight * 28) + (200 if sex == "M" else 0) + np.random.normal(0, 150), 1600, 4300))

        split = choose_split(training_age)

        return {
            "user_id": user_id,
            "user_name": f"user_{user_id:03d}",
            "sex": sex,
            "age": age,
            "height_cm": round(height, 2),
            "start_weight_kg": round(weight, 2),
            "start_bodyfat_pct": round(bodyfat, 2),
            "training_age_yrs": round(training_age, 2),
            "tdee_kcal": tdee,
            "goal_phase": phase,
            "diet_preference": diet_pref,
            "preferred_split": split
        }

    dim_users = pd.DataFrame([random_user(i) for i in range(1, NUM_USERS + 1)])

    # ---------- Exercise sampling weights ----------
    ex = workout.copy()
    ex["base_rating"] = ex["base_rating"].fillna(5.0)
    ex["w"] = (ex["base_rating"] + 0.5).clip(0.1, 10) ** 1.3
    ex["w"] = ex["w"] / ex["w"].sum()

    # ---------- Fact tables containers ----------
    sessions = []
    sets_rows = []
    feedback_rows = []
    meal_logs = []
    metrics = []

    session_id = 1
    set_id = 1
    feedback_id = 1
    meal_log_id = 1
    metric_id = 1

    # user-level adherence tendency
    user_adherence = {
        int(r.user_id): float(np.clip(np.random.normal(0.82, 0.10), 0.55, 0.97))
        for r in dim_users.itertuples()
    }

    # calories median fallback
    food_cals_median = float(food["calories_per_100g"].median()) if "calories_per_100g" in food.columns else 200.0
    if not np.isfinite(food_cals_median) or food_cals_median <= 0:
        food_cals_median = 200.0

    # ---------- Generate per user ----------
    for u in dim_users.itertuples():
        split_name = str(u.preferred_split)
        split_days = SPLITS[split_name]

        phase = str(u.goal_phase)
        tdee = int(u.tdee_kcal)

        cal_target = int(tdee * (1.0 + PHASE_CAL_ADJ[phase]))
        train_days_per_week = PHASE_TRAIN_DAYS[phase]
        adher = user_adherence[int(u.user_id)]

        # body metrics
        weight = float(u.start_weight_kg)
        waist = float(np.clip(0.45 * float(u.height_cm) + np.random.normal(0, 4), 60, 130))
        bodyfat = float(u.start_bodyfat_pct)

        # foods filtered by preference
        pref_food = food_filter(food, str(u.diet_preference))
        if len(pref_food) < 10:
            pref_food = food

        for day_i in range(DAYS):
            d = START_DATE + timedelta(days=day_i)
            date_str = d.isoformat()

            #train today? 
            p_train = train_days_per_week / 7.0
            trains = np.random.rand() < (p_train * adher)

            #workout generation 
            if trains:
                session_type = split_days[day_i % len(split_days)]
                target_muscles = SESSION_MUSCLES.get(session_type, [])

                pool = ex[ex["muscle_group_norm"].isin(target_muscles)] if target_muscles else ex
                if len(pool) < 6:
                    pool = ex

                n_exercises = int(np.random.randint(4, 7))
                chosen = pool.sample(n=n_exercises, replace=(len(pool) < n_exercises), weights="w")

                duration = int(np.clip(np.random.normal(70, 15), 35, 120))

                sessions.append({
                    "session_id": session_id,
                    "user_id": int(u.user_id),
                    "session_date": date_str,
                    "session_type": session_type,
                    "duration_min": duration,
                    "completed": 1
                })

                for e in chosen.itertuples():
                    
                    base_sets = 3 if phase in ("cut", "intense_cut") else 4
                    if split_name == "BRO" and session_type in ("Chest", "Back", "Legs"):
                        base_sets += 1

                    n_sets = int(np.clip(np.random.normal(base_sets, 1), 2, 7))

                    rep_low, rep_high = (8, 14) if phase in ("cut", "intense_cut") else (6, 12)

                    strength_factor = (float(u.start_weight_kg) / 80.0) * (1.0 + 0.10 * float(u.training_age_yrs))
                    base_load = float(np.clip(np.random.normal(35, 12) * strength_factor, 5, 160))

                    # slow progression
                    prog = 1.0 + (day_i / DAYS) * np.random.uniform(0.02, 0.08)
                    base_load *= prog

                    # feedback signals
                    mmc = float(np.clip(np.random.normal(5.5 + 0.25 * e.base_rating + 0.15 * float(u.training_age_yrs), 1.2), 1, 10))
                    difficulty = float(np.clip(np.random.normal(6.5 - 0.10 * float(u.training_age_yrs) + 0.15 * (10 - e.base_rating), 1.3), 1, 10))
                    discomfort = float(np.clip(np.random.normal(1.5 + 0.12 * difficulty, 1.0), 0, 10))

                    feedback_rows.append({
                        "feedback_id": feedback_id,
                        "session_id": session_id,
                        "exercise_id": int(e.exercise_id),
                        "difficulty_1_10": round(difficulty, 1),
                        "mmc_1_10": round(mmc, 1),
                        "discomfort_1_10": round(discomfort, 1),
                    })
                    feedback_id += 1

                    for s in range(1, n_sets + 1):
                        reps = int(np.random.randint(rep_low, rep_high + 1))
                        rpe = float(np.clip(np.random.normal(7.8, 0.7), 6.0, 9.8))
                        rest = int(np.clip(np.random.normal(120, 30), 60, 240))
                        load = float(np.clip(np.random.normal(base_load, base_load * 0.08), 2.5, 300))

                        sets_rows.append({
                            "set_id": set_id,
                            "session_id": session_id,
                            "exercise_id": int(e.exercise_id),
                            "set_number": s,
                            "reps": reps,
                            "load_kg": round(load, 2),
                            "rpe": round(rpe, 1),
                            "rest_sec": rest
                        })
                        set_id += 1

                session_id += 1

            #meals generation (daily) ----
            cal_actual = cal_target
            cal_actual *= float(np.clip(np.random.normal(0.98, 0.06), 0.80, 1.20))
            cal_actual *= float(np.clip(np.random.normal(adher, 0.08), 0.55, 1.05))
            cal_actual = float(np.clip(cal_actual, 1200, 4500))

            n_foods = int(np.random.randint(6, 11))
            day_foods = pref_food.sample(n=n_foods, replace=(len(pref_food) < n_foods))

            # calorie-based grams allocation
            cals100 = day_foods["calories_per_100g"].fillna(food_cals_median).astype(float).values
            shares = np.random.dirichlet(np.ones(n_foods))

            for j, row in enumerate(day_foods.itertuples()):
                target_cals = cal_actual * float(shares[j])
                cal_per_g = float(getattr(row, "calories_per_100g", food_cals_median) or food_cals_median) / 100.0
                if not np.isfinite(cal_per_g) or cal_per_g <= 0:
                    cal_per_g = food_cals_median / 100.0

                grams = target_cals / cal_per_g
                grams = float(np.clip(grams, 20, 800))

                meal_name = np.random.choice(MEAL_NAMES, p=MEAL_P)

                meal_logs.append({
                    "meal_log_id": meal_log_id,
                    "user_id": int(u.user_id),
                    "meal_date": date_str,
                    "meal_name": meal_name,
                    "food_id": int(row.food_id),
                    "grams": round(grams, 1)
                })
                meal_log_id += 1

            #body metrics ----
            kcal_balance = cal_actual - tdee
            delta_kg = (kcal_balance / 7700.0) * np.random.uniform(0.6, 1.0)

            #training-induced lean effect
            train_bonus = 0.0
            if trains:
                train_bonus = 0.01 * (adher) * (1.0 + 0.05 * float(u.training_age_yrs))
                if phase in ("cut", "intense_cut"):
                    train_bonus *= 0.5

            weight = float(np.clip(weight + delta_kg + train_bonus, 40, 220))

            waist += float(np.clip(delta_kg * (0.6 if kcal_balance > 0 else 0.9) + np.random.normal(0, 0.08), -0.7, 0.7))
            bodyfat += float(np.clip((delta_kg * 0.25) + np.random.normal(0, 0.05), -0.3, 0.3))
            bodyfat = float(np.clip(bodyfat, 6, 45))

            metrics.append({
                "metric_id": metric_id,
                "user_id": int(u.user_id),
                "metric_date": date_str,
                "weight_kg": round(weight, 2),
                "waist_cm": round(float(np.clip(waist, 55, 160)), 2),
                "bodyfat_est_pct": round(bodyfat, 2),
            })
            metric_id += 1

    # =========================
    # DIMENSIONS
    # =========================
    dim_exercises = workout[["exercise_id", "exercise_name", "muscle_group", "base_rating"]].copy()
    wanted_food_cols = [
        "food_id", "food_name", "category",
        "protein_g_per_100g", "calories_per_100g", "fat_g_per_100g", "carbs_g_per_100g", "fiber_g_per_100g",
        "vitamin_a_rae", "vitamin_c_mg", "vitamin_d_ug", "vitamin_b12_ug",
        "calcium_mg", "iron_mg", "magnesium_mg", "potassium_mg", "zinc_mg",
        "calories_per_gram_protein"
    ]
    for c in wanted_food_cols:
        if c not in food.columns:
            food[c] = np.nan
    dim_foods = food[wanted_food_cols].copy()
    dim_users_out = dim_users.copy()

    # =========================
    # FACTS
    # =========================
    fact_sessions = pd.DataFrame(sessions)
    fact_sets = pd.DataFrame(sets_rows)
    fact_feedback = pd.DataFrame(feedback_rows)
    fact_meals = pd.DataFrame(meal_logs)
    fact_metrics = pd.DataFrame(metrics)

    # Save CSVs
    dim_users_out.to_csv(os.path.join(OUTPUT_DIR, "dim_users.csv"), index=False)
    dim_dates.to_csv(os.path.join(OUTPUT_DIR, "dim_dates.csv"), index=False)
    dim_exercises.to_csv(os.path.join(OUTPUT_DIR, "dim_exercises.csv"), index=False)
    dim_foods.to_csv(os.path.join(OUTPUT_DIR, "dim_foods.csv"), index=False)

    fact_sessions.to_csv(os.path.join(OUTPUT_DIR, "fact_workout_sessions.csv"), index=False)
    fact_sets.to_csv(os.path.join(OUTPUT_DIR, "fact_workout_sets.csv"), index=False)
    fact_feedback.to_csv(os.path.join(OUTPUT_DIR, "fact_exercise_feedback.csv"), index=False)
    fact_meals.to_csv(os.path.join(OUTPUT_DIR, "fact_meal_logs.csv"), index=False)
    fact_metrics.to_csv(os.path.join(OUTPUT_DIR, "fact_body_metrics.csv"), index=False)

    #Checks
    print("Generated CSVs in:", OUTPUT_DIR)
    print("\nPhase distribution:")
    print(dim_users_out["goal_phase"].value_counts(normalize=True).round(3))
    print("\nAvg bodyfat by phase:")
    print(dim_users_out.groupby("goal_phase")["start_bodyfat_pct"].mean().round(2).sort_values())


if __name__ == "__main__":
    main()
