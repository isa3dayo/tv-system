#!/usr/bin/env bash
# ============================================
# スクリプト概要:
#   tv-system 本体側の起動入口。
#   番組準備画面を表示し、WebUI と scheduler を起動する。
#
# 現在の役割:
#   - 本体起動開始のハブ
#   - 待機画像の表示
#   - Python プロセス起動
#
# 今回の変更点:
#   - update_checking 表示を削除
#   - 待機画像表示に役割を絞った
#   - 既存PID停止処理を追加
#   - 起動ログを追加
# ============================================

# ============================================
# セクション: 基本設定
# ============================================
set -u

BASE_DIR="/home/omino/tv-system"
RUN_DIR="${BASE_DIR}/run"
LOG_DIR="${BASE_DIR}/data/logs"
BOOT_DIR="${BASE_DIR}/boot"

WEBUI_PID_FILE="${RUN_DIR}/webui.pid"
SCHEDULER_PID_FILE="${RUN_DIR}/scheduler.pid"

mkdir -p "${RUN_DIR}" "${LOG_DIR}"

# ============================================
# セクション: ログ
# ============================================
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "${LOG_DIR}/boot.log"
}

# ============================================
# セクション: PID整理
# ============================================
stop_old_process_if_needed() {
  local pid_file="$1"
  local name="$2"

  if [ -f "${pid_file}" ]; then
    local pid
    pid="$(cat "${pid_file}" 2>/dev/null || true)"
    if [ -n "${pid}" ] && kill -0 "${pid}" >/dev/null 2>&1; then
      log "旧 ${name} を停止します: pid=${pid}"
      kill "${pid}" >/dev/null 2>&1 || true
      sleep 1
    fi
    rm -f "${pid_file}"
  fi
}

# ============================================
# セクション: 起動画像表示
# ============================================
show_waiting_image() {
  local waiting_image="${BASE_DIR}/assets/program_checking.png"
  bash "${BOOT_DIR}/splash_control.sh" "${waiting_image}" || log "待機画像表示に失敗しました"
}

# ============================================
# セクション: WebUI起動
# ============================================
start_webui() {
  stop_old_process_if_needed "${WEBUI_PID_FILE}" "webui"

  nohup python3 "${BASE_DIR}/webui/app.py" >> "${LOG_DIR}/webui.log" 2>&1 &
  echo $! > "${WEBUI_PID_FILE}"
  log "webui を起動しました: pid=$(cat "${WEBUI_PID_FILE}")"
}

# ============================================
# セクション: Scheduler起動
# ============================================
start_scheduler() {
  stop_old_process_if_needed "${SCHEDULER_PID_FILE}" "scheduler"

  nohup python3 "${BASE_DIR}/core/scheduler.py" >> "${LOG_DIR}/scheduler.log" 2>&1 &
  echo $! > "${SCHEDULER_PID_FILE}"
  log "scheduler を起動しました: pid=$(cat "${SCHEDULER_PID_FILE}")"
}

# ============================================
# セクション: メイン処理
# ============================================
main() {
  log "boot_entry 開始"
  show_waiting_image
  start_webui
  start_scheduler
  log "boot_entry 正常終了"
  exit 0
}

main "$@"
