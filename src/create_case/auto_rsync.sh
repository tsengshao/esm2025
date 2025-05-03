#!/usr/bin/env bash
# ---------------------------------------
# auto_rsync.sh – sync cases & clean up
# ---------------------------------------
set -euo pipefail

# --- BASIC SETTINGS ----------------------------------------------------------
RUNDIR=$(cd "$(dirname "$0")" && pwd)          # folder that holds this script
ARCHIVE="${RUNDIR}/archive"                    # where the cases live
#CASE_HEADER='f02.F2000.hindcast_'              # pattern of case directories
CASE_HEADER='f02.F2000.hindcast_SSTp3k_'              # pattern of case directories
#REMOTE="39:/data/C.shaoyu/taiesm/archive" # change user/host as needed
REMOTE="tw3:~/data_wt/archive"            # change user/host as needed

LOGFILE="${RUNDIR}/autolog.rsync"       # everything goes here
RSYNC_RECORD="${RUNDIR}/autolog.rsync_processing"  # book-keeping: one line per case

touch "$LOGFILE" "$RSYNC_RECORD"

echo "$(date '+%F %T') ----- run start -----" >> "$LOGFILE"

# --- MAIN LOOP ---------------------------------------------------------------
for CPATH in "${ARCHIVE}/${CASE_HEADER}"*; do
    [[ -d $CPATH ]] || continue                      # ignore if nothing matches
    CNAME=$(basename "$CPATH")
    SIZE_BYTES=$(du -sb --apparent-size "$CPATH" | awk '{print $1}')

    # --- Has this case already been queued once? -----------------------------
    if grep -qE "^${CNAME}\b" "$RSYNC_RECORD"; then
        echo "$(date '+%F %T') CLEAN  $CNAME  size=${SIZE_BYTES}" >> "$LOGFILE"

        # remove *directories* that are now empty (files were deleted by rsync
        # with --remove-source-files in the *previous* run)
        find "$CPATH" -depth -type d -empty -print -delete >> "$LOGFILE" 2>&1
        continue
    fi

    # --- First time we see this case: launch rsync ---------------------------
    echo "$(date '+%F %T') RSYNC  $CNAME  size=${SIZE_BYTES}" >> "$LOGFILE"

    nohup rsync -avh --remove-source-files --exclude='.*' \
          "$CPATH"  "$REMOTE" \
          > "nohup_rsync_${CNAME}.log" 2>&1 &

    # record so we do not launch it again next time
    echo "${CNAME} $(date '+%F %T')" >> "$RSYNC_RECORD"
done

echo "$(date '+%F %T') ----- run end -----" >> "$LOGFILE"
