#*----------------------------------------------------------------*
# This script is used to run the main tests for Step 3-4
# Step 3 updates the incoming counters
#Step 4. It has a table that checks if the packet is coming from a user port. 
# If it is, it will set a flag in the metadata called user_flag.

import sys
import os
import subprocess
import time
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from entries_generator import entries_step_3_4
from stats_tracker import tracker_step_3_4
from scapy_pkts import pkts_step_3_4

import subprocess
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
    ./run_bfshell.sh -b ~/code/v1.4/test/entries_generator/entries_step_3_4.py
    """
    try:
        subprocess.run(command, shell=True, executable="/bin/bash", check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    print("-"*width)
    print("\n")


def verify_stats(stats1,numbers,stats2):
    width = 110
    test_bool = False
    for i in range(0,len(stats1)):
        if stats2[i][2] == stats1[i][2] + numbers[i][1]:
            test_bool = True
    if test_bool:
        print(f"{GREEN}{'='*width}{RESET}")
        print(f"{GREEN}{'COUNTERS HAVE BEEN UPDATED CORRECTLY'.center(width)}{RESET}")
        print(f"{GREEN}{'='*width}{RESET}")
        print(f"{GREEN}{'Results: Pass'}{RESET}")
    else:
        print(f"{RED}{'='*width}{RESET}")
        print(f"{RED}{'COUNTERS HAVE NOT BEEN UPDATED CORRECTLY'.center(width)}{RESET}")
        print(f"{RED}{'='*width}{RESET}")
        print(f"{RED}{'Results: Failed'}{RESET}")




def track_stats_and_send_packets():
    
    stats1 = tracker_step_3_4.main()
    interfaces = ["veth0", "veth2", "veth4", "veth6","veth8",
              "veth10","veth12","veth14","veth16","veth18",
                "veth20","veth22","veth24","veth26","veth28"]
    numbers = pkts_step_3_4.create_send_pkt(interfaces)
    time.sleep(2)
    stats2 = tracker_step_3_4.main()
    verify_stats(stats1,numbers,stats2)

def main():
    print("\n")
    print(f"{BLUE}{'='*width}{RESET}")
    print(f"{BLUE}{'='*width}{RESET}")
    print(f"{BLUE}{' S T E P   3   A N D   4  T E S T S'.center(width)}{RESET}")
    print(f"{BLUE}{'='*width}{RESET}")
    print(f"{BLUE}{'='*width}{RESET}")

    parser = argparse.ArgumentParser(description="Step 5-6 script for adding entries, tracking stats, and sending packets.")
    
    # Optional --all flag; if omitted, default to tracking only
    parser.add_argument("--all", action="store_true", help="Run all steps: Add entries, track stats, and send packets.")

    args = parser.parse_args()

    if args.all:
        add_entries()

    track_stats_and_send_packets()

if __name__ == '__main__':
    main()
