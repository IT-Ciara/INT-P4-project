#*----------------------------------------------------------------*
# This script is used to run the main tests for Step 8_9_10.
# Step 5 is realed to a table to check if it's an sd trace after checking that is coming from an
# user port. They key is the ethernet src address. 
# if it matches the eth src address, then it will send it to the cpu port. 

import sys
import os
import subprocess
import time
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from entries_generator import entries_stage_4
from stats_tracker import tracker_stage_4
from scapy_pkts import pkts_stage_4
import p4_functions as p4f



def track_stats_and_send_packets():
    tracker_stage_4.main()
    pkts_stage_4.create_send_pkt()
    print("Done")
    time.sleep(2)
    tracker_stage_4.main()

def main():
    p4f.print_main("Stage 4 Tests")
    parser = argparse.ArgumentParser(description="Step 8_9_10 script for adding entries, tracking stats, and sending packets.")
    
    # Optional --all flag; if omitted, default to tracking only
    parser.add_argument("--all", action="store_true", help="Run all steps: Add entries, track stats, and send packets.")

    args = parser.parse_args()

    if args.all:
        p4f.add_entries(entries_stage_4)

    track_stats_and_send_packets()

if __name__ == '__main__':
    main()
