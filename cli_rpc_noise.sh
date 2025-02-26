HOST1=$1
c=1
while [ $c -le 50000000 ]
do
#    cat rpclist.txt| sshpass -p password ssh -T -o StrictHostKeyChecking=no user@$1 -p 830 -s netconf

for command in `cat rpclist.txt`
do
    echo "\n==================================================================================="
    echo "Output for $command"
    echo "===================================================================================\n"
    echo $command | sshpass -p password ssh -T -o StrictHostKeyChecking=no user@$1 -p 830 -s netconf | tail -n 10
done
echo "\n Interation $c finished\n"
c=`expr $c + 1`
sleep  60
done
