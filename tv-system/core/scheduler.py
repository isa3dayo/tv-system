#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   システム全体の唯一の司令塔。
#   待機画像、JRA、override、program_end、shutdown を判断して遷移させる。
#
# 現在の役割:
#   - mode 判定
#   - JRA / override / program_end / shutdown 遷移
#   - player_daemon を呼び分ける
#   - 待機画像の表示制御
#
# 今回の変更点:
#   - shutdown 判定バグを修正
#   - state 初期化処理を追加
#   - 待機画面復帰処理を明確化
#   - override / JRA / program_end の優先順を整理
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

import time
from datetime import datetime

from config_manager import (
    get_jra_check_interval_sec,
    get_program_end_image_name,
    get_shutdown_hour,
    get_waiting_image_name,
)
from image_display import show_asset
from jra_manager import get_today_jra_url, is_jra_time
from override_manager import get_next_override_url
from player_daemon import is_playing, play_url, poll_playback_finished, stop_playback
from state_manager import (
    initialize_state_files,
    load_current_playback,
    set_last_error,
    set_mode,
)
from utils import append_log

# ============================================
# セクション: 定数
# ============================================
SCHEDULER_LOG = "scheduler.log"

# ============================================
# セクション: 判定補助
# ============================================
def is_program_end_time(now: datetime) -> bool:
    return now.hour == 0

def is_shutdown_time(now: datetime) -> bool:
    shutdown_hour = get_shutdown_hour()
    return now.hour == shutdown_hour

def determine_idle_mode(now: datetime) -> str:
    if is_shutdown_time(now):
        return "shutdown_pending"
    if is_program_end_time(now):
        return "program_end"
    if is_jra_time(now):
        return "jra_waiting"
    return "idle"

# ============================================
# セクション: 表示補助
# ============================================
def show_waiting_image() -> None:
    show_asset(get_waiting_image_name())

def show_program_end_image() -> None:
    show_asset(get_program_end_image_name())

# ============================================
# セクション: 遷移処理
# ============================================
def handle_override() -> bool:
    url = get_next_override_url()
    if not url:
        return False

    append_log(SCHEDULER_LOG, f"override 開始: {url}")
    set_mode("override")
    stop_playback()

    ok = play_url(url, playback_type="override")
    if not ok:
        set_last_error("override 再生開始に失敗しました")
        show_waiting_image()
        set_mode(determine_idle_mode(datetime.now()))
        return True

    return True

def handle_jra() -> bool:
    if not is_jra_time():
        return False

    url = get_today_jra_url()
    if not url:
        set_mode("jra_waiting")
        show_waiting_image()
        return True

    current = load_current_playback()
    if current.get("playback_type") == "jra_live" and is_playing():
        return True

    if not is_playing():
        append_log(SCHEDULER_LOG, f"JRA 再生開始: {url}")
        set_mode("jra_live")
        ok = play_url(url, playback_type="jra_live")
        if not ok:
            set_last_error("JRA 再生開始に失敗しました")
            set_mode("jra_waiting")
            show_waiting_image()
        return True

    return False

def handle_program_end(now: datetime) -> bool:
    if not is_program_end_time(now):
        return False

    set_mode("program_end")

    if not is_playing():
        show_program_end_image()

    return True

def handle_idle(now: datetime) -> None:
    mode = determine_idle_mode(now)
    set_mode(mode)

    if mode == "idle":
        show_waiting_image()
    elif mode == "jra_waiting":
        show_waiting_image()
    elif mode == "program_end" and not is_playing():
        show_program_end_image()

# ============================================
# セクション: 再生終了後の復帰
# ============================================
def handle_finished_playback(now: datetime) -> None:
    current = load_current_playback()
    playback_type = current.get("playback_type", "")

    if playback_type == "override":
        append_log(SCHEDULER_LOG, "override 終了")
        if is_jra_time(now):
            set_mode("jra_waiting")
            show_waiting_image()
            return

        handle_idle(now)
        return

    if playback_type == "jra_live":
        append_log(SCHEDULER_LOG, "JRA 再生終了")
        handle_idle(now)
        return

    handle_idle(now)

# ============================================
# セクション: メインループ
# ============================================
def main() -> None:
    initialize_state_files()
    set_mode("boot")
    append_log(SCHEDULER_LOG, "scheduler 開始")
    show_waiting_image()

    while True:
        now = datetime.now()

        if is_shutdown_time(now):
            append_log(SCHEDULER_LOG, "shutdown_pending へ遷移")
            set_mode("shutdown_pending")
            stop_playback()
            break

        if handle_override():
            time.sleep(1)
            continue

        if handle_jra():
            time.sleep(get_jra_check_interval_sec() if not is_playing() else 1)
            continue

        if handle_program_end(now):
            time.sleep(1)
            continue

        if is_playing():
            time.sleep(1)
            continue

        if poll_playback_finished():
            handle_finished_playback(now)

        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        set_last_error(str(exc))
        append_log(SCHEDULER_LOG, f"fatal error: {exc}")
        raise
