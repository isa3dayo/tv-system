#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   土日JRAライブの待機・URL取得・再生判断を担当する。
#
# 現在の役割:
#   - 土日判定
#   - 6:00〜19:00判定
#   - 今日のJRA URLキャッシュ利用
#   - A2取得処理の窓口
#
# 今回の変更点:
#   - MVP用のJRA管理雛形を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

from datetime import datetime

from state_manager import get_cached_jra_url, set_cached_jra_url
from utils import is_weekend

# ============================================
# セクション: 時間判定
# ============================================
def is_jra_day(dt: datetime | None = None) -> bool:
    target = dt or datetime.now()
    return is_weekend(target)

def is_jra_time(dt: datetime | None = None) -> bool:
    target = dt or datetime.now()
    start_ok = target.hour >= 6
    end_ok = target.hour < 19
    return is_jra_day(target) and start_ok and end_ok

# ============================================
# セクション: URL取得
# ============================================
def fetch_jra_live_url_from_a2() -> str | None:
    # TODO:
    # ここに A2 または外部取得元から
    # 今日のJRAライブURLを取得する実装を入れる
    return None

def get_today_jra_url() -> str | None:
    cached = get_cached_jra_url()
    if cached:
        return cached

    fetched = fetch_jra_live_url_from_a2()
    if fetched:
        set_cached_jra_url(fetched)
    return fetched
