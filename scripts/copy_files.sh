#!/bin/bash

PROJECT_DIR=/home/alejandro/repos/syrup-backend-python
FILE_PATH=$PROJECT_DIR/scripts/examples.txt
DEST_DIR=$PROJECT_DIR/experiments/examples/
SRC_DIR=$PROJECT_DIR/examples/ebso-comparison

rm -rf $DEST_DIR/*

while read -r line; do 
    cp $SRC_DIR/$line $DEST_DIR/$line
done < $FILE_PATH
