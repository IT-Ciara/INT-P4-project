import threading
from functions.print_utils import * 
from functions.packet_utils import *

#========================================================================================================================
"""Utility functions for packet sniffing and processing.
This module provides functions to capture packets on specified interfaces,
print packet details, and store captured packets in a thread-safe manner.
"""
#========================================================================================================================

#=======================================================================================================================
#========================================== S N I F F I N G  F U N C T I O N S =========================================
#=======================================================================================================================
# --- Packet Printer (for Sniffer) ---
def pkt_hex(pkt, create_pkt=False, packet_list=None,print_layers=False):
    """
    Print the hex representation of a packet and optionally save it to a list.
    :param pkt: Scapy packet object to be printed.
    :param create_pkt: Boolean flag to indicate if the packet should be created.
    :param packet_list: List to store the raw packet if provided.
    :param print_layers: Boolean flag to control printing of layer fields.
    :return: None
    """

    if not create_pkt:
        thread_name = threading.current_thread().name
        if print_layers:
            print_console("Reset", f"--- Packet Captured on {thread_name.replace('Sniffer-', '')} ---", 70,break_line=True)
    if packet_list is not None:
        packet_list.append(pkt)  # Save the raw packet
    parse_pkts(pkt,print_layers=print_layers)

    
# --- Background Sniffer (per interface) ---
def sniff_pkts(iface, timeout=5, results_dict=None, lock=None, packet_list=None,print_layers=False):
    """
    Sniff packets on a specified interface and print their details.
    :param iface: Network interface to sniff packets on.
    :param timeout: Time in seconds to wait for packets.
    :param results_dict: Dictionary to store results of the sniffer.
    :param lock: Lock for thread-safe access to results_dict.
    :param packet_list: List to store captured packets.
    :param print_layers: Boolean flag to control printing of layer fields.
    :return: None
    """

    # Use lambda to pass extra args to prn
    packets = sniff(
        iface=iface,
        timeout=timeout,
        prn=lambda pkt: pkt_hex(pkt, packet_list=packet_list,print_layers=print_layers),
    )

    captured = bool(packets)
    if results_dict is not None and lock is not None:
        with lock:
            results_dict[iface] = captured


def start_multi_sniffer_in_background(interfaces, timeout=5, print_layers=False):
    """
    Start multiple sniffer threads for each interface and return their results.
    :param interfaces: List of network interfaces to sniff on.
    :param timeout: Time in seconds to wait for packets on each interface.
    :param print_layers: Boolean flag to control printing of layer fields.
    :return: Tuple containing list of threads, results dictionary, and packet storage.
    """
    
    threads = []
    results_dict = {}
    packet_storage = {}  # Store packets per interface
    lock = threading.Lock()

    for iface in interfaces:
        packet_storage[iface] = []  # Initialize a list for each iface
        sniffer_thread = threading.Thread(
            target=sniff_pkts,
            args=(iface, timeout, results_dict, lock, packet_storage[iface],print_layers),
            daemon=True,
            name=f"Sniffer-{iface}"
        )
        sniffer_thread.start()
        threads.append(sniffer_thread)

    return threads, results_dict, packet_storage

