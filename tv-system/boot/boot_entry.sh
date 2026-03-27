#!/usr/bin/env bash
# ============================================
# スクリプト概要:
#   tv-system 本体側の起動入口。
#   起動時画像を出し、WebUI と scheduler を起動する。
#
# 現在の役割:
#   - 本体起動開始のハブ
#   - splash 表示
#   - Python プロセス起動
#
# 今回の変更点:
#   - MVP用の最小起動処理を追加
#   - WebUI と scheduler 起動処理を追加
#   - PID保存用 run ディレクトリを前提にした処理を追加
# ============================================

# ============================================
# セクション: 基本設定
# ============================================
set -eu

BASE_DIR="/home/omino/tv-system"
RUN_DIR="${BASE_DIR}/run"
LOG_DIR="${BASE_DIR}/data/logs"

mkdir -p "${RUN_DIR}" "${LOG_DIR}"

# ============================================
# セクション: 起動画像表示
# ============================================
bash "${BASE_DIR}/boot/splash_control.sh" "${BASE_DIR}/assets/update_checking.png" || true
sleep 1
bash "${BASE_DIR}/boot/splash_control.sh" "${BASE_DIR}/assets/program_checking.png" || true

# ============================================
# セクション: WebUI起動
# ============================================
nohup python3 "${BASE_DIR}/webui/app.py" >> "${LOG_DIR}/webui.log" 2>&1 &
echo $! > "${RUN_DIR}/webui.pid"

# ============================================
# セクション: Scheduler起動
# ============================================
nohup python3 "${BASE_DIR}/core/scheduler.py" >> "${LOG_DIR}/scheduler.log" 2>&1 &
echo $! > "${RUN_DIR}/scheduler.pid"

exit 0
