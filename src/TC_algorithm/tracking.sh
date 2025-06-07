#/bin/bash

hostdir=`pwd`/tracking/

# Read cases from config.yaml
yamlfile="config.yaml"
yamlfile="config_p3k.yaml"
#yamlfile="config_control.yaml"
cases=$(awk '/cases:/ {flag=1; next} /^[[:space:]]*-/ && flag {print $2} /^[^[:space:]]/ && flag && !/cases:/ {flag=0}' ${yamlfile})
outpath=$(awk -F': ' '/output_path:/ {print $2}' ${yamlfile})

for expn in $cases; do
    expfolder="${outpath}/${expn}"
    expname=$expn
    TCdata="${expfolder}/${expname}.TC.nc"
    echo "----------"
    echo ${TCdata}
    echo ${expname}
    echo "----------"

    # Prepare input/output folder
    cd ${hostdir}
    if [ ! -d ./tracking_data ]; then mkdir ./tracking_data; fi
    rm -rf ./tracking_data/*
    ln -sf ${TCdata} ./tracking_data/TC.nc
    #ln -sf /data/W.eddie/SPCAM/LANDmask.dat ./tracking_data/lsm.dat

    # Run tracking
    cd tracking2
    ./iterate.sh
    cd ${hostdir}

    # Copy the results
    outdir="${outpath}/${expname}"
    mkdir -p ${outdir}
    cd tracking_data
    cp irt_objects_mask.dat irt_objects_output.txt ${outdir}
    cp irt_tracks_mask.dat irt_tracks_output.txt ${outdir}
    cp irt_tracklinks_output.txt ${outdir}
    cd ${hostdir}

    # Create the ctl file
    cd ${outdir}
    cp ${hostdir}/DATA/irt_objects_mask.ctl ${hostdir}/DATA/irt_tracks_mask.ctl .

    # Extract datetime part (after the last underscore)
    datetime=${expname##*_}
    
    # Extract components
    yr=${datetime:0:4}
    mo=${datetime:4:2}
    dy=${datetime:6:2}
    hr=${datetime:8:2}
    
    # Output for check
    echo "yr=$yr"
    echo "mo=$mo"
    echo "dy=$dy"
    echo "hr=$hr"
    ddMMyyyy=$(LC_TIME=en_US.utf8 date +%d%b%Y -d "${yr}-${mo}-${dy}")
    sed -i "s/ddMMyyyy/${hr}:00Z${ddMMyyyy}/g" irt_objects_mask.ctl
    sed -i "s/ddMMyyyy/${hr}:00Z${ddMMyyyy}/g" irt_tracks_mask.ctl
    cd ${hostdir}

done
