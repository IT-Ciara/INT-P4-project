import sys
import os
import subprocess
import time
import argparse
import signal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from entries_generator import entries_stage_6
from scapy_pkts import pkts_stage_6
import p4_functions as p4f


tshark_process = None  # To store the running tshark process
pcap_file = "./captured_pkts.pcap"  # File to store captured packets

def start_packet_capture():
    """Start tshark to capture packets on all veth interfaces."""
    global tshark_process
    veth_pairs = [f"veth{i}" for i in range(0, 32, 2)]
    
    if not veth_pairs:
        print(f"{p4f.get_color('RED')}No veth pairs found!{p4f.get_color('RESET')}")
        return
    
    # -i veth0 -i veth2 -i veth4 -i veth6 -i veth8 -i veth10 -i veth12 -i veth14 -i veth16 -i veth18 -i veth20 -i veth22 -i veth24 -i veth26 -i veth28 -i veth30
    # Construct the tshark command with multiple interfaces
    interface_args = " ".join(f"-i {veth}" for veth in veth_pairs)
    cmd = f"tshark {interface_args} -w {pcap_file} -a duration:6 &"
    
    print(f"{p4f.get_color('YELLOW')}Starting packet capture on: {', '.join(veth_pairs)}{p4f.get_color('RESET')}")
    tshark_process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)

def count_pkts():
    print(f"{p4f.get_color('GREEN')}Packet capture complete.{p4f.get_color('RESET')}")
    # Count the number of captured packets
    count_cmd = f"tshark -r {pcap_file} | wc -l"
    try:
        count_output = subprocess.check_output(count_cmd, shell=True).decode().strip()
        print(f"{p4f.get_color('GREEN')}Captured Packets: {count_output}{p4f.get_color('RESET')}")
    except subprocess.CalledProcessError as e:
        print(f"{p4f.get_color('RED')}Error counting packets: {e}{p4f.get_color('RESET')}")


def track_stats_and_send_packets():
    start_packet_capture()  # Start tshark before sending packets
    time.sleep(3)  # Allow capture process to initialize
    pkts_stage_6.create_send_pkt(6,1000,17,55)
    time.sleep(5)  # Allow time for packet capture
    count_pkts()  # Stop capture and count packets

    # start_packet_capture()  # Start tshark before sending packets
    # time.sleep(3)  # Allow capture process to initialize
    # pkts_stage_6.create_send_pkt(6,1000,6,5000)
    # time.sleep(5)  # Allow time for packet capture 
    # count_pkts()  # Stop capture and count packets

def main():
    p4f.print_main("Stage 6 Tests")
    parser = argparse.ArgumentParser(description="Step 15_16_17 script for adding entries, tracking stats, and sending packets.")

    # Optional --all flag; if omitted, default to tracking only
    parser.add_argument("--all", action="store_true", help="Run all steps: Add entries, track stats, and send packets.")
    
    args = parser.parse_args()

    if args.all:
        p4f.add_entries(entries_stage_6)

    track_stats_and_send_packets()

if __name__ == '__main__':
    main()
