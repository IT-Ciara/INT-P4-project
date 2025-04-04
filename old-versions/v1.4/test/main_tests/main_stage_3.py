#*----------------------------------------------------------------*
# This script is used to run the main tests for Step 5-6.
# Step 5 is realed to a table to check if it's an sd trace after checking that is coming from an
# user port. They key is the ethernet src address. 
# if it matches the eth src address, then it will send it to the cpu port. 

import sys
import os
import subprocess
import time
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from entries_generator import entries_stage_3
from stats_tracker import tracker_stage_3
from scapy_pkts import pkts_stage_3
import p4_functions as p4f

# def add_entries():
#     width = 100
#     print("\n\n")
#     print(f"{GREY}{'='*width}{RESET}")
#     print(f"{GREY}{'A D D I N G   E N T R I E S'.center(width)}{RESET}")
#     print(f"{GREY}{'='*width}{RESET}")
#     entries_stage_3.main()


def track_stats_and_send_packets():
    tracker_stage_3.main()
    pkts_stage_3.create_send_pkt(["veth0"])
    time.sleep(2)
    tracker_stage_3.main()

def main():
    p4f.print_main("Stage 3 Tests")
    parser = argparse.ArgumentParser(description="Step 5-6 script for adding entries, tracking stats, and sending packets.")
    
    # Optional --all flag; if omitted, default to tracking only
    parser.add_argument("--all", action="store_true", help="Run all steps: Add entries, track stats, and send packets.")

    args = parser.parse_args()

    if args.all:
        p4f.add_entries(entries_stage_3)

    track_stats_and_send_packets()

if __name__ == '__main__':
    main()
