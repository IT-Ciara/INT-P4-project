from functions.packet_utils import *
from functions.print_utils import *

#========================================================================================================================
"""Utility functions for validating captured packets against expected values.
This module provides a function to validate captured packets based on the expected output
and handles different mirroring and export scenarios.
"""
#========================================================================================================================


def validate_captured_packets(packet_storage, case_stg, idx, printing=False):
    """
    Validate captured packets against expected values in a test case scenario.
    :param packet_storage: Dictionary containing captured packets for each interface.
    :param case_stg: Dictionary containing stage information for the test case.
    :param idx: Index of the test case.
    :param printing: Boolean flag to control printing of debug information.
    :return: Boolean indicating whether the packet validation passed.
    """
    passed = False
    expected_pkt = case_stg['pkt_values']['Output pkt'].lower()
    flow_mirror_enabled = case_stg['stage_tables']['Stg8 | Flow mirror?'].get('value') == "YES"
    port_mirror_enabled = case_stg['stage_tables']['Stg9 | Port mirror?'].get('value') == "YES"
    export_int_enabled = case_stg['stage_tables']['Stg10 | IG:Has Polka. Export INT?'].get('value') == "YES"

    for iface, packets in packet_storage.items():
        if not packets:
            if case_stg['Output'].lower() == "drop":
                if printing:
                    print_console("green", f"No packet captured on {iface}. Expected drop.", 100, '-', space=False)
                passed = True
            continue
        parsed_pkt = parse_pkts(packets[0], print_layers=printing).lower()
        if parsed_pkt == expected_pkt:
            if printing:
                print_console("green", f"Packet captured on {iface} matches expected packet", 100, '-', space=False)
            passed = True
        elif flow_mirror_enabled and iface == "veth28":
            if printing:
                print_console("green", f"Captured pkt on {iface}. Flow mirror is enabled", 100, '-', space=False)
            passed = True
        elif port_mirror_enabled and iface == "veth30":
            if printing:
                print_console("green", f"Captured pkt on {iface}. Port mirror is enabled", 100, '-', space=False)
            passed = True
        elif export_int_enabled and iface == "veth32":
            if printing:
                print_console("green", f"Captured pkt on {iface}. Export INT is enabled", 100, '-', space=False)
            passed = True
            
        else:
            if printing:
                print_console("red", f"Packet captured on {iface} does not match expected packet", 100, '-', space=False)
            passed = False
    
    return passed


 