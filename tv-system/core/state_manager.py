#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   runtime_state や override_queue などの状態ファイルを一元管理する。
#
# 現在の役割:
#   - mode 管理
#   - JRA URL キャッシュ管理
#   - override キュー管理
#   - 再生状態管理
#
# 今回の変更点:
#   - MVP用の状態管理雛形を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

from datetime import date
from typing import Any

from utils import DATA_DIR, RUN_DIR, read_json, write_json_atomic

# ============================================
# セクション: ファイルパス
# ============================================
RUNTIME_STATE_PATH = DATA_DIR / "runtime_state.json"
DATA_JSON_PATH = DATA_DIR / "data.json"
PLAYBACK_HISTORY_PATH = DATA_DIR / "playback_history.json"
PLAYLIST_CACHE_PATH = DATA_DIR / "playlist_cache.json"
OVERRIDE_QUEUE_PATH = RUN_DIR / "override_queue.json"
CURRENT_PLAYBACK_PATH = RUN_DIR / "current_playback.json"

# ============================================
# セクション: デフォルト
# ============================================
DEFAULT_RUNTIME_STATE: dict[str, Any] = {
    "mode": "boot",
    "last_error": "",
}

DEFAULT_DATA_JSON: dict[str, Any] = {
    "jra_live_cache": {}
}

# ============================================
# セクション: runtime_state
# ============================================
def load_runtime_state() -> dict[str, Any]:
    return read_json(RUNTIME_STATE_PATH, DEFAULT_RUNTIME_STATE.copy())

def save_runtime_state(state: dict[str, Any]) -> None:
    write_json_atomic(RUNTIME_STATE_PATH, state)

def set_mode(mode: str) -> dict[str, Any]:
    state = load_runtime_state()
    state["mode"] = mode
    save_runtime_state(state)
    return state

# ============================================
# セクション: data.json
# ============================================
def load_data_json() -> dict[str, Any]:
    return read_json(DATA_JSON_PATH, DEFAULT_DATA_JSON.copy())

def save_data_json(data: dict[str, Any]) -> None:
    write_json_atomic(DATA_JSON_PATH, data)

def get_cached_jra_url(target_date: str | None = None) -> str | None:
    target_date = target_date or date.today().isoformat()
    data = load_data_json()
    return data.get("jra_live_cache", {}).get(target_date)

def set_cached_jra_url(url: str, target_date: str | None = None) -> None:
    target_date = target_date or date.today().isoformat()
    data = load_data_json()
    cache = data.setdefault("jra_live_cache", {})
    cache[target_date] = url
    save_data_json(data)

# ============================================
# セクション: override_queue
# ============================================
def load_override_queue() -> list[str]:
    return read_json(OVERRIDE_QUEUE_PATH, [])

def enqueue_override(url: str) -> list[str]:
    queue = load_override_queue()
    queue.append(url)
    write_json_atomic(OVERRIDE_QUEUE_PATH, queue)
    return queue

def pop_override() -> str | None:
    queue = load_override_queue()
    if not queue:
        return None
    value = queue.pop(0)
    write_json_atomic(OVERRIDE_QUEUE_PATH, queue)
    return value

# ============================================
# セクション: current_playback
# ============================================
def load_current_playback() -> dict[str, Any]:
    return read_json(CURRENT_PLAYBACK_PATH, {})

def save_current_playback(data: dict[str, Any]) -> None:
    write_json_atomic(CURRENT_PLAYBACK_PATH, data)
