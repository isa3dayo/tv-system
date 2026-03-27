#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   settings.json の読書きと設定検証を行う。
#   MVPで必要な解像度、WebUI、JRA確認間隔、シャットダウン時刻などを扱う。
#
# 現在の役割:
#   - 画質設定の保持
#   - WebUI からの設定変更受付
#   - デフォルト設定の供給
#   - 設定値の最低限バリデーション
#
# 今回の変更点:
#   - shutdown_hour を追加
#   - waiting_image / program_end_image を追加
#   - fbi_tty を追加
#   - 数値系設定の補正を強化
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

from typing import Any

from utils import CONFIG_DIR, read_json, write_json_atomic

# ============================================
# セクション: 定数
# ============================================
SETTINGS_PATH = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS: dict[str, Any] = {
    "resolution": "480p",
    "wifi_page_enabled": True,
    "webui_port": 5000,
    "jra_check_interval_sec": 60,
    "shutdown_hour": 1,
    "waiting_image": "program_checking.png",
    "program_end_image": "program_end.png",
    "fbi_tty": 1,
}

ALLOWED_RESOLUTIONS = {"360p", "480p"}

# ============================================
# セクション: 設定取得
# ============================================
def load_settings() -> dict[str, Any]:
    settings = read_json(SETTINGS_PATH, DEFAULT_SETTINGS.copy())
    merged = DEFAULT_SETTINGS.copy()
    if isinstance(settings, dict):
        merged.update(settings)
    return validate_settings(merged)

def save_settings(settings: dict[str, Any]) -> None:
    validated = validate_settings(settings)
    write_json_atomic(SETTINGS_PATH, validated)

def set_setting(key: str, value: Any) -> dict[str, Any]:
    settings = load_settings()
    settings[key] = value
    validated = validate_settings(settings)
    save_settings(validated)
    return validated

# ============================================
# セクション: 個別取得補助
# ============================================
def get_resolution() -> str:
    return load_settings().get("resolution", "480p")

def get_webui_port() -> int:
    return load_settings().get("webui_port", 5000)

def get_jra_check_interval_sec() -> int:
    return load_settings().get("jra_check_interval_sec", 60)

def get_shutdown_hour() -> int:
    return load_settings().get("shutdown_hour", 1)

def get_waiting_image_name() -> str:
    return load_settings().get("waiting_image", "program_checking.png")

def get_program_end_image_name() -> str:
    return load_settings().get("program_end_image", "program_end.png")

# ============================================
# セクション: バリデーション
# ============================================
def validate_settings(settings: dict[str, Any]) -> dict[str, Any]:
    settings = dict(settings)

    resolution = settings.get("resolution", "480p")
    if resolution not in ALLOWED_RESOLUTIONS:
        settings["resolution"] = "480p"

    port = settings.get("webui_port", 5000)
    if not isinstance(port, int) or not (1 <= port <= 65535):
        settings["webui_port"] = 5000

    interval_sec = settings.get("jra_check_interval_sec", 60)
    if not isinstance(interval_sec, int) or interval_sec < 10:
        settings["jra_check_interval_sec"] = 60

    shutdown_hour = settings.get("shutdown_hour", 1)
    if not isinstance(shutdown_hour, int) or not (0 <= shutdown_hour <= 23):
        settings["shutdown_hour"] = 1

    waiting_image = settings.get("waiting_image", "program_checking.png")
    if not isinstance(waiting_image, str) or not waiting_image.strip():
        settings["waiting_image"] = "program_checking.png"

    program_end_image = settings.get("program_end_image", "program_end.png")
    if not isinstance(program_end_image, str) or not program_end_image.strip():
        settings["program_end_image"] = "program_end.png"

    fbi_tty = settings.get("fbi_tty", 1)
    if not isinstance(fbi_tty, int) or fbi_tty < 1:
        settings["fbi_tty"] = 1

    wifi_page_enabled = settings.get("wifi_page_enabled", True)
    settings["wifi_page_enabled"] = bool(wifi_page_enabled)

    return settings
