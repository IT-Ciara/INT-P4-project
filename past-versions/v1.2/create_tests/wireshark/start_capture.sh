#!/bin/bash

#empty all pcaps
# Directory containing the .pcap files
DIR="./"

# Loop through each .pcap file in the directory
for file in "$DIR"/*.pcap; do
  # Check if the file exists (in case there are no .pcap files in the directory)
  if [ -f "$file" ]; then
    # Empty the file
    > "$file"
    echo "Emptied: $file"
  fi
done

ls -l

cd ~/P4-projects/create_tests
python3 main.py &


cd 
for i in {1..20}
do
    sudo tshark -i veth0 -i veth2 -i veth4 -i veth6 -i veth8 -i veth10 -i veth12 -i veth14 -i veth16 -i veth18 -i veth20 -i veth22 -i veth24 -i veth26 -w case$i.pcap -a duration:8
done