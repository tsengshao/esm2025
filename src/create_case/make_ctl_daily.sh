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

ctl_h2(){
cat <<EOF
dset ^hist/${1}.cam.h2.%y4-%m2-%d2-00000.nc
options template 365_day_calendar
title UNSET
undef 9.96921e+36
dtype netcdf
xdef 1152 linear 0 0.3125
ydef 768 linear -90 0.234681
zdef 30 levels 992.556 976.325 957.485 936.198 912.645 887.02 859.535 820.858
 763.404 691.389 609.779 524.687 445.993 379.101 322.242 273.911 232.829 197.908
 168.225 142.994 121.547 103.317 87.8212 72.0125 54.5955 38.2683 24.6122 14.3566
 7.59482 3.64347
tdef  12  linear 00Z${2} 1dy
vars 27
hyam=>hyam  30  z  hybrid A coefficient at layer midpoints
hybm=>hybm  30  z  hybrid B coefficient at layer midpoints
date=>date  0  t  current date (YYYYMMDD)
datesec=>datesec  0  t  current seconds of current date
nlon=>nlon  0  y  number of longitudes
wnummax=>wnummax  0  y  cutoff Fourier wavenumber
gw=>gw  0  y  gauss weights
ndcur=>ndcur  0  t  current day (from base day)
nscur=>nscur  0  t  current seconds of current day
co2vmr=>co2vmr  0  t  co2 volume mixing ratio
ch4vmr=>ch4vmr  0  t  ch4 volume mixing ratio
n2ovmr=>n2ovmr  0  t  n2o volume mixing ratio
f11vmr=>f11vmr  0  t  f11 volume mixing ratio
f12vmr=>f12vmr  0  t  f12 volume mixing ratio
sol_tsi=>sol_tsi  0  t  total solar irradiance
nsteph=>nsteph  0  t  current timestep
FLNS=>flns  0  t,y,x  Net longwave flux at surface
FLNSC=>flnsc  0  t,y,x  Clearsky net longwave flux at surface
FLNT=>flnt  0  t,y,x  Net longwave flux at top of model
FLNTC=>flntc  0  t,y,x  Clearsky net longwave flux at top of model
FSNS=>fsns  0  t,y,x  Net solar flux at surface
FSNSC=>fsnsc  0  t,y,x  Clearsky net solar flux at surface
FSNT=>fsnt  0  t,y,x  Net solar flux at top of model
FSNTC=>fsntc  0  t,y,x  Clearsky net solar flux at top of model
LHFLX=>lhflx  0  t,y,x  Surface latent heat flux
PRECT=>prect  0  t,y,x  Total (convective and large-scale) precipitation rate (liq + ice)
SHFLX=>shflx  0  t,y,x  Surface sensible heat flux
endvars
EOF
}

ctl_h1(){
cat <<EOF
dset ^hist/${1}.cam.h1.%y4-%m2-%d2-00000.nc
options template 365_day_calendar
title UNSET
undef 9.96921e+36
dtype netcdf
xdef 1152 linear 0 0.3125
ydef 768 linear -90 0.234681
zdef 30 levels 992.556 976.325 957.485 936.198 912.645 887.02 859.535 820.858
 763.404 691.389 609.779 524.687 445.993 379.101 322.242 273.911 232.829 197.908
 168.225 142.994 121.547 103.317 87.8212 72.0125 54.5955 38.2683 24.6122 14.3566
 7.59482 3.64347
tdef 12  linear 00Z${2} 1dy
vars 31
hyam=>hyam  30  z  hybrid A coefficient at layer midpoints
hybm=>hybm  30  z  hybrid B coefficient at layer midpoints
date=>date  0  t  current date (YYYYMMDD)
datesec=>datesec  0  t  current seconds of current date
nlon=>nlon  0  y  number of longitudes
wnummax=>wnummax  0  y  cutoff Fourier wavenumber
gw=>gw  0  y  gauss weights
ndcur=>ndcur  0  t  current day (from base day)
nscur=>nscur  0  t  current seconds of current day
co2vmr=>co2vmr  0  t  co2 volume mixing ratio
ch4vmr=>ch4vmr  0  t  ch4 volume mixing ratio
n2ovmr=>n2ovmr  0  t  n2o volume mixing ratio
f11vmr=>f11vmr  0  t  f11 volume mixing ratio
f12vmr=>f12vmr  0  t  f12 volume mixing ratio
sol_tsi=>sol_tsi  0  t  total solar irradiance
nsteph=>nsteph  0  t  current timestep
OMEGA=>omega  30  t,z,y,x  Vertical velocity (pressure)
PS=>ps  0  t,y,x  Surface pressure
PSL=>psl  0  t,y,x  Sea level pressure
Q=>q  30  t,z,y,x  Specific humidity
SST=>sst  0  t,y,x  sea surface temperature
T=>t  30  t,z,y,x  Temperature
TMQ=>tmq  0  t,y,x  Total (vertically integrated) precipitable water
U=>u  30  t,z,y,x  Zonal wind
U10=>u10  0  t,y,x  10m wind speed
U300=>u300  0  t,y,x  Zonal wind at 300 mbar pressure surface
U850=>u850  0  t,y,x  Zonal wind at 850 mbar pressure surface
V=>v  30  t,z,y,x  Meridional wind
V300=>v300  0  t,y,x  Meridional wind at 300 mbar pressure surface
V850=>v850  0  t,y,x  Meridional wind at 850 mbar pressure surface
Z3=>z3  30  t,z,y,x  Geopotential Height (above sea level)
endvars
EOF
}

# ====== Function End ======
#export archive="/work1/umbrella0c/taiesm_work/archive/"
#export archive="/data/C.shaoyu/TaiESM/archive/"
export archive="/data/C.shaoyu/TaiESM/archive/daily/f02.F2000.hindcast_SST2015/"
case_header='hindcast_SST2015'
#case_header='hindcast'
res='f02'
compset='F2000'
start_ts=$( date -u -d '2016-08-01 00:00:00' +%s )
end_ts=$( date -u -d '2016-11-01 00:00:00' +%s )
now_ts="${start_ts}"
delta_ts=86400 #[second]

while [ "$now_ts" -lt "$end_ts" ] || \
      [ "$now_ts" -eq "$end_ts" ]; do
    yyyymmddhh=$(date -u -d @$now_ts +'%Y%m%d%H')
    read yr mo dy hr <<< $(func_extract_yyyymmddhh ${yyyymmddhh})
    echo ${yr}${mo}${dy}${hr}
    ## casename="${res}.${compset}.hindcast_${yr}${mo}${dy}${hr}"
    casename="${res}.${compset}.${case_header}_${yr}${mo}${dy}${hr}"

    echo "CTL ... ${casename} ... creating"

    # ====== ctl file ======
    # f02.F2000.hindcast_2016080100.cam.h1.2016-08-03-00000.nc
    fname="${archive}/${casename}/atm/hist_h1.ctl"
    MON=$(func_mo2MON ${mo})
    ctl_h1 ${casename} ${dy}${MON}${yr} > ${fname}
    
    # ====== ctl file ======
    fname="${archive}/${casename}/atm/hist_h2.ctl"
    MON=$(func_mo2MON ${mo})
    ctl_h2 ${casename} ${dy}${MON}${yr} > ${fname}

    now_ts=$(( ${now_ts} + ${delta_ts} ))
done 




