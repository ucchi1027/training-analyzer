import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def ensure_sample_csv(path: str) -> None:
    """
    サンプルCSVが存在しない場合に、自動生成する。
    ※手でCSV編集したくない人向け
    """
    p = Path(path)
    if p.exists():
        return

    p.parent.mkdir(parents=True, exist_ok=True)

    # bench_pressは最後に少し伸びるようにして「not stagnating」の例が出やすい
    rows = [
        # date, exercise, weight, reps, sets, body_part
        ("2026-01-01", "bench_press", 60, 8, 3, "chest"),
        ("2026-01-08", "bench_press", 60, 8, 3, "chest"),
        ("2026-01-15", "bench_press", 60, 8, 3, "chest"),
        ("2026-01-22", "bench_press", 60, 9, 3, "chest"),
        ("2026-01-29", "bench_press", 60, 9, 3, "chest"),
        ("2026-02-05", "bench_press", 60, 9, 3, "chest"),

        # squat / deadlift は停滞例として横ばい
        ("2026-01-02", "squat", 100, 5, 3, "legs"),
        ("2026-01-09", "squat", 100, 5, 3, "legs"),
        ("2026-01-16", "squat", 100, 5, 3, "legs"),
        ("2026-01-23", "squat", 100, 5, 3, "legs"),
        ("2026-01-30", "squat", 100, 5, 3, "legs"),
        ("2026-02-06", "squat", 100, 5, 3, "legs"),

        ("2026-01-03", "deadlift", 120, 5, 3, "back"),
        ("2026-01-10", "deadlift", 120, 5, 3, "back"),
        ("2026-01-17", "deadlift", 120, 5, 3, "back"),
        ("2026-01-24", "deadlift", 120, 5, 3, "back"),
        ("2026-01-31", "deadlift", 120, 5, 3, "back"),
        ("2026-02-07", "deadlift", 120, 5, 3, "back"),
    ]

    out = pd.DataFrame(
        rows, columns=["date", "exercise", "weight", "reps", "sets", "body_part"]
    )
    out.to_csv(p, index=False)
    print(f"created sample csv: {p}")


def calc_e1rm(weight: float, reps: int, k: float) -> float:
    """
    推定1RM（e1RM）: weight * (1 + reps/k)
    kは種目ごとに調整できる（例：bench=40, squat/deadlift=30）
    """
    return weight * (1 + reps / k)


def analyze_exercise_e1rm(df: pd.DataFrame, exercise_name: str, output_dir: str) -> None:
    # 対象種目のみ抽出
    ex = df[df["exercise"] == exercise_name].copy()
    if ex.empty:
        print(f"{exercise_name}: no data")
        return

    # 日付をdatetimeにして並べ替え
    ex["date"] = pd.to_datetime(ex["date"], errors="coerce")
    ex = ex.dropna(subset=["date"]).sort_values("date")

    # volume = weight * reps * sets
    ex["volume"] = ex["weight"] * ex["reps"] * ex["sets"]

    # 日ごとにまとめる（その日の最大重量/最大回数、volume合計）
    daily = ex.groupby("date", as_index=False).agg(
        weight=("weight", "max"),
        reps=("reps", "max"),
        volume=("volume", "sum"),
    )

    # 種目ごとのk
    K_MAP = {
        "bench_press": 40.0,
        "squat": 30.0,
        "deadlift": 30.0,
    }
    k = K_MAP.get(exercise_name, 30.0)

    # 推定1RM（e1RM）
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

    # ===== 停滞判定（ブレに強い版：直近3平均 vs その前3平均） =====
    if len(daily) < 6:
        print(f"{exercise_name}: not enough data to judge stagnation (need >= 6 days)")
        return

    recent_mean = daily.tail(3)["e1rm"].mean()
    prev_mean = daily.iloc[-6:-3]["e1rm"].mean()

    tolerance = 0.01  # 1%未満は誤差として「伸びてない」扱い
    improving = recent_mean > prev_mean * (1 + tolerance)
    stagnating = not improving

    print(
        f"{exercise_name}: {'stagnating' if stagnating else 'not stagnating'} "
        f"(prev3={prev_mean:.1f}, recent3={recent_mean:.1f})"
    )

    # ===== 簡易の改善提案（ルールベース例） =====
    if stagnating:
        print(
            f"{exercise_name}: suggestion -> "
            "1) deload 1 week OR 2) add +1 set at same weight/reps OR 3) reduce weight slightly and increase reps"
        )


def main(csv_path: str) -> None:
    # サンプル指定なら、無ければ自動生成
    if Path(csv_path).name == "training_log_sample.csv":
        ensure_sample_csv(csv_path)

    df = pd.read_csv(csv_path)

    # 必要列チェック
    required = {"date", "exercise", "weight", "reps", "sets", "body_part"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {sorted(missing)}")

    # BIG3を解析
    for ex_name in ["bench_press", "squat", "deadlift"]:
        analyze_exercise_e1rm(df, ex_name, output_dir="output")


if __name__ == "__main__":
    # 使い方（PowerShell）:
    # python .\src\main.py .\data\training_log_sample.csv
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/training_log_sample.csv"
    main(csv_path)

