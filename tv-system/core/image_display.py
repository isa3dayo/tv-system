#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   fbi を使った画像表示を Python から扱うための薄い抽象化。
#   scheduler や player_daemon から画像表示/停止を呼べるようにする。
#
# 現在の役割:
#   - 起動画像表示
#   - 待機画像表示
#   - program_end 画像表示
#   - 画像停止
#
# 今回の変更点:
#   - hide_image() を追加
#   - 画像存在確認を追加
#   - fbi_tty を設定から取得
#   - ログ出力を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from config_manager import load_settings
from utils import ASSETS_DIR, BASE_DIR, append_log

# ============================================
# セクション: 定数
# ============================================
SPLASH_SCRIPT = BASE_DIR / "boot" / "splash_control.sh"
IMAGE_LOG = "image_display.log"

# ============================================
# セクション: 補助関数
# ============================================
def _build_env() -> dict[str, str]:
    settings = load_settings()
    env = os.environ.copy()
    env["FBI_TTY"] = str(settings.get("fbi_tty", 1))
    return env

# ============================================
# セクション: 表示制御
# ============================================
def show_image(image_path: str | Path) -> bool:
    image_path = Path(image_path)

    if not image_path.exists():
        append_log(IMAGE_LOG, f"画像が存在しません: {image_path}")
        return False

    result = subprocess.run(
        ["bash", str(SPLASH_SCRIPT), str(image_path)],
        check=False,
        env=_build_env(),
    )

    ok = result.returncode == 0
    append_log(IMAGE_LOG, f"画像表示: path={image_path} ok={ok}")
    return ok


def show_asset(filename: str) -> bool:
    image_path = ASSETS_DIR / filename
    return show_image(image_path)


def hide_image() -> bool:
    result = subprocess.run(
        ["bash", str(SPLASH_SCRIPT), "stop"],
        check=False,
        env=_build_env(),
    )
    ok = result.returncode == 0
    append_log(IMAGE_LOG, f"画像停止: ok={ok}")
    return ok
