import pandas as pd

def main():
    df = pd.read_csv("data/training_log.csv")
    df["volume"] = df["weight"] * df["reps"] * df["sets"]

    summary = (
        df.groupby(["body_part", "exercise"])["volume"]
        .sum()
        .sort_values(ascending=False)
    )

    print("=== Total Volume (body_part, exercise) ===")
    print(summary)

if __name__ == "__main__":
    main()
