import json
import pandas as pd
import bfrt_grpc.client as gc
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
import sys
from scapy.all import Ether, Dot1Q, Dot1AD, IP, UDP, Raw, Packet, BitField, sendp, wrpcap, TCP, bind_layers, sniff
from scapy.contrib.lldp import LLDPDU, LLDPDUChassisID, LLDPDUPortID, LLDPDUTimeToLive, LLDPDUEndOfLLDPDU
import time
import threading
import numpy as np
#========================================== I N T E R F A C E S ========================================================
#=======================================================================================================================
with open('tf1_model.json') as f:
    tf1_model = json.load(f)
# tf1_model is already the interfaces dictionary
interfaces = list(tf1_model.values())
print(interfaces)

#============================== P A C K E T   H E A D E R S ============================================================
#=======================================================================================================================
from functions.packet_headers import *

#========================================= P R I N T I N G  F U N C T I O N S ==========================================
#=======================================================================================================================
from functions.printing_functions import *

#============================== P A C K E T   B A S E L I N E  =========================================================
#=======================================================================================================================
polka = PolkaHdr(version=1, ttl=64, proto=0x0601, routeid=0x002)

#======================================== C A S E  F I L E  F U N C T I O N S ==========================================
#=======================================================================================================================
from functions.case_file_functions import *

#========================================== S N I F F I N G  F U N C T I O N S =========================================
#=======================================================================================================================
from functions.sniffing_functions import *  

#========================================== G R P C  F U N C T I O N S =================================================
#=======================================================================================================================
from functions.grpc_functions import *

#========================================== P A C K E T  F U N C T I O N S =============================================
#=======================================================================================================================
from functions.packet_functions import *
from functions.packet_functions import polka

#========================================== C R E A T E  E N T R I E S =================================================
#=======================================================================================================================
from functions.create_entries import *

#==========================================================================================================================
#================================================= R E G I S T R Y  F U N C T I O N S ==================================
#==========================================================================================================================
from functions.registry_functions import *

#=======================================================================================================================
#================================================ I N D I R E C T  C O U N T E R S =====================================
#=======================================================================================================================
from functions.counters import *

def get_table_details(tables, bfrt_info):
    tables_dict = {}
    for table_name in tables:
        table = bfrt_info.table_get(table_name)
        keys = table.info.key_field_name_list_get()
        actions = table.info.action_name_list_get()
        tables_dict[table_name] = {
            "grpc_name": table_name,
            "keys": [],
            "actions": []
        }
        for key in keys:
            match_type = table.info.key_field_match_type_get(key)
            tables_dict[table_name]["keys"].append({
                "name": key,
                "match": match_type
            })
        for action_name in actions:
            if action_name == "NoAction":
                continue
            action_entry = {
                "name": action_name,
                "parameters": []
            }
            try:
                param_names = table.info.data_field_name_list_get(action_name)
                for param in param_names:
                    if "$COUNTER" in param:
                        continue
                    action_entry["parameters"].append(param)
                tables_dict[table_name]["actions"].append(action_entry)
            except Exception as e:
                print(f"  Could not retrieve action parameters: {e}")
    return tables_dict


def get_all_tables(bfrt_info):
    tables = []
    all_tables = bfrt_info.table_name_list_get()
    for table_name in all_tables:
        if "pipe.Ingress." in table_name or "pipe.Egress." in table_name:
            if any(x in table_name for x in ['miss', 'counter', 'routeId', 'hash']):
                continue
            tables.append(table_name)
    return get_table_details(tables, bfrt_info)


def get_indirect_counters_details(counters, bfrt_info):
    indirect_counters_info = {}
    for counter_name in counters:
        table = bfrt_info.table_get(counter_name)
        indirect_counters_info[counter_name] = {
            "keys": [],
        }
        try:
            for key in table.info.key_field_name_list_get():
                match_type = table.info.key_field_match_type_get(key)
                indirect_counters_info[counter_name]["keys"].append({
                    "name": key,
                    "match": match_type
                })
        except Exception as e:
            print(f"  Could not retrieve key fields: {e}")
        data_fields_list = table.info.data_dict_allname
        indirect_counters_info[counter_name]["data_fields"] = data_fields_list
    return indirect_counters_info


def get_all_counters(bfrt_info):
    indirect_counter = []
    all_tables = bfrt_info.table_name_list_get()
    for table_name in all_tables:
        if "pipe.Ingress." in table_name or "pipe.Egress." in table_name:
            if 'counter' in table_name:
                indirect_counter.append(table_name)
    return get_indirect_counters_details(indirect_counter, bfrt_info)

