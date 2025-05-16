#!/bin/bash

rm -rf *.pcap
for i in {1..50}
do  
    echo "Creating pcap $i"
    touch case$i.pcap
    sudo chmod 777 case$i.pcap

done