#!/usr/bin/env bash
# -------------------------------------------------------------------
#  submit_when_quota_ok.sh
#  • Submits up to 3 fresh cases per run
#  • Each case needs JOB_SIZE_GB GiB of free quota
#  • Never pushes your total squeue count above 5
# -------------------------------------------------------------------
set -euo pipefail

# --------- user-tunable variables ----------------------------------
USER=umbrella0c
FS=work1                                   # GPFS filesystem
CASE_PATTERN="f02.F2000.hindcast_*"        # case dirs to scan
JOB_CMD="./*.submit"                       # <-- SLURM submission cmd
JOB_SIZE_GB=${JOB_SIZE_GB:-200}            # 1 job ≙ this many GiB
MAX_PER_RUN=3                              # cap submissions / run
MAX_IN_QUEUE=5                             # cap total squeue jobs
LOG=autolog.submit
# -------------------------------------------------------------------
JOB_SIZE=$(( JOB_SIZE_GB * 1024**2 ))      # bytes per job

# --------- single-instance lock (optional but safe) ----------------
exec 9>"/tmp/${USER}_submit_quota.lock"
flock -n 9 || { echo "Another instance is running; exit."; exit 0; }

timestamp() { date '+%F %T'; }

kbytes_free () {
    # quota – used, in bytes
    mmlsquota -u "$USER" --block-size K "$FS" |
        awk '$2=="USR"{print 2500000000 - $3}'
        #awk '$2=="USR"{print $4 - $3}'
}

queue_used () {
    squeue -u "$USER" -h | wc -l
}

gi () { printf "%.1fGiB" "$(bc -l <<< "$1/1048576")"; }  # kB → GiB (string)


echo "$(timestamp) ---- script start ----" >> "$LOG"

CURRENT_QUEUE=$(queue_used)
FREE=$(kbytes_free)
PFREE=$(( FREE - CURRENT_QUEUE * JOB_SIZE ))  #potential free

echo "current queue ... ${CURRENT_QUEUE}, quota ... $(gi ${PFREE})"
# slots limited by: quota, per-run cap, queue headroom
slots_by_quota=$(( PFREE / JOB_SIZE ))
slots_available=$(( MAX_IN_QUEUE - CURRENT_QUEUE ))
echo "slots ... ${slots_by_quota} ${slots_available}"

SLOTS=$slots_by_quota
(( SLOTS > MAX_PER_RUN ))   && SLOTS=$MAX_PER_RUN
(( SLOTS > slots_available )) && SLOTS=$slots_available


if (( SLOTS <= 0 )); then
    echo "$(timestamp)  HALT  pfree=$(gi $PFREE)  queue=$CURRENT_QUEUE/$MAX_IN_QUEUE" >> "$LOG"
    echo "Nothing to submit: quota or queue limit reached."
    echo "$(timestamp) ---- script end ----" >> "$LOG"
    exit 0
fi

echo "$(timestamp)  INFO pfree=$(gi $PFREE)  queue=$CURRENT_QUEUE/$MAX_IN_QUEUE  slots=$SLOTS" >> "$LOG"

# --------- submit up to $SLOTS brand-new cases ---------------------
for CASE_DIR in $(ls -d $CASE_PATTERN 2>/dev/null | sort); do
    [[ -d $CASE_DIR ]] || continue
    [[ -e $CASE_DIR/.submitted ]] && continue
    (( SLOTS == 0 )) && break

    echo "$(timestamp)  RUN   $CASE_DIR" >> "$LOG"
    CASE=$(basename $CASE_DIR)

    (
        cd "$CASE_DIR"
        echo $JOB_CMD                      # e.g. sbatch run_case.sbatch
	eval "$JOB_CMD"
    )

    touch "$CASE_DIR/.submitted"
    SLOTS=$(( SLOTS - 1 ))
done

echo "$(timestamp) ---- script end ----" >> "$LOG"
