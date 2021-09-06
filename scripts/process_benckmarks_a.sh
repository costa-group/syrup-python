#!/bin/bash

SOL_DIR=/home/pabgordi/tosem20/most-called-contracts
RESULTS_OK=/home/pabgordi/tosem20/results-a/SFS_OK
RESULTS_TIMEOUT=/home/pabgordi/tosem20/results-a/SFS_TIMEOUT
RESULTS_ERROR=/home/pabgordi/tosem20/results-a/SFS_ERROR
ETHIR_DIR=/home/pabgordi/tosem20/syrup/ethir
COSTABS_DIR=/home/pabgordi/tmp/costabs
ETHIR_COMMAND="python3 $ETHIR_DIR/oyente_ethir.py -s"
ETHIR_ARGS=" -syrup -storage"
TIMEOUT=210s

rm -rf $SOL_DIR/*.evm $SOL_DIR/*.disasm

mkdir ../results-a/SFS_OK
mkdir ../results-a/SFS_TIMEOUT
mkdir ../results-a/SFS_ERROR
mkdir ../results-a/logs

SOL_FILES=`ls $SOL_DIR`

echo $SOL_FILES

for SOL in $SOL_FILES; do
    FILENAME=$(basename "$SOL")
    FNAME="${FILENAME%.*}"
    echo timeout $TIMEOUT $ETHIR_COMMAND $SOL_DIR/$SOL $ETHIR_ARGS
    $ETHIR_COMMAND $SOL_DIR/$SOL $ETHIR_ARGS 1> ../results-a/logs/$FNAME.log
    RES="$?"

    echo "RESULTADO $RES"

    if [ $RES -eq "0" ]; then
        echo "$SOL OK"
        mkdir $RESULTS_OK/$FNAME
        cp -r $COSTABS_DIR/* $RESULTS_OK/$FNAME
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
