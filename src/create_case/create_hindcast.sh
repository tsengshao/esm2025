#!/bin/sh

# CESM code directory ###
export CCSMROOT=/home/j07hsu00/taiesm/ver250204

# Cases directory ###
export MYRUNS=$PWD

# ======================================
# Function to apply the input file
# ==========
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

# ==========

# ==========
# Function
# =====================================

res='f02'
compset='F2000'
start_ts=$( date -u -d '2016-08-02 00:00:00' +%s )
end_ts=$( date -u -d '2016-11-01 00:00:00' +%s )
now_ts="${start_ts}"
delta_ts=86400 #[second]

while [ "$now_ts" -lt "$end_ts" ] || \
      [ "$now_ts" -eq "$end_ts" ]; do
    yyyymmddhh=$(date -u -d @$now_ts +'%Y%m%d%H')
    read yr mo dy hr <<< $(func_extract_yyyymmddhh ${yyyymmddhh})
    ## casename="${res}.${compset}.hindcast_${yr}${mo}${dy}${hr}"
    casename="${res}.${compset}.hindcast_${yr}${mo}${dy}${hr}"
     
    echo "------------"
    echo "create ${casename}"
    echo "------------"
    if [ -d ${casename} ]; then rm -rf ${casename}; fi

    cd ${MYRUNS}
   
    # ======== create case ========== 
    # Case name ###
    export CASE=$MYRUNS/${casename}
    # create newcase ###
    cd $CCSMROOT/scripts
    dum=$(echo ${compset}| cut -c1)
    dum2=$(echo ${compset}| cut -c2-)
    ./create_newcase -case ${CASE} -mach f1 -compset ${dum}_${dum2}_TAI -res ${res}_${res} -mpilib impi -compiler intel

    cd ${CASE}
    # ------ 
    # -- change env_mach 
    # ------ 
    ./xmlchange NTASKS_ATM=1920,NTASKS_LND=1920,NTASKS_ICE=1920
    ./xmlchange NTASKS_OCN=1920,NTASKS_CPL=1920,NTASKS_GLC=1920
    ./xmlchange NTASKS_ROF=1920,NTASKS_WAV=1920
    ./xmlchange MAX_TASKS_PER_NODE=96,PES_PER_NODE=96

    ./cesm_setup

    # ------ 
    # -- change the model setting and inital condiction ------
    # ------ 
    # ---- env_run.xml // sst, simulation day
    tstr="${yr}-${mo}-${dy}"
    ./xmlchange RUN_STARTDATE=$tstr,RUN_REFDATE=$tstr
    ./xmlchange SSTICE_DATA_FILENAME=/work1/j07hcl00/inidata/OISST_BC/sst_OISST-V2_bc_0.23x0.31_20150101-20250101_c250401.nc,SSTICE_YEAR_ALIGN=${yr},SSTICE_YEAR_START=2015,SSTICE_YEAR_END=2025
    ./xmlchange STOP_OPTION=nday,STOP_N=12

    # ---- env_run.xml // open pnetcdf output
    ./xmlchange PIO_TYPENAME=pnetcdf,OCN_PIO_TYPENAME=pnetcdf
    ./xmlchange LND_PIO_TYPENAME=pnetcdf,ROF_PIO_TYPENAME=pnetcdf
    ./xmlchange ICE_PIO_TYPENAME=pnetcdf,ATM_PIO_TYPENAME=pnetcdf
    ./xmlchange CPL_PIO_TYPENAME=pnetcdf,GLC_PIO_TYPENAME=pnetcdf
    ./xmlchange WAV_PIO_TYPENAME=pnetcdf
    ./xmlchange REST_OPTION=never

    # ---- cp source code -----
    cp /work1/umbrella0c/taiesm/src/create_case/cam_diagnostics.F90
 ./SourceMods/src.cam/
    
    echo "
    avgflag_pertape =   'A',   'I', 'A'
    mfilt           =     1,    24,  24
    nhtfrq          =     0,    -1,  -1

    fincl2  = 'U','V','OMEGA','Q','T','Z3',
              'TMQ','PS','PSL','SST',
              'U10','U850','V850','U300','V300'
    fincl3  = 'PRECT', 'LHFLX', 'SHFLX',
              'FSNT',   'FLNT',  'FSNS', 'FLNS',
              'FSNTC', 'FLNTC', 'FSNSC', 'FLNSC',

    ncdata = '/work1/umbrella0c/taiesm_initial/ERA5_f02/${yr}${mo}/ERA5_f02_${yyyymmddhh}_hourly_initial.nc'
    " >> user_nl_cam

    # ------ 
    # -- modify slurm setting
    # ------
    fname=$(ls *.run)
    echo ${fname}
    sed -i 's/--account=MST113255/--account=MST111414/g' ${fname}

    # ------ 
    # -- build and submit --
    # ------ 
    ./*.build
    #./*.submit
    
    now_ts=$(( ${now_ts} + ${delta_ts} ))
done

# ====== prepare ctl file ======
MON=$(func_mo2MON ${mm})
ctl="
echo 
dset ^hist/${casename}.cam.h1.%y4-%m2-%d2-00000.nc
options template 365_day_calendar
tdef time  289  linear 00Z${dy}${MON}${yr} 1hr
"

