#!/bin/bash
echo "Hello World"
echo "Fifo starting in 5s"


# Loop forever (until break is issued)
while true; do

Year=`date +%Y`
Month=`date +%m`
Day=`date +%d`
Hour=`date +%H`
Minute=`date +%M`
Second=`date +%S`
echo `date`
echo "Current Date is: $Day-$Month-$Year"
echo "Current Time is: $Hour:$Minute:$Second"
echo "Local Time is: [$Year-$Month-$Day $Hour:$Minute:$Second]"

echo "Fifo starting in 5s"


#sleep
echo "Wait for 5 seconds to Kill processes"
sleep 5
echo "Completed"


#ps aux  |  grep -i csp_build  |  awk '{print $2}'  |  xargs sudo kill -9
ps aux  |  grep -i a1pyprox.py  |  awk '{print $2}'  |  xargs kill -9
ps aux  |  grep -i a1pyprox.py  |  awk '{print $2}'  |  xargs kill -9

echo "Wait for 10 seconds to start /xxxxxx.sh"
sleep 10
echo "Completed" 

#nohup ./run_fifo_.sh &

nohup ./run_fifo_.sh >> "./logfile.$(date +'%Y-%m-%d').log"   &


echo "Wait for  1  hours to loop"
sleep  3600
echo "Completed"


done

 
