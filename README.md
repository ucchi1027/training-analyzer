# Training Analyzer

筋トレ記録（CSV）をPythonで分析し、成長の停滞を検出して可視化するツールです。

## 背景
筋トレの記録は取っていても、「どの種目が停滞しているのか」「次に何を改善すべきか」が分かりにくいと感じたため、本ツールを作成しました。

## 機能
- 筋トレ記録（CSV）の読み込み
- 種目ごとの推定1RM（e1RM）推移グラフの生成（PNG出力）
- 成長停滞の検出（stagnating / not stagnating を表示）
- ※改善案の自動提示は今後拡張予定（ルールベース）

## 使用技術
- Python
- pandas
- matplotlib

## ディレクトリ構成
```text
training-analyzer/
├─ data/        # 入力CSV（サンプル）
├─ src/         # Pythonコード
├─ output/      # グラフ出力（PNG）
├─ requirements.txt
└─ README.md
```

## 実行方法
1.依存ライブラリをインストール

```powershell
python -m pip install -r requirements.txt
```


2.サンプルデータで実行（BIG3（ベンチプレス、スクワット、デッドリフト）のグラフPNGが output/ に生成されます）

```powershell
python .\src\main.py .\data\training_log_sample.csv
```

## サンプルデータについて

data/training_log_sample.csv は「停滞しているケース（伸びが見られない例）」として作成しています。
そのため実行すると、BIG3 はすべて stagnating と表示されます。

※実データでは、伸びている期間は not stagnating になる想定です。
