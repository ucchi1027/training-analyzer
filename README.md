# Training Analyzer

筋トレ記録をPythonで分析し、成長の停滞を検出して改善提案を行うツールです。

## 背景
筋トレの記録は取っていても、「どの種目が停滞しているのか」「次に何を改善すべきか」が分かりにくいと感じたため、本ツールを作成しました。

## 機能
- 筋トレ記録（CSV）の読み込み
- 種目ごとのトレーニングボリューム分析
- 成長停滞の検出
- 改善案の自動提示（ルールベース）

## 使用技術
- Python
- pandas
- matplotlib

## ディレクトリ構成
```text
training-analyzer/
├─ data/        # トレーニング記録CSV
├─ src/         # Pythonコード
├─ output/      # グラフ出力
└─ README.md
```
## How to run

```bash
pip install pandas
python src/main.py
```