def get_main_stages(bfrt_info,file_path='cases.xlsx'):
    stages = {}
    
    # Load Excel sheets
    tables_df = pd.read_excel(file_path, sheet_name='Stg-tbls').fillna('')
    counters_df = pd.read_excel(file_path, sheet_name='indirect_counter').fillna('')
    tables_df.columns = tables_df.columns.str.replace('\n', ' | ', regex=False)
    counters_df.columns = counters_df.columns.str.replace('\n', ' | ', regex=False)
    for col in tables_df.columns:
        stage_name = col.strip()
        table_values = tables_df[col].dropna().astype(str).str.strip().tolist()
        counter_values = counters_df[col].dropna().astype(str).str.strip().tolist() if col in counters_df.columns else []
        table_values = [val for val in table_values if val]
        counter_values = [val for val in counter_values if val]
        stages[stage_name] = {
            'value': "",
            'Tables': table_values,
            'Indirect Counters': counter_values
        }
    # Fetch metadata from BFRT
    tables = get_all_tables(bfrt_info)
    indirect_counters = get_all_counters(bfrt_info)
    # Combine everything
    enriched_stages = {}
    for stage, data in stages.items():
        stage_info = {
            'value' : "",
            'Tables': {},
            'Indirect Counters': {}
        }
        # Match and enrich table info
        for tbl_name in data['Tables']:
            fq_table = next((t for t in tables if t.endswith(tbl_name)), None)
            if fq_table and fq_table in tables:
                stage_info['Tables'][fq_table] = tables[fq_table]
            else:
                stage_info['Tables'][tbl_name] = {"error": "Table metadata not found"}
        # Match and enrich counter info
        for ctr_name in data['Indirect Counters']:
            fq_counter = next((c for c in indirect_counters if c.endswith(ctr_name)), None)
            if fq_counter and fq_counter in indirect_counters:
                stage_info['Indirect Counters'][fq_counter] = indirect_counters[fq_counter]
            else:
                stage_info['Indirect Counters'][ctr_name] = {"error": "Counter metadata not found"}
        enriched_stages[stage] = stage_info
    # Save to JSON
    with open("stage_mapping.json", "w") as f:
        json.dump(enriched_stages, f, indent=4)
    return enriched_stages

def load_case_data(file_path):
    df = pd.read_excel(file_path, sheet_name='Cases').fillna('')
    df.columns = df.columns.str.replace('\n', ' | ', regex=False)
    return df

def clear_all(stages, dev_tgt, bfrt_info):
    for stage, data in stages.items():
        for tbl_name in data['Tables']:
            if 'eg_int_table' in tbl_name:
                continue
            table = bfrt_info.table_get(tbl_name)
            table.entry_del(dev_tgt, [])
        for ctr_name in data['Indirect Counters']:
            table = bfrt_info.table_get(ctr_name)
            table.entry_del(dev_tgt, [])

def add_stages_tables(case,stages, case_stg):
    for stage, data in stages.items():
        stages[stage]['value'] = case[stage]
    case_stg['stage_tables'] = stages
    return case_stg

def add_pkt_values(case, case_stg):
    pkt_keys = {}
    for key, value in case.items():
        # print(f"{key}: {value}")
        if key.startswith("ig_intr_md.") or key.startswith("eg_intr_md.") or key.startswith("ig_tm_md.") or key.startswith("hdr") or key.endswith("pkt") or ("pkt" in key.lower() and "Stg" not in key):
            pkt_keys[key] = value
    case_stg['pkt_values'] = pkt_keys
    return case_stg

def add_other_case_values(case, case_stg):
    case_stg['Case'] = case['Case']
    case_stg['User Case'] = case['User Case']
    case_stg['Input'] = case['Input']
    case_stg['Output'] = case['Output']
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





