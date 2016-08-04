#!/bin/bash

load5=`uptime | awk '{printf $(NF)}'`
cpus=`nproc`

cpuusage=$(awk "BEGIN {printf \"%.f%%\",${load5}*100/${cpus}}")
ramusage=`free | awk 'NR==2{printf "%.f%%",$3*100/$2}'`

echo c:$cpuusage m:$ramusage
