HOST1=$1
c=1
while [ $c -le 50000000 ]
do
for mib in `cat miblist.txt`
do
    echo "\n========================================================================"
    echo "Running MIB $mib:"
    echo "========================================================================\n"
    snmpwalk -v 2c -c 4m0nTFB $HOST1 $mib | tail -n 10
done
echo "\n Interation $c finished\n"
c=`expr $c + 1`
sleep  60
done
