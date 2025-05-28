from results_fns.compare_cnts import *
from results_fns.compare_pkts import *

#=========================================================================================================================
"""Utility functions for validating results in a test case.
This module provides a function to validate captured packets and counters
against expected values in a test case scenario.
"""
#=========================================================================================================================

def validate_results(counter_df, packet_storage, dev_tgt, bfrt_info, case_stg, idx, failed_cases, printing=False):
    """
    Validate the results of a test case by checking captured packets and counters.
    :param counter_df: DataFrame containing counter information.
    :param packet_storage: Dictionary containing captured packets for each interface.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :param case_stg: Dictionary containing stage information for the test case.
    :param idx: Index of the test case.
    :param failed_cases: List to store indices of failed test cases.
    :param printing: Boolean flag to control printing of debug information.
    :return: Updated list of failed cases.
    """

    pkt_passed = validate_captured_packets(packet_storage, case_stg, idx, printing)
    cnt_passed = validate_counters(counter_df, dev_tgt, bfrt_info, case_stg, printing)
    if printing:
        print_console("Blue", f"Validation Results for Case {idx + 1}", 100, space=False)
        if pkt_passed:
            print_console("PALE_GREEN", f"[PASS] packet validation", 100, '-', space=False)
        else:
            print_console("PALE_RED", f"[FAIL] packet validation", 100, '-',space=False)
        if cnt_passed:
            print_console("PALE_GREEN", f"[PASS] counter validation", 100, '-',space=False)
        else:
            print_console("PALE_RED", f"[FAIL] counter validation", 100, '-',space=False)

    if pkt_passed and cnt_passed:
        if printing:
            print_console("green", f"[PASS] Case {idx + 1}", 100, space=False)
    else:
        if printing:
            print_console("red", f"[FAIL] Case {idx + 1}", 100, space=False)
        failed_cases.append(idx + 1)

    return failed_cases



    
