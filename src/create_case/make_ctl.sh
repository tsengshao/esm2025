#!/bin/bash

# ====== Function Start ======
func_extract_yyyymmddhh() {
    # ----- useage -----
    # -- func_extract_yyyymmddhh 2016080100
    # -- read yr mo dy hr <<< $(func_extract_yyyymmddhh 2016080100)
    # -----
    local yr=$(echo ${1}|cut -c1-4)
    local mo=$(echo ${1}|cut -c5-6)
    local dy=$(echo ${1}|cut -c7-8)
    local hr=$(echo ${1}|cut -c9-10)
    echo ${yr} ${mo} ${dy} ${hr}
}

func_mo2MON() {
    case $1 in
        01|1)  echo JAN;;
        02|2)  echo FEB;;
        03|3)  echo MAR;;
        04|4)  echo APR;;
        05|5)  echo MAY;;
        06|6)  echo JUN;;
        07|7)  echo JUL;;
        08|8)  echo AUG;;
        09|9)  echo SEP;;
        10)    echo OCT;;
        11)    echo NOV;;
        12)    echo DEC;;
        *)     echo "??" ;;
    esac
}

# ====== Function End ======
export archive="/work1/umbrella0c/taiesm_work/archive/"
res='f02'
compset='F2000'
start_ts=$( date -u -d '2016-08-01 00:00:00' +%s )
end_ts=$( date -u -d '2016-08-02 00:00:00' +%s )
now_ts="${start_ts}"
delta_ts=86400 #[second]

while [ "$now_ts" -lt "$end_ts" ] || \
      [ "$now_ts" -eq "$end_ts" ]; do
    yyyymmddhh=$(date -u -d @$now_ts +'%Y%m%d%H')
    read yr mo dy hr <<< $(func_extract_yyyymmddhh ${yyyymmddhh})
    ## casename="${res}.${compset}.hindcast_${yr}${mo}${dy}${hr}"
    casename="${res}.${compset}.hindcast_${yr}${mo}${dy}${hr}"

    echo "CTL ... ${casename} ... creating"

    # ====== ctl file ======
    # f02.F2000.hindcast_2016080100.cam.h1.2016-08-03-00000.nc
    fname="${archive}/${casename}/atm/hist_h1.ctl"
    MON=$(func_mo2MON ${mo})
    echo "
    dset ^hist/${casename}.cam.h1.%y4-%m2-%d2-00000.nc
    options template 365_day_calendar
    tdef time  289  linear 00Z${dy}${MON}${yr} 1hr
    " > ${fname}
    
    # ====== ctl file ======
    fname="${archive}/${casename}/atm/hist_h2.ctl"
    MON=$(func_mo2MON ${mo})
    echo "
    dset ^hist/${casename}.cam.h2.%y4-%m2-%d2-00000.nc
    options template 365_day_calendar
    tdef time  289  linear 00Z${dy}${MON}${yr} 1hr
    " > ${fname}

    now_ts=$(( ${now_ts} + ${delta_ts} ))
done 



