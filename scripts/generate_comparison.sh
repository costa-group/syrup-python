#!/bin/bash

PROJECT_DIR=/home/alejandro/repos/syrup-python
FILES_DIR=$PROJECT_DIR/experiments/examples
LOG_FILE=$PROJECT_DIR/experiments/analyzing_log.txt
RESULTS_FILE=$PROJECT_DIR/experiments/analyzing_results.txt
SOL_DIR=$PROJECT_DIR/experiments/comparison
TIMEOUT=90s


Z3_PATH=$PROJECT_DIR/bin/z3
Z3_COMMAND="$Z3_PATH"
Z3_ARGS=" -smt2"
Z3_OUT1=$SOL_DIR/out1.txt
Z3_OUT2=$SOL_DIR/out2.txt

SYRUP_BACKEND_PATH=$PROJECT_DIR/bin/syrup_backend
SYRUP_BACKEND_COMMAND="$SYRUP_BACKEND_PATH"
SYRUP_BACKEND_ARGS=" -solver Z3 -write-only"
SYRUP_BACKEND_SMT_FILE_PATH=$FILES_DIR/encoding_Z3.smt2
SYRUP_BACKEND_OBJECTIVES=$FILES_DIR/objectives.smt2
SYRUP_BACKEND_MAP=$FILES_DIR/instruction.map


SYRUP_PYTHON_PATH=$PROJECT_DIR/python-syrup-backend/python-syrup.py
SYRUP_PYTHON_COMMAND="$SYRUP_PYTHON_PATH"
SYRUP_PYTHON_SMT_FILE_DIR=$FILES_DIR
SYRUP_PYTHON_SMT_FILE_PATH=$SYRUP_PYTHON_SMT_FILE_DIR/encoding_Z3.smt2
SYRUP_PYTHON_ARGS=" -out $SYRUP_PYTHON_SMT_FILE_DIR"

rm -rf $SOL_DIR/*
rm $LOG_FILE
rm $RESULTS_FILE

BLOCK_FILES=`ls $FILES_DIR`

correct=0
tout=0
toutocaml=0
toutpython=0

for BLOCK in $BLOCK_FILES; do
    FILENAME=$(basename "$BLOCK")
    FNAME="${FILENAME%.*}"
    echo "Analyzing file ${BLOCK}" >> $LOG_FILE
    
    $SYRUP_BACKEND_COMMAND $FILES_DIR/$BLOCK $SYRUP_BACKEND_ARGS
    timeout $TIMEOUT $Z3_COMMAND $SYRUP_BACKEND_SMT_FILE_PATH  $Z3_ARGS > $Z3_OUT1
    RES="$?"
    
    rm $SYRUP_BACKEND_SMT_FILE_PATH
    rm $SYRUP_BACKEND_MAP
    rm $SYRUP_BACKEND_OBJECTIVES

    if [ $RES -eq "124" ]; then
        ((tout++))
        ((toutocaml++))

        $SYRUP_PYTHON_COMMAND $FILES_DIR/$BLOCK $SYRUP_PYTHON_ARGS
        timeout $TIMEOUT $Z3_COMMAND $SYRUP_PYTHON_SMT_FILE_PATH $Z3_ARGS > $Z3_OUT2 
        RES="$?"
        if [ $RES -eq "124" ]; then
            ((toutpython++))
        fi
        continue
    fi

    $SYRUP_PYTHON_COMMAND $FILES_DIR/$BLOCK $SYRUP_PYTHON_ARGS
    timeout $TIMEOUT $Z3_COMMAND $SYRUP_PYTHON_SMT_FILE_PATH $Z3_ARGS > $Z3_OUT2
    RES="$?"
    rm $SYRUP_PYTHON_SMT_FILE_PATH
    if [ $RES -eq "124" ]; then
        ((toutpython++))
    else
        ((correct++))
        cat $Z3_OUT1 $Z3_OUT2 >> $SOL_DIR/$FNAME.txt 
    fi
done

rm $Z3_OUT1
rm $Z3_OUT2


echo "Number of correct comparisons: ${correct}" >> $RESULTS_FILE
echo "Number of incorrect comparisons: ${tout}" >> $RESULTS_FILE
echo "Number of OCAML version comparisons: ${toutocaml}" >> $RESULTS_FILE
echo "Number of Python version comparisons: ${toutpython}" >> $RESULTS_FILE

