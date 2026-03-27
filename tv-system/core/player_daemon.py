#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   yt-dlp + mpv による動画再生の唯一窓口。
#
# 現在の役割:
#   - URL再生
#   - 停止
#   - 再生中判定
#   - 画質設定反映
#
# 今回の変更点:
#   - MVP用の再生制御雛形を追加
#   - mpv subprocess 管理を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

import signal
import subprocess
from typing import Optional

from config_manager import load_settings
from state_manager import save_current_playback

# ============================================
# セクション: 内部状態
# ============================================
_player_process: Optional[subprocess.Popen] = None

# ============================================
# セクション: 補助関数
# ============================================
def _build_mpv_command(url: str) -> list[str]:
    settings = load_settings()
    resolution = settings.get("resolution", "480p")
    ytdl_format = "bestvideo[height<=480]+bestaudio/best[height<=480]" if resolution == "480p" else "bestvideo[height<=360]+bestaudio/best[height<=360]"

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
        _player_process = subprocess.Popen(cmd)
        save_current_playback({
            "url": url,
            "playback_type": playback_type,
            "status": "playing",
        })
        return True
    except Exception:
        save_current_playback({
            "url": url,
            "playback_type": playback_type,
            "status": "error",
        })
        return False

def stop_playback() -> None:
    global _player_process

    if _player_process and _player_process.poll() is None:
        _player_process.send_signal(signal.SIGTERM)
        try:
            _player_process.wait(timeout=5)
        except Exception:
            _player_process.kill()

    _player_process = None
    save_current_playback({})

def is_playing() -> bool:
    return _player_process is not None and _player_process.poll() is None

def poll_playback_finished() -> bool:
    if _player_process is None:
        return True
    return _player_process.poll() is not None
