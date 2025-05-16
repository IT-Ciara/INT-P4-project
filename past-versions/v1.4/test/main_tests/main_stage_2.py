#*----------------------------------------------------------------*
# This script is used to run the main tests for Step 3-4
# Step 3 updates the incoming counters
#Step 4. It has a table that checks if the packet is coming from a user port. 
# If it is, it will set a flag in the metadata called user_port.

import sys
import os
import subprocess
import time
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from entries_generator import entries_stage_2
from stats_tracker import tracker_stage_2
from scapy_pkts import pkts_stage_2
import p4_functions as p4f


def verify_stats(stats1,numbers,stats2):
    width = 110
    test_bool = False
    for i in range(0,len(stats1)):
        if stats2[i][2] == stats1[i][2] + numbers[i][1]:
            test_bool = True
    if test_bool:
        print(f"{p4f.get_color('green')}{'='*width}{p4f.get_color('reset')}")
        print(f"{p4f.get_color('green')}{'COUNTERS HAVE BEEN UPDATED CORRECTLY'.center(width)}{p4f.get_color('reset')}")
        print(f"{p4f.get_color('green')}{'='*width}{p4f.get_color('reset')}")
        print(f"{p4f.get_color('green')}{'Results: Pass'}{p4f.get_color('reset')}")
    else:
        print(f"{p4f.get_color('red')}{'='*width}{p4f.get_color('reset')}")
        print(f"{p4f.get_color('red')}{'COUNTERS HAVE NOT BEEN UPDATED CORRECTLY'.center(width)}{p4f.get_color('reset')}")
        print(f"{p4f.get_color('red')}{'='*width}{p4f.get_color('reset')}")
        print(f"{p4f.get_color('red')}{'Results: Failed'}{p4f.get_color('reset')}")





def track_stats_and_send_packets():
    stats1 = tracker_stage_2.main()
    numbers = pkts_stage_2.create_send_pkt(p4f.get_interfaces())    
    time.sleep(2)
    stats2 = tracker_stage_2.main()
    verify_stats(stats1,numbers,stats2)

def main():
    p4f.print_main("Stage 2 Tests")
    parser = argparse.ArgumentParser(description="Step 3-4 script for adding entries, tracking stats, and sending packets.")
    
    # Optional --all flag; if omitted, default to tracking only
    parser.add_argument("--all", action="store_true", help="Run all steps: Add entries, track stats, and send packets.")

    args = parser.parse_args()

    if args.all:
        p4f.add_entries(entries_stage_2)

    track_stats_and_send_packets()

if __name__ == '__main__':
    main()
