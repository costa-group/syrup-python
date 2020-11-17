#!/bin/bash

PROJECT_DIR=/home/alejandro/repos/syrup-python
FILE_PATH=$PROJECT_DIR/scripts/examples.txt
DEST_DIR=$PROJECT_DIR/jsons/
SRC_DIR=$PROJECT_DIR/examples/blocks

rm -rf $DEST_DIR/*

while read -r line; do 
    cp $SRC_DIR/$line $DEST_DIR/$line
done < $FILE_PATH
