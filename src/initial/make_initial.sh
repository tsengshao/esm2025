#!/usr/bin/bash

#===============================
# Choose dataset: "hourly" or "daily"
# Choose resolution: "f02" or "f09"
dataset="daily"
#dataset="hourly"
res="f02" 

# Set path based on dataset
refpath="/data/C.shaoyu/ESM2025/src/initial/ref_file"
#outpath="/data/C.shaoyu/ESM2025/data/initial"
outpath="./initial"
mkdir -p ${outpath}

#===============================
# Define remap files by resolution
latgrid="${refpath}/${res}slat.txt"
longrid="${refpath}/${res}slon.txt"
fullgrid="${refpath}/${res}.txt"
con_lat="${refpath}/ERA5to${res}slat_con.nc"
con_lon="${refpath}/ERA5to${res}slon_con.nc"
con_full="${refpath}/ERA5to${res}_con.nc"
#===============================

# Function to apply the input file
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

func_get_input_path() {
    # ----- useage -----
    # -- func_get_input_path daily u 2016080100
    # -----
    local dtype=${1} #daily, hourly
    local varn=${2}
    local yyyymmddhh=${3} #yyyymmddhh
    read yr mo dy hr <<< $(func_extract_yyyymmddhh ${yyyymmddhh})
    hourlypath="/data/C.shaoyu/data/era5/cwbgfs_hourly"
    dailypath="/data/dadm1/reanalysis/ERA5"

    # process era5 daily data
    if [ "$dtype" == "daily" ]; then
        local pllist="u v t q z w"
        if [[ "$pllist" =~ "$varn" ]]; then eratype="PRS"; else eratype="SFC"; fi 
        #echo ${varn} ${eratype}
        output="${dailypath}/${eratype}/day/${varn}/${yr}/ERA5_${eratype}_${varn}_${yr}${mo}_r1440x721_day.nc"
        echo ${output}

    # ------ process era hourly with cwbgfs format
    else
        local pllist="o3 clwc q t u v"
        # pl/ERA5_pressure_essentials_2016072900.nc
        if [[ "$pllist" =~ "$varn" ]]; then
            output="${hourlypath}/pl/ERA5_pressure_essentials_${yr}${mo}${dy}${hr}.nc" 
        else
            output="${hourlypath}/sl/ERA5_surface_${yr}${mo}${dy}${hr}.nc" 
        fi 
        echo ${output}
    fi
}

# Function to apply remap
remap() {
    local ifile=$1
    local ofile=$2
    local gridfile=$3
    local confile=$4
    local varn=$5
    local its=$6
    cdo -P 2 remap,$gridfile,$confile \
        -selvar,${varn} \
        -seltimestep,${its} \
        $ifile $ofile
}

#===============================
start_ts=$( date -u -d '2016-08-05 00:00:00' +%s )
end_ts=$( date -u -d '2016-08-06 00:00:00' +%s )
now_ts="${start_ts}"
delta_ts=86400 #[second]

while [ "$now_ts" -lt "$end_ts" ] || \
      [ "$now_ts" -eq "$end_ts" ]; do
    yyyymmddhh=$(date -u -d @$now_ts +'%Y%m%d%H')
    read yr mo dy hr <<< $(func_extract_yyyymmddhh ${yyyymmddhh})
    echo "${yr}-${mo}-${dy} ${hr}"

    # --- process select timestep
    if [ "${dataset}" == "daily" ];then
        day_ts=$( date -u -d "${yr}-${mo}-01 ${hr}:00:00" +%s )
        tstep=$(echo "scale=0; ($now_ts - $day_ts) / 86400" | bc)
        echo ${tstep}
    else
        tstep=1
    fi
    varn=u
    
    outfilelist=""
    # --- process regrid staggered lat
    for varn in u sp; do
        outfile=${outpath}/ERA5_${res}_${varn}slat_${yyyymmddhh}_${dataset}.nc
        remap $(func_get_input_path ${dataset} ${varn} ${yyyymmddhh}) \
              ${outfile} ${latgrid} ${con_lat} ${varn} ${tstep} &
        outfilelist="${outfilelist} ${outfile}"
    done
    wait  

    # --- process regrid staggered lon
    for varn in v sp; do
        outfile=${outpath}/ERA5_${res}_${varn}slon_${yyyymmddhh}_${dataset}.nc
        remap $(func_get_input_path ${dataset} ${varn} ${yyyymmddhh}) \
              ${outfile} ${longrid} ${con_lon} ${varn} ${tstep} &
        outfilelist="${outfilelist} ${outfile}"
    done
    wait  

    # --- process regrid center
    for varn in t q sp; do
        outfile=${outpath}/ERA5_${res}_${varn}_${yyyymmddhh}_${dataset}.nc
        remap $(func_get_input_path ${dataset} ${varn} ${yyyymmddhh}) \
              ${outfile} ${fullgrid} ${con_full} ${varn} ${tstep} &
        outfilelist="${outfilelist} ${outfile}"
    done
    wait
      
    now_ts=$(( now_ts + delta_ts))
    ls -l ${outfilelist}
    exit
done

##     #===============================
##     YR=$yr MON=$mon TYPE=$dataset RES=$res ncl ERA5_Vert_Interpo.ncl
##     #===============================


