import pandas as pd

#==========================================================
#========== C A S E  F I L E F U N C T I O N S ============
#==========================================================
def load_stage_table_mapping(file_path):
    df = pd.read_excel(file_path, sheet_name='Stg-tbls').fillna('')
    df.columns = df.columns.str.replace('\n', ' | ', regex=False)
    # Transpose: stage names become index
    df_transposed = df.transpose()
    df_transposed.columns = [f"tbl_{i}" for i in range(len(df_transposed.columns))]
    # Build dictionary: stage -> list of non-empty table names
    return {
        stage: [tbl for tbl in row if tbl]
        for stage, row in df_transposed.iterrows()
    }
def load_case_data(file_path):
    df = pd.read_excel(file_path, sheet_name='Cases').fillna('')
    df.columns = df.columns.str.replace('\n', ' | ', regex=False)
    return df

def build_case_with_stage_tables(case_series, stage_table_map, tables):
    case_dict = case_series.to_dict()
    stage_tables = {}

    # Track which tables belong to which stages
    for stage in list(case_dict):
        if not stage.startswith("Stg"):
            continue

        stage_value = case_dict[stage]
        stage_table_entries = []

        for tbl_name in stage_table_map.get(stage, []):
            grpc_name = None
            for full_name in tables:
                if tbl_name in full_name:
                    grpc_name = full_name
                    break

            if not grpc_name:
                continue

            table_data = tables[grpc_name]

            # Add stage_name to the table entry (in-place modification)
            if "stage_names" not in table_data:
                table_data["stage_names"] = []
            if stage not in table_data["stage_names"]:
                table_data["stage_names"].append(stage)

            stage_table_entries.append({
                "name": tbl_name,
                "grpc_name": grpc_name,
                "keys": table_data.get("keys", []),
                "actions": table_data.get("actions", [])
            })

        stage_tables[stage] = {
            "value": stage_value,
            "tables": stage_table_entries
        }

        del case_dict[stage]

    case_dict["stage_tables"] = stage_tables

    pkt_keys = [key for key in case_dict if (
        key.startswith("ig_intr_md.") or
        key.startswith("eg_intr_md.") or
        key.startswith("ig_tm_md.") or
        key.startswith("hdr") or
        key.endswith("pkt") or
        "pkt" in key.lower()
    )]
    pkt_values = {key: case_dict[key] for key in pkt_keys}
    for key in pkt_keys:
        del case_dict[key]

    case_dict["pkt_values"] = pkt_values
    return case_dict


# def build_case_with_stage_tables(case_series, stage_table_map, tables):
#     case_dict = case_series.to_dict()
#     stage_tables = {}
#     # Process stages and enrich with gRPC table metadata
#     for stage in list(case_dict):
#         if not stage.startswith("Stg"):
#             continue
#         stage_value = case_dict[stage]
#         stage_table_entries = []
#         for tbl_name in stage_table_map.get(stage, []):
#             grpc_name = None
#             for full_name in tables:
#                 if tbl_name in full_name:
#                     grpc_name = full_name
#                     break
#             if not grpc_name:
#                 continue  # Skip if not found
#             table_data = tables[grpc_name]
#             stage_table_entries.append({
#                 "name": tbl_name,
#                 "grpc_name": grpc_name,
#                 "keys": table_data.get("keys", []),
#                 "actions": table_data.get("actions", [])
#             })
#         stage_tables[stage] = {
#             "value": stage_value,
#             "tables": stage_table_entries
#         }
#         # Remove stage field from the top-level case_dict
#         del case_dict[stage]
#     case_dict["stage_tables"] = stage_tables
#     # Group packet-related fields into 'pkt_values'
#     pkt_keys = [key for key in case_dict if (
#         key.startswith("ig_intr_md.") or
#         key.startswith("eg_intr_md.") or
#         key.startswith("ig_tm_md.") or
#         key.startswith("hdr") or
#         key.endswith("pkt") or
#         "pkt" in key.lower()
#     )]
#     pkt_values = {key: case_dict[key] for key in pkt_keys}
#     for key in pkt_keys:
#         del case_dict[key]
#     case_dict["pkt_values"] = pkt_values
#     return case_dict