def main():
    interface, dev_tgt, bfrt_info = gc_connect()
    stages = get_main_stages(bfrt_info, file_path='cases.xlsx')
    df_cases = load_case_data(file_path='cases.xlsx')
    #==============  A D D  P O L K A  R E G I S T E R S ============
    #----------------------------------------------------------------
    add_polka_registers(dev_tgt, bfrt_info)
    # Save the stages to a file
    case=130
    failed_cases = []
    for idx in range(case-1,case):
    # for idx in range(len(df_cases)):
        case_stg = {}
        interfaces = list(tf1_model.values())
        clear_all(stages, dev_tgt, bfrt_info)
        case_df = df_cases.iloc[idx]
        case_stg = add_other_case_values(case_df, case_stg.copy())
        case_stg = add_stages_tables(case_df, stages, case_stg.copy())
        case_stg = add_pkt_values(case_df, case_stg.copy())

        with open(f"case.json", "w") as f:
            json.dump(convert_to_serializable(case_stg), f, indent=4)
        original_pkt = create_pkts(case_stg['pkt_values'])
        create_entries_main(case_stg,dev_tgt, bfrt_info, original_pkt)
        
        #===================Sniff packets==========================
        #----------------------------------------------------------
        print("Starting multi-interface sniffer")
        print_console("grey","Starting multi-interface sniffer",100,'-')
        initial_ingress_port = case_stg['pkt_values']['ig_intr_md.ingress_port']
        ingress_veth = f"veth{initial_ingress_port*2}"
        if case_stg['Output'].lower() != "ingress port":
            #Exclude the ingress port from interfaces
            interfaces.remove(ingress_veth)
        sniff_threads,capture_results,packet_storage  = start_multi_sniffer_in_background(interfaces, timeout=7)
        # Give sniffers a moment to start up
        time.sleep(1.5)
        
        #===================Send packets===========================
        #----------------------------------------------------------
        print_console("reset",f"Sending packets {initial_ingress_port}",70)
        #replace the ether src 
        parse_pkts(original_pkt)
        sendp(original_pkt, iface=ingress_veth, verbose=False)
        time.sleep(1)

        #=============== Wait for Sniffers to Finish =================
        for thread in sniff_threads:
            thread.join()  # Ensures the sniffers finish before printing stats

        # Check if NO packets were captured on ANY interface
        if not any(capture_results.values()):  
            print_console("reset", "- - - PACKET CAPTURE RESULTS - - -", 100)
            print_console("grey", "No packets captured on any interface", 100, '-', space=False) 
            if case_stg['Output'].lower() == "drop":
                print_console("green",f"Packet dropped as expected", 100, '-', space=False)
            else:
                print_console("red",f"Packet dropped but expected to be captured", 100, '-', space=False)
                failed_cases.append(idx+1)

        for iface, packet in packet_storage.items():
            if packet!= []:
                result = parse_pkts(packet[0],print_layers=False)
                print(f"Interface: {iface}, Packet: {result}")
                #Compare the captured packet with the expected packet
                if result.lower() == case_stg['pkt_values']['Output pkt'].lower():
                    print_console("green",f"Packet captured on {iface} matches expected packet", 100, '-', space=False)
                elif case_stg['stage_tables']['Stg8 | Flow mirror?'].get('value') == "YES" and iface == "veth28":
                    print_console("green",f"Captured pkt on {iface}. Flow mirror is enabled", 100, '-', space=False)
                elif case_stg['stage_tables']['Stg9 | Port mirror?'].get('value') == "YES" and iface == "veth30":
                    print_console("green",f"Captured pkt on {iface}. Port mirror is enabled", 100, '-', space=False)
                elif case_stg['stage_tables']['Stg10 | IG:Has Polka. Export INT?'].get('value') == "YES" and iface == "veth32":
                    print_console("green",f"Captured pkt on {iface}. Export INT is enabled", 100, '-', space=False)
                else:
                    print(case_stg['stage_tables']['Stg10 | IG:Has Polka. Export INT?'].get('value'))
                    print_console("red",f"Packet captured on {iface} does not match expected packet", 100, '-', space=False)
                    failed_cases.append(idx+1)

        #==================  C O U N T E R S  ==========================
        #---------------------------------------------------------------
        for stage, details in case_stg['stage_tables'].items():
            #print values of the stage
            if details['value'] == "YES" and 'polka' not in stage.lower():
                #Check if the stage has a table
                if details['Tables']!= []:
                    print(f"\n{get_color('PALE_BLUE')}\nStage: {stage.upper()},  Value: {details['value']}{get_color('RESET')}")
                    get_direct_counters(details['Tables'], dev_tgt, bfrt_info)
            elif 'polka' in stage.lower() and details['value'] != "":
                if details['value']=="YES":
                    print(f"\n{get_color('PALE_BLUE')}\nStage: {stage.upper()},  Value: {details['value']}{get_color('RESET')}")
                    get_indirect_counter_values(details['Indirect Counters'], dev_tgt, bfrt_info, target_index=1)
                elif details['value'] == "NO":
                    print(f"\n{get_color('PALE_BLUE')}\nStage: {stage.upper()},  Value: {details['value']}{get_color('RESET')}")
                    get_indirect_counter_values(details['Indirect Counters'], dev_tgt, bfrt_info, target_index=0)
            elif details['value'] == "NO" or ('polka' in stage.lower() and (details['value'] == "YES" or details['value'] == "NO")):
                if details['Indirect Counters'] != {}:
                    print(f"\n{get_color('PALE_PINK')}\nStage: {stage.upper()},  Value: {details['value']}{get_color('RESET')}")
                    get_indirect_counter_values(details['Indirect Counters'], dev_tgt, bfrt_info)
            else:
                #print in green
                print(f"{get_color('GREY')}\nStage: {stage},  Value: N/A{get_color('RESET')}")

                    
    for failed_case in failed_cases:
        print_console("red",f"Case {failed_case} failed", 100, '-', space=False)

    interface.tear_down_stream()


if __name__ == "__main__":
    main()
