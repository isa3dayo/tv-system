#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   runtime_state や override_queue などの状態ファイルを一元管理する。
#   scheduler / webui / player_daemon が直接ファイルを触らずに済むようにする。
#
# 現在の役割:
#   - mode 管理
#   - JRA URL キャッシュ管理
#   - override キュー管理
#   - 再生状態管理
#   - エラー状態管理
#
# 今回の変更点:
#   - 初期化関数を追加
#   - mode更新時の timestamp を追加
#   - current_playback のクリア関数を追加
#   - エラー記録関数を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

from datetime import date
from typing import Any

from utils import (
    DATA_DIR,
    RUN_DIR,
    ensure_runtime_dirs,
    now_local,
    read_json,
    write_json_atomic,
)

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
    "updated_at": "",
}

DEFAULT_DATA_JSON: dict[str, Any] = {
    "jra_live_cache": {}
}

DEFAULT_PLAYBACK_HISTORY: list[dict[str, Any]] = []
DEFAULT_PLAYLIST_CACHE: dict[str, Any] = {}

# ============================================
# セクション: 初期化
# ============================================
def initialize_state_files() -> None:
    ensure_runtime_dirs()

    if not RUNTIME_STATE_PATH.exists():
        save_runtime_state(DEFAULT_RUNTIME_STATE.copy())

    if not DATA_JSON_PATH.exists():
        save_data_json(DEFAULT_DATA_JSON.copy())

    if not PLAYBACK_HISTORY_PATH.exists():
        write_json_atomic(PLAYBACK_HISTORY_PATH, DEFAULT_PLAYBACK_HISTORY.copy())

    if not PLAYLIST_CACHE_PATH.exists():
        write_json_atomic(PLAYLIST_CACHE_PATH, DEFAULT_PLAYLIST_CACHE.copy())

    if not OVERRIDE_QUEUE_PATH.exists():
        write_json_atomic(OVERRIDE_QUEUE_PATH, [])

    if not CURRENT_PLAYBACK_PATH.exists():
        write_json_atomic(CURRENT_PLAYBACK_PATH, {})

# ============================================
# セクション: runtime_state
# ============================================
def load_runtime_state() -> dict[str, Any]:
    data = read_json(RUNTIME_STATE_PATH, DEFAULT_RUNTIME_STATE.copy())
    merged = DEFAULT_RUNTIME_STATE.copy()
    if isinstance(data, dict):
        merged.update(data)
    return merged

def save_runtime_state(state: dict[str, Any]) -> None:
    payload = DEFAULT_RUNTIME_STATE.copy()
    payload.update(state)
    write_json_atomic(RUNTIME_STATE_PATH, payload)

def set_mode(mode: str) -> dict[str, Any]:
    state = load_runtime_state()
    state["mode"] = mode
    state["updated_at"] = now_local().isoformat(timespec="seconds")
    save_runtime_state(state)
    return state

def set_last_error(message: str) -> dict[str, Any]:
    state = load_runtime_state()
    state["last_error"] = message
    state["updated_at"] = now_local().isoformat(timespec="seconds")
    save_runtime_state(state)
    return state

# ============================================
# セクション: data.json
# ============================================
def load_data_json() -> dict[str, Any]:
    data = read_json(DATA_JSON_PATH, DEFAULT_DATA_JSON.copy())
    merged = DEFAULT_DATA_JSON.copy()
    if isinstance(data, dict):
        merged.update(data)
    return merged

def save_data_json(data: dict[str, Any]) -> None:
    payload = DEFAULT_DATA_JSON.copy()
    payload.update(data)
    write_json_atomic(DATA_JSON_PATH, payload)

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
    queue = read_json(OVERRIDE_QUEUE_PATH, [])
    if isinstance(queue, list):
        return [item for item in queue if isinstance(item, str) and item.strip()]
    return []

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

def clear_override_queue() -> None:
    write_json_atomic(OVERRIDE_QUEUE_PATH, [])

# ============================================
# セクション: current_playback
# ============================================
def load_current_playback() -> dict[str, Any]:
    data = read_json(CURRENT_PLAYBACK_PATH, {})
    return data if isinstance(data, dict) else {}

def save_current_playback(data: dict[str, Any]) -> None:
    payload = dict(data)
    payload["updated_at"] = now_local().isoformat(timespec="seconds")
    write_json_atomic(CURRENT_PLAYBACK_PATH, payload)

def clear_current_playback() -> None:
    write_json_atomic(CURRENT_PLAYBACK_PATH, {})

# ============================================
# セクション: playback_history
# ============================================
def load_playback_history() -> list[dict[str, Any]]:
    data = read_json(PLAYBACK_HISTORY_PATH, DEFAULT_PLAYBACK_HISTORY.copy())
    return data if isinstance(data, list) else DEFAULT_PLAYBACK_HISTORY.copy()

def append_playback_history(item: dict[str, Any]) -> None:
    history = load_playback_history()
    history.append(item)
    write_json_atomic(PLAYBACK_HISTORY_PATH, history)
