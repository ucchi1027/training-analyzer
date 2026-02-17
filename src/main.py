import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def calc_e1rm(weight: float, reps: int, k: float) -> float:
    # estimated 1RM: weight * (1 + reps / k)
    return weight * (1 + reps / k)


def analyze_exercise_e1rm(df: pd.DataFrame, exercise_name: str, output_dir: str) -> None:
    ex = df[df["exercise"] == exercise_name].copy()
    if ex.empty:
        print(f"{exercise_name}: no data")
        return

    ex["date"] = pd.to_datetime(ex["date"])
    ex = ex.sort_values("date")

    # volume（その日の総負荷量）
    ex["volume"] = ex["weight"] * ex["reps"] * ex["sets"]

    # 1日が複数行あるときに日別にまとめる
    daily = ex.groupby("date", as_index=False).agg(
        weight=("weight", "max"),   # その日の最大重量（簡易）
        reps=("reps", "max"),       # その日の最大回数（簡易）
        volume=("volume", "sum"),   # その日の総ボリューム
    )

    # 種目ごとの k
    K_MAP = {
        "bench_press": 40.0,
        "squat": 30.0,
        "deadlift": 30.0,
    }
    k = K_MAP.get(exercise_name, 30.0)

    # e1RM
    daily["e1rm"] = daily.apply(
        lambda r: calc_e1rm(float(r["weight"]), int(r["reps"]), k),
        axis=1
    )

    # ===== グラフ保存 =====
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(output_dir) / f"{exercise_name}_e1rm.png"

    plt.figure()
    plt.plot(daily["date"], daily["e1rm"], marker="o")
    plt.xlabel("date")
    plt.ylabel("estimated 1RM (e1RM)")
    plt.title(f"{exercise_name} progress (e1RM)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

    print(f"saved: {out_path}")

    # ===== 停滞判定 =====
    if len(daily) < 4:
        print(f"{exercise_name}: not enough data to judge stagnation (need >= 4 days)")
        return

    recent = daily.tail(2)["e1rm"]                         # 直近2回
    past_best = daily.head(len(daily) - 2)["e1rm"].max()   # それ以前の最高
    stagnating = recent.max() <= past_best

    print(f"{exercise_name}: {'stagnating' if stagnating else 'not stagnating'}")


def main(csv_path: str) -> None:
    df = pd.read_csv(csv_path)

    required = {"date", "exercise", "weight", "reps", "sets", "body_part"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {sorted(missing)}")

    for ex_name in ["bench_press", "squat", "deadlift"]:
        analyze_exercise_e1rm(df, ex_name, output_dir="output")


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/training_log_sample.csv"
    main(csv_path)

