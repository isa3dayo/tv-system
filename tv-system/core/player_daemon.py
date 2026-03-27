#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   yt-dlp + mpv による動画再生の唯一窓口。
#   再生開始時に画像表示を閉じ、再生状態を state_manager に保存する。
#
# 現在の役割:
#   - URL再生
#   - 停止
#   - 再生中判定
#   - 画質設定反映
#   - 再生状態保存
#
# 今回の変更点:
#   - 再生開始前に待機画像を閉じる処理を追加
#   - current_playback の保存内容を強化
#   - 停止時に current_playback を明示クリア
#   - ログ出力を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

import signal
import subprocess
from typing import Optional

from config_manager import get_resolution
from image_display import hide_image
from state_manager import (
    append_playback_history,
    clear_current_playback,
    save_current_playback,
)
from utils import append_log, now_local

# ============================================
# セクション: 定数
# ============================================
PLAYER_LOG = "player.log"

# ============================================
# セクション: 内部状態
# ============================================
_player_process: Optional[subprocess.Popen] = None

# ============================================
# セクション: 補助関数
# ============================================
def _build_mpv_command(url: str) -> list[str]:
    resolution = get_resolution()

    if resolution == "360p":
        ytdl_format = "bestvideo[height<=360]+bestaudio/best[height<=360]"
    else:
        ytdl_format = "bestvideo[height<=480]+bestaudio/best[height<=480]"

    return [
        "mpv",
        f"--ytdl-format={ytdl_format}",
        url,
    ]

# ============================================
# セクション: 公開API
# ============================================
def play_url(url: str, playback_type: str = "generic") -> bool:
    global _player_process

    stop_playback()

    cmd = _build_mpv_command(url)

    try:
        hide_image()
        append_log(PLAYER_LOG, f"再生開始要求: type={playback_type} url={url}")

        _player_process = subprocess.Popen(cmd)

        save_current_playback(
            {
                "url": url,
                "playback_type": playback_type,
                "status": "playing",
                "started_at": now_local().isoformat(timespec="seconds"),
                "pid": _player_process.pid,
            }
        )
        return True

    except Exception as exc:
        append_log(PLAYER_LOG, f"再生開始失敗: {exc}")
        save_current_playback(
            {
                "url": url,
                "playback_type": playback_type,
                "status": "error",
                "error": str(exc),
            }
        )
        return False


def stop_playback() -> None:
    global _player_process

    if _player_process and _player_process.poll() is None:
        append_log(PLAYER_LOG, f"再生停止: pid={_player_process.pid}")
        _player_process.send_signal(signal.SIGTERM)
        try:
            _player_process.wait(timeout=5)
        except Exception:
            _player_process.kill()

    _player_process = None
    clear_current_playback()


def is_playing() -> bool:
    return _player_process is not None and _player_process.poll() is None


def poll_playback_finished() -> bool:
    global _player_process

    if _player_process is None:
        return True

    if _player_process.poll() is None:
        return False

    append_log(PLAYER_LOG, f"再生終了検知: pid={_player_process.pid}")
    append_playback_history(
        {
            "finished_at": now_local().isoformat(timespec="seconds"),
        }
    )
    _player_process = None
    return True
