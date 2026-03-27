#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   core 全体で使う共通ユーティリティ群。
#   パス、JSON操作、時刻判定、URL判定、ログ補助をまとめる。
#
# 現在の役割:
#   - 共通パス定義
#   - JSON読書き補助
#   - 現在時刻取得
#   - URL簡易判定
#   - ログ出力補助
#
# 今回の変更点:
#   - JSON破損時のフォールバックを追加
#   - パス初期化関数を追加
#   - ログ出力関数を追加
#   - 日時判定補助を追加
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
LOG_DIR = DATA_DIR / "logs"

# ============================================
# セクション: ディレクトリ補助
# ============================================
def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def ensure_runtime_dirs() -> None:
    ensure_dir(DATA_DIR)
    ensure_dir(RUN_DIR)
    ensure_dir(CONFIG_DIR)
    ensure_dir(ASSETS_DIR)
    ensure_dir(LOG_DIR)

# ============================================
# セクション: JSON補助
# ============================================
def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def write_json_atomic(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    os.replace(tmp_path, path)

# ============================================
# セクション: 時刻補助
# ============================================
def now_local() -> datetime:
    return datetime.now()

def is_weekend(dt: datetime | None = None) -> bool:
    target = dt or now_local()
    return target.weekday() in (5, 6)

def is_program_end_hour(dt: datetime | None = None) -> bool:
    target = dt or now_local()
    return target.hour == 0

def is_shutdown_hour(dt: datetime | None = None, shutdown_hour: int = 1) -> bool:
    target = dt or now_local()
    return target.hour == shutdown_hour and target.minute >= 0

# ============================================
# セクション: URL補助
# ============================================
def is_probably_url(value: str) -> bool:
    if not isinstance(value, str):
        return False
    value = value.strip()
    return value.startswith("http://") or value.startswith("https://")

# ============================================
# セクション: ログ補助
# ============================================
def append_log(filename: str, message: str) -> None:
    ensure_runtime_dirs()
    log_path = LOG_DIR / filename
    timestamp = now_local().strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
