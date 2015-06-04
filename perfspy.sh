#!/bin/bash
# Run an experiment, capturing performance data using perfspy in the background,
# which gets saved to OUTDIR/trace_N, where N is the experiment number (will get
# incremented automatically).
#
# Author Pablo Llopis <pablo.llopis@gmail.com>

PYPROCSTAT="/home/pablo/coolr-pablo/pyprocstat/pyprocstat.py -s 0.1"
OUTDIR=/home/pablo/coolr-pablo/experiments

nextindex () {
    nextfile="$1"
    i=1
    while [[ -e "${nextfile}_${i}" ]]
    do
        let i++
    done
    echo -n $i
}

if (( $# < 1 ))
then
    echo "Usage: $0 <command>"
    exit 1
fi

next=$(nextindex ${OUTDIR}/trace)
${PYPROCSTAT} &> ${OUTDIR}/trace_${next} &
pid=$!
echo "$@" > ${OUTDIR}/out_${next} 
"$@" &>> ${OUTDIR}/out_${next}
echo "Saved as out_${next}"
kill $pid
