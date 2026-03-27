#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   軽量Flask常駐の管理WebUI。
#   現在状態、現在再生、解像度変更、override投入を扱う。
#
# 現在の役割:
#   - 現在状態表示
#   - 解像度変更
#   - override URL投入
#   - Wi-Fiページ土台
#
# 今回の変更点:
#   - current_playback 表示を追加
#   - エラーメッセージ表示を追加
#   - 解像度選択状態を反映
#   - Wi-Fi設定ページ土台を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template_string, request, url_for

BASE_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = BASE_DIR / "core"
sys.path.insert(0, str(CORE_DIR))

from config_manager import get_webui_port, load_settings, set_setting
from override_manager import add_override_url
from state_manager import load_current_playback, load_runtime_state

# ============================================
# セクション: Flask初期化
# ============================================
app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>JRA TV System</title>
</head>
<body>
  <h1>JRA TV System</h1>

  {% if message %}
    <p><strong>{{ message }}</strong></p>
  {% endif %}

  <h2>現在状態</h2>
  <p>mode: {{ mode }}</p>
  <p>last_error: {{ last_error }}</p>

  <h2>現在再生</h2>
  <p>playback_type: {{ playback_type }}</p>
  <p>status: {{ playback_status }}</p>
  <p>url: {{ playback_url }}</p>

  <h2>画質変更</h2>
  <form method="post" action="/settings/resolution">
    <select name="resolution">
      <option value="360p" {% if resolution == "360p" %}selected{% endif %}>360p</option>
      <option value="480p" {% if resolution == "480p" %}selected{% endif %}>480p</option>
    </select>
    <button type="submit">変更</button>
  </form>

  <h2>override 再生</h2>
  <form method="post" action="/override">
    <input type="text" name="url" style="width: 400px;" placeholder="https://...">
    <button type="submit">送信</button>
  </form>

  <h2>Wi-Fi設定</h2>
  <p><a href="/wifi">Wi-Fi設定ページ（準備中）</a></p>
</body>
</html>
"""

WIFI_HTML = """
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>Wi-Fi設定</title>
</head>
<body>
  <h1>Wi-Fi設定</h1>
  <p>このページは土台です。実反映処理は次段階で追加します。</p>

  <form method="post" action="/wifi">
    <div>
      <label>SSID</label>
      <input type="text" name="ssid">
    </div>
    <div>
      <label>Password</label>
      <input type="password" name="password">
    </div>
    <button type="submit">保存（まだ反映しない）</button>
  </form>

  <p><a href="/">戻る</a></p>
</body>
</html>
"""

# ============================================
# セクション: 画面
# ============================================
@app.route("/", methods=["GET"])
def index():
    state = load_runtime_state()
    settings = load_settings()
    playback = load_current_playback()
    message = request.args.get("message", "")

    return render_template_string(
        INDEX_HTML,
        message=message,
        mode=state.get("mode", "unknown"),
        last_error=state.get("last_error", ""),
        resolution=settings.get("resolution", "480p"),
        playback_type=playback.get("playback_type", ""),
        playback_status=playback.get("status", ""),
        playback_url=playback.get("url", ""),
    )


@app.route("/wifi", methods=["GET"])
def wifi_page():
    return render_template_string(WIFI_HTML)


# ============================================
# セクション: API
# ============================================
@app.route("/override", methods=["POST"])
def override():
    url = request.form.get("url", "").strip()
    ok = add_override_url(url)
    if not ok:
        return redirect(url_for("index", message="URLが不正です"))

    return redirect(url_for("index", message="overrideキューへ投入しました"))


@app.route("/settings/resolution", methods=["POST"])
def update_resolution():
    resolution = request.form.get("resolution", "480p").strip()
    set_setting("resolution", resolution)
    return redirect(url_for("index", message=f"解像度を {resolution} に変更しました"))


@app.route("/wifi", methods=["POST"])
def update_wifi_stub():
    ssid = request.form.get("ssid", "").strip()
    _password = request.form.get("password", "").strip()

    if not ssid:
        return redirect(url_for("index", message="SSIDが空です"))

    return redirect(url_for("index", message="Wi-Fi設定ページはまだ土台段階です"))


@app.route("/health", methods=["GET"])
def health():
    state = load_runtime_state()
    playback = load_current_playback()
    settings = load_settings()

    return jsonify(
        {
            "ok": True,
            "mode": state.get("mode", "unknown"),
            "last_error": state.get("last_error", ""),
            "resolution": settings.get("resolution", "480p"),
            "current_playback": playback,
        }
    )

# ============================================
# セクション: 起動
# ============================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=get_webui_port())
