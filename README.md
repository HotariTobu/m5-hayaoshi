# m5-hayaoshi

M5Stack / ESP32 向けの早押しボタン用 MicroPython アプリです。
ボタン入力を検出すると、デバイス固有IDを含むURLへ HTTP POST し、成功時にリアクション音で反応します。

## 機能

- 外部ボタン入力をADCで検出
- `{device_id}` を埋め込んだURLへ空のHTTP POSTを送信
- 成功時にPWMでリアクション音を再生

## 必要なもの

- Python 3.10 以上
- [uv](https://docs.astral.sh/uv/) または同等のPython仮想環境
- USB接続できる ESP32 / M5Stack 系デバイス

依存パッケージは `pyproject.toml` に定義されています。

```sh
uv sync
```

## 設定

設定例をコピーして、Wi-Fiや送信先URLを編集します。

```sh
cp app/config.example.json app/config.json
```

主な設定項目:

| 項目 | 内容 |
| --- | --- |
| `wifi_ssid` | 接続するWi-Fi SSID |
| `wifi_password` | Wi-Fiパスワード |
| `post_url_template` | 押下時にPOSTするURL。`{device_id}` を含める必要があります |
| `expected_status` | 成功とみなすHTTPステータスコード |
| `adc_threshold` | ADC入力を押下と判定するしきい値 |
| `cooldown_ms` | 連続入力を抑制する時間 |
| `reset_after_failures` | 連続失敗後にリセットする回数 |

HTTPクライアントは軽量実装のため、送信先URLは `http://` のみ対応しています。
`app/config.json` は秘密情報を含むため `.gitignore` されています。

## ファームウェアを書き込む

接続したデバイスへ MicroPython firmware を書き込みます。
firmwareは `tools/flush.py` が自動で取得します。

```sh
uv run python tools/flush.py
```

ポートを明示する場合:

```sh
uv run python tools/flush.py --port /dev/tty.usbserial-xxxx
```

`tools/flush.py` は、最新の安定版 `ESP32_GENERIC` firmware を取得して `.firmware/` に保存します。
フラッシュ全消去を伴うため、実行時に確認入力があります。

キャッシュ済みfirmwareを使う場合:

```sh
uv run python tools/flush.py --use-cached
```

## アプリを転送する

`tools/upload.py` で、デバイス側に必要なアプリ一式を転送します。

```sh
uv run python tools/upload.py
```

ポートを明示する場合:

```sh
uv run python tools/upload.py --port /dev/tty.usbserial-xxxx
```

## デバイス上で実行する

転送済みのアプリをデバイス上で起動します。

```sh
uv run python tools/run.py
```

実機のファイルシステムを消去する場合は、内容を確認してから実行してください。

```sh
uv run python tools/clear.py
```

## 動作確認用サーバー

ローカルでPOST受信用の確認サーバーを起動できます。

```sh
uv run python tools/verify-server.py 5000
```

`app/config.json` の `post_url_template` を、PCのLAN内IPアドレスに合わせて設定します。

```json
{
  "post_url_template": "http://192.168.1.10:5000/api/act/{device_id}"
}
```

確認サーバーの返すステータスコードを変える場合は、第2引数に指定します。

```sh
uv run python tools/verify-server.py 5000 204
```

## ピン設定

ピン定義は `app/hardware/pins.py` にあります。

## 配線例

配線例は [EXAMPLE.md](EXAMPLE.md) を参照してください。

## 動作確認用の内蔵機能

内蔵ボタンと内蔵LEDは、動作確認用です。

| 状態 | 表示 |
| --- | --- |
| 起動中 | 白 |
| Wi-Fi接続中 | 黄 |
| 待機中 | 青 |
| POST送信中 | シアン |
| 成功 | 緑 |
| Wi-Fiエラー | 赤 |
| POSTエラー | 紫 |
| リセット直前 | 白 |

## ディレクトリ構成

| パス | 内容 |
| --- | --- |
| `app/` | デバイス側で動くMicroPythonアプリ |
| `tools/` | ファームウェア書き込み、転送、実行確認などのホスト側ツール |

## トラブルシュート

- シリアルポートが見つからない場合は、USB接続、ドライバ、デバイスの電源状態を確認してください。
- POSTが失敗する場合は、PC/サーバーが同じネットワークから到達できること、URLが `http://` であること、`expected_status` が実際のレスポンスと一致していることを確認してください。
- 外部ボタンの反応が不安定な場合は、`adc_threshold` と `cooldown_ms` を調整してください。
- Wi-Fi接続が不安定な場合は、`wifi_timeout_ms`、`wifi_recheck_ms`、`reset_after_failures` を調整してください。
