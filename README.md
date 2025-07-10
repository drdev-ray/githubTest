# HeatIndex-MVP-v0.2

簡単な説明 (JP): ノートPCのウェブカメラだけで観客のエンゲージメントを推定するオープンソースMVPです。

Brief description (EN): Open-source MVP for estimating audience engagement using only a laptop webcam.

## Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
streamlit run main.py
```

初回起動時は計測が始まるまで数秒ほど画面に「Waiting for metrics...」と表示されます。

## Privacy
- 取得した映像や顔画像は保存しません。
- すべての推論はローカルで完結します。
- 年齢・性別推定はあくまで参考値です。

## Troubleshooting
- `ModuleNotFoundError: onnxruntime` が表示された場合は、依存関係が正しく
  インストールされていない可能性があります。以下を実行してください。
```bash
pip install onnxruntime
```
- `ModuleNotFoundError: plotly` が表示された場合は、以下を実行してください。
```bash
pip install plotly
```
