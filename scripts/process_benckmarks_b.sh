#!/bin/bash

SOL_DIR=../examples/tosem-benchmarks-b
RESULTS_OK=../results-b/SFS_OK
RESULTS_TIMEOUT=../results-b/SFS_TIMEOUT
RESULTS_ERROR=../results-b/SFS_ERROR
ETHIR_DIR=../ethir
COSTABS_DIR=/tmp/syrup
ETHIR_COMMAND="python3 $ETHIR_DIR/oyente_ethir.py -s"
ETHIR_ARGS=" -b -syrup -storage"
TIMEOUT=210s

rm -rf $SOL_DIR/*.evm $SOL_DIR/*.disasm
rm -rf ../results-b
rm -rf /tmp/syrup

mkdir /tmp/syrup
mkdir ../results-b
mkdir ../results-b/SFS_OK
mkdir ../results-b/SFS_TIMEOUT
mkdir ../results-b/SFS_ERROR
mkdir ../results-b/logs
mkdir ../results-b/sfs-b

echo ls $SOL_DIR
SOL_FILES=`ls $SOL_DIR`

echo $SOL_FILES

for SOL in $SOL_FILES; do
    FILENAME=$(basename "$SOL")
    FNAME="${FILENAME%.*}"
    echo timeout $TIMEOUT $ETHIR_COMMAND $SOL_DIR/$SOL $ETHIR_ARGS
    $ETHIR_COMMAND $SOL_DIR/$SOL $ETHIR_ARGS 1> ../results-b/logs/$FNAME.log
    RES="$?"

    echo "RESULTADO $RES"

    if [ $RES -eq "0" ]; then
        echo "$SOL OK"
        mkdir $RESULTS_OK/$FNAME
        cp -r $COSTABS_DIR/* $RESULTS_OK/$FNAME
        cp $COSTABS_DIR/jsons/* ../results-b/sfs-b
        cp $SOL_DIR/$SOL $RESULTS_OK/$FNAME
        
    elif [ $RES -eq "124" ]; then
        echo "$SOL BASH TIMEOUT"
        cp $SOL_DIR/$SOL $RESULTS_TIMEOUT/
    elif [ $RES -eq "1" ]; then
        echo "$SOL OYENTE ERROR"
        cp $SOL_DIR/$SOL $RESULTS_ERROR/
    elif [ $RES -eq "2" ]; then
        echo "$SOL OYENTE TIMEOUT"
        cp $SOL_DIR/$SOL $RESULTS_TIMEOUT/
    else
        echo "$SOL ERROR DESCONOCIDO"
        cp $SOL_DIR/$SOL $RESULTS_UNKNOWN/
    fi

done
