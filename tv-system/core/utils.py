#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   core 全体で使う共通ユーティリティ群。
#
# 現在の役割:
#   - パス取得
#   - JSON読書き補助
#   - 現在時刻取得
#   - URL簡易判定
#
# 今回の変更点:
#   - MVP用の共通関数を新規追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# ============================================
# セクション: パス定義
# ============================================
BASE_DIR = Path("/home/omino/tv-system")
DATA_DIR = BASE_DIR / "data"
RUN_DIR = BASE_DIR / "run"
CONFIG_DIR = BASE_DIR / "config"
ASSETS_DIR = BASE_DIR / "assets"

# ============================================
# セクション: 汎用関数
# ============================================
def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_json_atomic(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)

def now_local() -> datetime:
    return datetime.now()

def is_weekend(dt: datetime | None = None) -> bool:
    target = dt or now_local()
    return target.weekday() in (5, 6)

def is_probably_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")
