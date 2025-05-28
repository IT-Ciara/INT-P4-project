import json
import numpy as np

#========================================================================================================================
"""Utility functions for managing and updating case staging data in a testing framework.
This module provides functions to update case staging dictionaries with case data, stage tables, packet values,
and to convert objects to a serializable format. """
#========================================================================================================================



GREY = "\033[90m"
RESET = "\033[0m" 

def update_case_staging(case, case_stg):
    """
    Update the case staging dictionary with the provided case data.
    """
    case_stg['Case'] = case['Case']
    case_stg['User Case'] = case['User Case']
    case_stg['Input'] = case['Input']
    case_stg['Output'] = case['Output']
    return case_stg

def add_stages_tables(case,stages, case_stg):
    """
    Add stage tables and their values to the case staging dictionary.
    """
    for stage, data in stages.items():
        stages[stage]['value'] = case[stage]
    case_stg['stage_tables'] = stages
    return case_stg

def add_pkt_values(case, case_stg):
    """
    Extract packet-related keys from the case and add them to the case staging dictionary.
    """
    pkt_keys = {}
    for key, value in case.items():
        if key.startswith("ig_intr_md.") or key.startswith("eg_intr_md.") or key.startswith("ig_tm_md.") or key.startswith("hdr") or key.endswith("pkt") or ("pkt" in key.lower() and "Stg" not in key):
            pkt_keys[key] = value
    case_stg['pkt_values'] = pkt_keys
    return case_stg

def convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
    
