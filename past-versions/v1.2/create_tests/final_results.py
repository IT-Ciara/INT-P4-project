from scapy.all import rdpcap, hexdump, Ether, IP, UDP, Raw, Dot1Q, IPv6, TCP, Packet, BitField
import hashlib

import compare_pkts as cpkts

def compare_number_of_packets(packets, num_links):
    """Compare the number of packets captured."""
    if len(packets) == 2**num_links:
        # print("pass")
        return f"\tpass\t\t({len(packets)} pkts)"
    else:
        # print("fail")
        return f"\tfailed\t\t({len(packets)} pkts)"
    

def compare_different_layers(different_layers, use_case):
    different_layers_map = {
        "No VLAN translation": [],
        "With VLAN range (No translation)": [],
        "No VLAN U1 with VLAN U2": ['ethernet'],
        "VLAN translation": ['vlan_0x8100_0'],
        "No VLAN": [],
    }

    #find the use case in the map
    if use_case in different_layers_map:
        #compare the different layers
        if different_layers == different_layers_map[use_case]:
            return f"\tpass\t\t({different_layers})"
        else:
            return f"\tfailed\t\t({different_layers})"
        






def get_final_results(case_number,use_case,num_links):
    """Get the final results of the test case."""
    # Load the packets
    packets = rdpcap(f"./wireshark/case{case_number}.pcap")
    
    print(f"Test case {case_number}: {use_case}")
    print(f"Number of packets test: {compare_number_of_packets(packets, num_links)}")


    total_pkts = len(packets)
    #sort the packets based on the timestamp
    packets.sort(key=lambda x: x.time)
    #get the first and last packet
    first_packet = packets[0]
    last_packet = packets[-1]
    packet_data_1 = cpkts.parse_packet(first_packet)
    packet_data_2 = cpkts.parse_packet(last_packet)
    counter = 1
    counter,same_layers,different_layers= cpkts.compare_pkts(packet_data_1, packet_data_2, counter,False)
    
    print(f"Expected different layers: {compare_different_layers(different_layers, use_case)}")



