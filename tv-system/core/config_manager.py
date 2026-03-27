#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   settings.json の読書きと設定検証を行う。
#
# 現在の役割:
#   - 画質設定の保持
#   - WebUI からの設定変更受付
#   - デフォルト設定の供給
#
# 今回の変更点:
#   - MVP用の設定管理雛形を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

from pathlib import Path
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
}

ALLOWED_RESOLUTIONS = {"360p", "480p"}

# ============================================
# セクション: 設定取得
# ============================================
def load_settings() -> dict[str, Any]:
    settings = read_json(SETTINGS_PATH, DEFAULT_SETTINGS.copy())
    merged = DEFAULT_SETTINGS.copy()
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
# セクション: バリデーション
# ============================================
def validate_settings(settings: dict[str, Any]) -> dict[str, Any]:
    resolution = settings.get("resolution", "480p")
    if resolution not in ALLOWED_RESOLUTIONS:
        settings["resolution"] = "480p"

    port = settings.get("webui_port", 5000)
    if not isinstance(port, int):
        settings["webui_port"] = 5000

    interval_sec = settings.get("jra_check_interval_sec", 60)
    if not isinstance(interval_sec, int) or interval_sec < 10:
        settings["jra_check_interval_sec"] = 60

    return settings
