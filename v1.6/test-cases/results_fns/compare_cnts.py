from results_fns.counters import *
from functions.print_utils import *
from results_fns.counters import *
from functions.print_utils import *

#=========================================================================================================================
"""Utility functions for validating counters in a test case.
This module provides functions to validate direct and indirect counters
against expected values in a test case scenario.
"""
#=========================================================================================================================

def validate_counters(counter_df, dev_tgt, bfrt_info, case_stg, printing=False):
    """
    Validate counters against expected values in a test case scenario.
    :param counter_df: DataFrame containing counter information.
    :param dev_tgt: Device target for the BFRT operations.
    :param bfrt_info: BFRT information object.
    :param case_stg: Dictionary containing stage information for the test case.
    :param printing: Boolean flag to control printing of debug information.
    :return: Boolean indicating whether the counter validation passed.
    """
    counter_dict = counter_df.to_dict()
    passed = False
    for stage, details in case_stg['stage_tables'].items():
        counter_type = ""
        value = None
        stage_name = stage.upper()
        #==================  C O U N T E R S  ==========================
        #---------------------------------------------------------------
        #print values of the stage
        if details['value'] == "YES" and 'polka id' not in stage.lower():
            #Check if the stage has a table
            if details['Tables']!= []:
                if printing:
                    print(f"\n{get_color('PALE_BLUE')}\nStage: {stage.upper()},  Value: {details['value']}{get_color('RESET')}")
                value = get_direct_counters(details['Tables'], dev_tgt, bfrt_info)
                counter_type = "DIRECT"
        elif 'polka id' in stage.lower() and details['value'] != "":
            if details['value']=="YES":
                if printing:
                    print(f"\n{get_color('PALE_BLUE')}\nStage: {stage.upper()},  Value: {details['value']}{get_color('RESET')}")
                value = get_indirect_counter_values(details['Indirect Counters'], dev_tgt, bfrt_info, target_index=1)
                counter_type = "INDIRECT(1)"
            elif details['value'] == "NO":
                if printing:
                    print(f"\n{get_color('PALE_BLUE')}\nStage: {stage.upper()},  Value: {details['value']}{get_color('RESET')}")
                value = get_indirect_counter_values(details['Indirect Counters'], dev_tgt, bfrt_info, target_index=0)
                counter_type = "INDIRECT(0)"
        elif details['value'] == "NO" or ('polka' in stage.lower() and (details['value'] == "YES" or details['value'] == "NO")):
            if details['Indirect Counters'] != {}:
                if printing:
                    print(f"\n{get_color('PALE_PINK')}\nStage: {stage.upper()},  Value: {details['value']}{get_color('RESET')}")
                value = get_indirect_counter_values(details['Indirect Counters'], dev_tgt, bfrt_info)
                counter_type = "INDIRECT"
        else:
            #print in green
            if printing:
                print(f"{get_color('GREY')}\nStage: {stage},  Value: N/A{get_color('RESET')}")

        #Check if the stage is in the counter dictionary
        if stage not in counter_dict:
            continue

        observed_type = counter_dict.get(stage, '').strip().upper()
        if observed_type.lower() == counter_type.lower():
            if case_stg['Output'] == "Drop" and value == 1 and 'output' in case_stg:
                passed = False
                if printing:
                    print_console("red", f"[FAIL] Stage: {stage_name}, Expected drop, counter value zero → Invalid", 100, '-')
            else:
                passed = True
                if printing:
                    print_console("green", f"[PASS] Counter Value: {value}, Counter Type: {counter_type}, Observed Type: {observed_type}", 100, '-')
        else:
            print(f"{get_color('RED')}\n[FAIL] Stage: {stage_name}, Expected Counter Type: {counter_type}, Observed Type: {observed_type}{get_color('RESET')}")
            passed = False

    return passed
