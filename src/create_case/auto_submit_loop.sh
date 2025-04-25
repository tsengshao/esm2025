#!/usr/bin/env bash
# -------------------------------------------------------------
# auto_submit_loop.sh  –  call auto_submit.sh every 2 h forever
#   • writes its PID to auto_submit_loop.pid
#   • refuses to start if another copy is already running
#   • removes the pid-file on clean exit or Ctrl-C
# -------------------------------------------------------------
# useage
#   nohup ./auto_submit_loop.sh > autolog.submit_loop &
#   • See if script running      : ps -fp $(<auto_submit_loop.pid)
#   • Tail the script output     : tail -f autolog.submit_loop
#   • Stop it gracefully         : kill $(<auto_submit_loop.pid)
#   • Force-kill (rarely needed) : kill -9 $(<auto_submit_loop.pid)
#   • Start again                : repeat the nohup 
# -------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PIDFILE="$SCRIPT_DIR/auto_submit_loop.pid"

cleanup () { rm -f "$PIDFILE"; }
trap cleanup EXIT INT TERM

# ------- safety: only one instance ---------------------------------
if [[ -e $PIDFILE ]]; then
    if kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
        echo "❗ auto_submit_loop is already running (pid $(cat "$PIDFILE"))"
        exit 1
    else
        echo "⚠️  Stale pid-file found; cleaning it."
        rm -f "$PIDFILE"
    fi
fi

echo $$ > "$PIDFILE"        # <-- record our pid

# ------- the endless cycle -----------------------------------------
while true; do
    echo "$(date '+%F %T') auto_submit.sh"
    eval "$SCRIPT_DIR/auto_submit.sh"          # your main one-shot script
    sleep 1h
done
