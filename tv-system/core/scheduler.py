#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   システム全体の唯一の司令塔。
#
# 現在の役割:
#   - mode 判定
#   - JRA / override / program_end / shutdown 遷移
#   - player_daemon を呼び分ける
#
# 今回の変更点:
#   - MVP用の最小状態遷移ループを追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

import time
from datetime import datetime

from image_display import show_asset
from jra_manager import get_today_jra_url, is_jra_time
from override_manager import get_next_override_url
from player_daemon import is_playing, play_url, poll_playback_finished, stop_playback
from state_manager import load_runtime_state, set_mode

# ============================================
# セクション: mode判定
# ============================================
def is_program_end_time(now: datetime) -> bool:
    return now.hour == 0

def is_shutdown_time(now: datetime) -> bool:
    return now.hour >= 1

def determine_idle_mode(now: datetime) -> str:
    if is_shutdown_time(now):
        return "shutdown_pending"
    if is_program_end_time(now):
        return "program_end"
    if is_jra_time(now):
        return "jra_waiting"
    return "idle"

# ============================================
# セクション: 遷移処理
# ============================================
def handle_override() -> bool:
    url = get_next_override_url()
    if not url:
        return False

    set_mode("override")
    stop_playback()
    play_url(url, playback_type="override")
    return True

def handle_jra() -> bool:
    if not is_jra_time():
        return False

    url = get_today_jra_url()
    if not url:
        set_mode("jra_waiting")
        show_asset("program_checking.png")
        return True

    if not is_playing():
        set_mode("jra_live")
        play_url(url, playback_type="jra_live")
    return True

def handle_program_end() -> bool:
    now = datetime.now()
    if is_program_end_time(now):
        set_mode("program_end")
        if not is_playing():
            show_asset("program_end.png")
        return True
    return False

# ============================================
# セクション: メインループ
# ============================================
def main() -> None:
    set_mode("boot")
    show_asset("program_checking.png")

    while True:
        now = datetime.now()

        if is_shutdown_time(now):
            set_mode("shutdown_pending")
            stop_playback()
            break

        if handle_override():
            time.sleep(1)
            continue

        if handle_jra():
            time.sleep(1)
            continue

        if handle_program_end():
            time.sleep(1)
            continue

        if poll_playback_finished():
            mode = determine_idle_mode(now)
            set_mode(mode)

        time.sleep(1)

if __name__ == "__main__":
    main()
