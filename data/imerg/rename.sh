#!/bin/bash

# slightly malformed input data
input_start=$(date -d "2016-08-01 00:00:00" '+%s')
input_end=$(date -d "2016-11-01 00:00:00" '+%s')
#dir="/nwpr/gfs/xb117/shao/2024final/rawdata/imerg/GPM_3IMERGHH.07/"
dir="/data/dadm1/obs/GPM_IMERG/GPM_3IMERGHH.07/"
#GPM_3IMERGHH.07/2010/204/3B-HHR.MS.MRG.3IMERG.20100723-S063000-E065959.0390.V07B.HDF5


lfile="clog.lg"
echo "$(date)" > ${lfile}
echo "check from -- $(date -d "@${input_start}" '+%Y-%m-%d %H:%M:%S')" >> ${lfile}
echo "check to   -- $(date -d "@${input_end}" '+%Y-%m-%d %H:%M:%S')"  >> ${lfile}
echo " ------ missing ------" >> ${lfile}

d="$input_start"
while [ "${input_end}" -gt "${d}" ]; do
  nowdate=$(date -d "@${d}" '+%Y-%m-%d %H:%M:%S')

  date=$(date -d "@${d}" '+%Y%m%d')
  year=$(date -d "@${d}" '+%Y')
  mo=$(date -d "@${d}" '+%m')
  julian=$(date -d "@${d}" '+%j')
  stime=$(date -d "@${d}" '+%H%M%S')
  d2=$(expr ${d} + 1800 - 1)
  etime=$(date -d "@${d2}" '+%H%M%S')
  d0=$( echo "$(( ( ${d} - $(date -d "${date}" '+%s') ) / 1800 * 30 ))" )
  dt=$(printf "%04d" ${d0})

  echo ${julian} ${date} ${stime} ${etime} ${d0}
  fpath="${dir}/${year}/${julian}/3B-HHR.MS.MRG.3IMERG.${date}-S${stime}-E${etime}.${dt}.V07B.HDF5"
  link="https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHH.07/${year}/${julian}/3B-HHR.MS.MRG.3IMERG.${date}-S${stime}-E${etime}.${dt}.V07B.HDF5"
  if [ ! -f ${fpath} ]; then
    #echo "${fpath}" >> ${lfile}
    echo ${link} >> ${lfile}
  fi
  if [ -f ${fpath} ]; then
    outdir="./all_rename/${year}${mo}/"
    mkdir -p ${outdir}
    ln -sf ${fpath} ${outdir}/imerg_${date}_${stime}.HDF5
  fi

  d=$(expr ${d} + 1800)
done
