#!/bin/bash

csvsql --query 'SELECT SUM("gas saved") FROM result' result.csv 
