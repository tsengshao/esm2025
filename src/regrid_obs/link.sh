#!/usr/bin/env bash
# build_f02_obs_hindcast_links.sh
# -----------------------------------------------------------
# Create 12-day hindcast folders (atm/hist) filled with
# symlinks whose names start with "f02.F2000.obs_YYYYMMDD00".

set -euo pipefail

# -------- USER SETTINGS ------------------------------------
SRC_ROOT="/data/C.shaoyu/ESM2025/data/obs_taigrid/merge"
DST_ROOT="/data/C.shaoyu/ESM2025/data/obs_hindcast"
START_DATE="2016-08-01"
END_DATE="2016-08-02"        # inclusive
#END_DATE="2016-10-31"        # inclusive
WINDOW_DAYS=12               # files per hindcast
DATE_CMD=date                # use "gdate" on macOS
CASE_PREFIX="f02.F2000.obs"  # <-- new hindcast name prefix
# -----------------------------------------------------------

mkdir -p "$DST_ROOT"

curr="$START_DATE"
while [[ $($DATE_CMD -d "$curr" +%Y%m%d) -le $($DATE_CMD -d "$END_DATE" +%Y%m%d) ]]; do
    ymd="$($DATE_CMD -d "$curr" +%Y%m%d)"
    run_tag="${ymd}00"
    case_name="${CASE_PREFIX}_${run_tag}"            # f02.F2000.obs_YYYYMMDD00
    run_dir="$DST_ROOT/${case_name}/atm/hist"
    mkdir -p "$run_dir"

    # Link WINDOW_DAYS consecutive source files
    for ((i=0; i<WINDOW_DAYS; i++)); do
        file_date="$($DATE_CMD -d "$curr +${i} day" +%Y-%m-%d)"
        src_file="${SRC_ROOT}/obs_f02_${file_date}.nc"

        if [[ -e "$src_file" ]]; then
            link_name="${case_name}.h1.${file_date}.nc"
            ln -sf "$src_file" "${run_dir}/${link_name}"
        else
            echo "Warning: missing file ${src_file}" >&2
        fi
    done

    # Next initialization day
    curr="$($DATE_CMD -d "$curr +1 day" +%Y-%m-%d)"
done
