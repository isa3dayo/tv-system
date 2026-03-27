#!/usr/bin/env python3
# ============================================
# スクリプト概要:
#   iPhoneショートカットや WebUI から来る割り込み再生を扱う。
#
# 現在の役割:
#   - override キュー投入
#   - 次の override 取得
#   - URL妥当性確認
#
# 今回の変更点:
#   - MVP用の割り込み管理雛形を追加
# ============================================

# ============================================
# セクション: import
# ============================================
from __future__ import annotations

from state_manager import enqueue_override, pop_override
from utils import is_probably_url

# ============================================
# セクション: 公開API
# ============================================
def add_override_url(url: str) -> bool:
    if not is_probably_url(url):
        return False
    enqueue_override(url)
    return True

def get_next_override_url() -> str | None:
    return pop_override()
