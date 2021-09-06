#!/bin/bash

SOL_DIR=/home/pabgordi/tosem20/most-called-contracts
RESULTS_OK=/home/pabgordi/tosem20/results/ethir_OK
RESULTS_TIMEOUT=/home/pabgordi/tosem20/results/ethir_TIMEOUT
RESULTS_ERROR=/home/pabgordi/tosem20/results/ethir_ERROR
RESULTS_CLONING=/home/pabgordi/tosem20/results/ethir_CLONING
RESULTS_RBR=/home/pabgordi/tosem20/results/ethir_RBR
RESULTS_SACO=/home/pabgordi/tosem20/results/ethir_SACO
RESULTS_UNKNOWN=/home/pabgordi/tosem20/results/ethir_UNKNOWN_ERROR
ETHIR_DIR=/home/pabgordi/tosem20/syrup/ethir
COSTABS_DIR=/home/pabgordi/tmp/costabs
ETHIR_COMMAND="python3 $ETHIR_DIR/oyente_ethir.py -s"
ETHIR_ARGS=" -b -syrup -storage"
TIMEOUT=210s

rm -rf $SOL_DIR/*.evm $SOL_DIR/*.disasm

SOL_FILES=`ls $SOL_DIR`

echo $SOL_FILES

for SOL in $SOL_FILES; do
    FILENAME=$(basename "$SOL")
    FNAME="${FILENAME%.*}"
    echo timeout $TIMEOUT $ETHIR_COMMAND $SOL_DIR/$SOL $ETHIR_ARGS
    $ETHIR_COMMAND $SOL_DIR/$SOL $ETHIR_ARGS 1> ./logs/$FNAME.log
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
    elif [ $RES -eq "3" ]; then
        echo "$SOL CLONING ERROR"
        cp $SOL_DIR/$SOL $RESULTS_CLONING/
    elif [ $RES -eq "4" ]; then
        echo "$SOL RBR ERROR"
        cp $SOL_DIR/$SOL $RESULTS_RBR/
    elif [ $RES -eq "5" ]; then
        echo "$SOL SACO ERROR"
    	cp $SOL_DIR/$SOL $RESULTS_SACO/
    else
        echo "$SOL ERROR DESCONOCIDO"
        cp $SOL_DIR/$SOL $RESULTS_UNKNOWN/
    fi

done
