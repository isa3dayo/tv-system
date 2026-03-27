#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   軽量Flask常駐の管理WebUI。
#
# 現在の役割:
#   - 現在状態表示
#   - 解像度変更
#   - override URL投入
#   - 将来のWi-Fi変更ページ土台
#
# 今回の変更点:
#   - MVP用の最小Flaskアプリ雛形を追加
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

from config_manager import load_settings, set_setting
from override_manager import add_override_url
from state_manager import load_runtime_state

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

  <h2>現在状態</h2>
  <p>mode: {{ mode }}</p>
  <p>resolution: {{ resolution }}</p>

  <h2>画質変更</h2>
  <form method="post" action="/settings/resolution">
    <select name="resolution">
      <option value="360p">360p</option>
      <option value="480p">480p</option>
    </select>
    <button type="submit">変更</button>
  </form>

  <h2>override 再生</h2>
  <form method="post" action="/override">
    <input type="text" name="url" style="width: 400px;" placeholder="https://...">
    <button type="submit">送信</button>
  </form>
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
    return render_template_string(
        INDEX_HTML,
        mode=state.get("mode", "unknown"),
        resolution=settings.get("resolution", "480p"),
    )

# ============================================
# セクション: API
# ============================================
@app.route("/override", methods=["POST"])
def override():
    url = request.form.get("url", "").strip()
    ok = add_override_url(url)
    if not ok:
        return jsonify({"ok": False, "error": "invalid url"}), 400
    return redirect(url_for("index"))

@app.route("/settings/resolution", methods=["POST"])
def update_resolution():
    resolution = request.form.get("resolution", "480p").strip()
    set_setting("resolution", resolution)
    return redirect(url_for("index"))

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

# ============================================
# セクション: 起動
# ============================================
if __name__ == "__main__":
    settings = load_settings()
    port = settings.get("webui_port", 5000)
    app.run(host="0.0.0.0", port=port)
