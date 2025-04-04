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
from entries_generator import entries_step_8_9_10
from stats_tracker import tracker_step_8_9_10
from scapy_pkts import pkts_step_8_9_10
width = 120
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"  # Reset to default color
GREY = "\033[90m"



def add_entries():
    width = 100
    print("\n\n")
    print(f"{GREY}{'='*width}{RESET}")
    print(f"{GREY}{'A D D I N G   E N T R I E S'.center(width)}{RESET}")
    print(f"{GREY}{'='*width}{RESET}")

    command = """
    cd /root/mysde/bf-sde-9.13.4
    . ../tools/set_sde.bash
    ./run_bfshell.sh -b ~/code/v1.4/test/entries_generator/entries_step_8_9_10.py
    """
    try:
        subprocess.run(command, shell=True, executable="/bin/bash", check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

    print("-"*width)
    print("\n")

def track_stats_and_send_packets():
    tracker_step_8_9_10.main()
    pkts_step_8_9_10.create_send_pkt()
    print("Done")
    time.sleep(2)
    tracker_step_8_9_10.main()

def main():
    print("\n")
    print(f"{BLUE}{'='*width}{RESET}")
    print(f"{BLUE}{'='*width}{RESET}")
    print(f"{BLUE}{' S T E P   8  ,  9   A N D   10  T E S T S'.center(width)}{RESET}")
    print(f"{BLUE}{'='*width}{RESET}")
    print(f"{BLUE}{'='*width}{RESET}")
    
    parser = argparse.ArgumentParser(description="Step 8_9_10 script for adding entries, tracking stats, and sending packets.")
    
    # Optional --all flag; if omitted, default to tracking only
    parser.add_argument("--all", action="store_true", help="Run all steps: Add entries, track stats, and send packets.")

    args = parser.parse_args()

    if args.all:
        add_entries()

    track_stats_and_send_packets()

if __name__ == '__main__':
    main()
