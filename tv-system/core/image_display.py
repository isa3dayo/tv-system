#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   fbi を使った画像表示を Python から扱うための薄い抽象化。
#
# 現在の役割:
#   - 起動画像表示
#   - program_end 画像表示
#   - オフライン画像表示
#
# 今回の変更点:
#   - MVP用の画像表示雛形を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

import subprocess
from pathlib import Path

from utils import BASE_DIR

# ============================================
# セクション: 定数
# ============================================
SPLASH_SCRIPT = BASE_DIR / "boot" / "splash_control.sh"

# ============================================
# セクション: 表示制御
# ============================================
def show_image(image_path: str | Path) -> None:
    subprocess.run(
        ["bash", str(SPLASH_SCRIPT), str(image_path)],
        check=False,
    )

def show_asset(filename: str) -> None:
    image_path = BASE_DIR / "assets" / filename
    show_image(image_path)
