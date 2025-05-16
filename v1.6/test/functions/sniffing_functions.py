import threading
from functions.printing_functions import * 
from functions.packet_functions import *

#=======================================================================================================================
#========================================== S N I F F I N G  F U N C T I O N S =========================================
#=======================================================================================================================
# --- Packet Printer (for Sniffer) ---
def pkt_hex(pkt, create_pkt=False, packet_list=None):
    if not create_pkt:
        thread_name = threading.current_thread().name
        print_console("Reset", f"--- Packet Captured on {thread_name.replace('Sniffer-', '')} ---", 70)

    if packet_list is not None:
        packet_list.append(pkt)  # Save the raw packet

    parse_pkts(pkt)  # Your existing parsing logic

    
# --- Background Sniffer (per interface) ---
def sniff_pkts(iface, timeout=5, results_dict=None, lock=None, packet_list=None):
    # Use lambda to pass extra args to prn
    packets = sniff(
        iface=iface,
        timeout=timeout,
        prn=lambda pkt: pkt_hex(pkt, packet_list=packet_list)
    )

    captured = bool(packets)
    if results_dict is not None and lock is not None:
        with lock:
            results_dict[iface] = captured


def start_multi_sniffer_in_background(interfaces, timeout=5):
    threads = []
    results_dict = {}
    packet_storage = {}  # Store packets per interface
    lock = threading.Lock()

    for iface in interfaces:
        packet_storage[iface] = []  # Initialize a list for each iface
        sniffer_thread = threading.Thread(
            target=sniff_pkts,
            args=(iface, timeout, results_dict, lock, packet_storage[iface]),
            daemon=True,
            name=f"Sniffer-{iface}"
        )
        sniffer_thread.start()
        threads.append(sniffer_thread)

    return threads, results_dict, packet_storage

