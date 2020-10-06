#!/bin/bash

# get a list of files
find jsons_corrected/ -name *.json > corrected-list.txt

# replace folder name
sed -i 's/jsons_corrected/all_jsons/g' corrected-list.txt 

for f in $(cat corrected-list.txt)
do
    # find corresponding line in input-list to get result i
    LINE=$(grep -n $f input-list.txt)
    SPLITLINE=(${LINE//:/ })
    INDEX=${SPLITLINE[0]}
    # create list of results to be deleted
    echo results/result_Z3_$INDEX.json >> delete-list.txt
    echo results/result_OMS_$INDEX.json >> delete-list.txt
    echo results/result_BCLT_$INDEX.json >> delete-list.txt
done
