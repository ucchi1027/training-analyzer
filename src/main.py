import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def calc_e1rm(weight: float, reps: int, k: float) -> float:
    """
    推定1RM（e1RM）を計算する。
    例）bench: weight * (1 + reps/40) など、kは種目ごとに調整
    """
    return weight * (1 + reps / k)


def analyze_exercise_e1rm(df: pd.DataFrame, exercise_name: str, output_dir: str) -> None:
    # 対象種目だけ抽出
    ex = df[df["exercise"] == exercise_name].copy()
    if ex.empty:
        print(f"{exercise_name}: no data")
        return

    # 日付をdatetimeにして日付順に並べる
    ex["date"] = pd.to_datetime(ex["date"], errors="coerce")
    ex = ex.dropna(subset=["date"]).sort_values("date")

    # 1回の行に対してボリューム（重量×回数×セット）
    ex["volume"] = ex["weight"] * ex["reps"] * ex["sets"]

    # 1日に複数セット（複数行）がある場合は日ごとにまとめる
    # weight/reps は「その日の最大（簡易）」、volume は合計
    daily = ex.groupby("date", as_index=False).agg(
        weight=("weight", "max"),
        reps=("reps", "max"),
        volume=("volume", "sum"),
    )

    # 種目ごとのk（ベンチは40、スクワット/デッドは30）
    K_MAP = {
        "bench_press": 40.0,
        "squat": 30.0,
        "deadlift": 30.0,
    }
    k = K_MAP.get(exercise_name, 30.0)

    # 推定1RM（e1RM）を計算
    daily["e1rm"] = daily.apply(
        lambda r: calc_e1rm(float(r["weight"]), int(r["reps"]), k),
        axis=1,
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
    # 判定には最低6回分（直近3 + その前3）が必要
    if len(daily) < 6:
        print(f"{exercise_name}: not enough data to judge stagnation (need >= 6 days)")
        return

    recent_mean = daily.tail(3)["e1rm"].mean()       # 直近3回平均
    prev_mean = daily.iloc[-6:-3]["e1rm"].mean()     # その前3回平均

    tolerance = 0.01  # 1%未満は誤差として「伸びてない」とみなす
    improving = recent_mean > prev_mean * (1 + tolerance)
    stagnating = not improving

    print(
        f"{exercise_name}: {'stagnating' if stagnating else 'not stagnating'} "
        f"(prev3={prev_mean:.1f}, recent3={recent_mean:.1f})"
    )


def main(csv_path: str) -> None:
    # CSVを読み込む
    df = pd.read_csv(csv_path)

    # 必要列チェック（エラーが分かりやすくなる）
    required = {"date", "exercise", "weight", "reps", "sets", "body_part"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {sorted(missing)}")

    # BIG3を解析
    for ex_name in ["bench_press", "squat", "deadlift"]:
        analyze_exercise_e1rm(df, ex_name, output_dir="output")


if __name__ == "__main__":
    # 使い方：
    # python .\src\main.py .\data\training_log_sample.csv
    # 引数がない場合は data/training_log_sample.csv を読む
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/training_log_sample.csv"
    main(csv_path)
