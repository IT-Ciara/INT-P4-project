import json 
import bfrt_grpc.client as gc
from functions.packet_utils import polka


#==========================================================================================================================
#================================================= R E G I S T R Y  F U N C T I O N S ==================================
#==========================================================================================================================
def split_128bit_to_32bit_chunks(val):
    return [
        (val >> 96) & 0xFFFFFFFF,
        (val >> 64) & 0xFFFFFFFF,
        (val >> 32) & 0xFFFFFFFF,
        val & 0xFFFFFFFF
    ]

def add_polka_registers(dev_tgt, bfrt_info, selected_node=1,TARGET="tf1_model"):
    with open(f'./polka_fns/route_info_{TARGET}.json', 'r') as f:
        route_data = json.load(f)        
    #==================================================================
    # ======= P O L K A - R E G I S T E R S ========
    #==================================================================
    # ======== Route ID ========
    # #-------Set the route ID-------
    routeid_int = route_data['route']['values']['int_route_id']
    chunks = split_128bit_to_32bit_chunks(routeid_int)
    reg_names = [
        "Egress.routeId_high_upper",
        "Egress.routeId_high_lower",
        "Egress.routeId_low_upper",
        "Egress.routeId_low_lower"
    ]
    for i, reg_name in enumerate(reg_names):
        routeId_tbl = bfrt_info.table_get(reg_name)
        key = routeId_tbl.make_key([gc.KeyTuple('$REGISTER_INDEX', 0)])
        data = routeId_tbl.make_data([
            gc.DataTuple(f'{reg_name}.f1', chunks[i])
        ])
        routeId_tbl.entry_mod(dev_tgt, [key], [data])
    #Modify the route ID
    polka.routeid = routeid_int
    
    # =========== Node ID ===========
    node_key = f"node_{selected_node}"
    node_id_hex = route_data['nodes'][node_key]['id']['hex_node_id']
    node_id_int = int(node_id_hex, 16) & 0xffff  # Convert then mask    
    algorithm_tbl = bfrt_info.table_get("Ingress.hash.algorithm")
    data_field_list = [
        gc.DataTuple("polynomial",node_id_int), #node_id
    ]
    data_list = algorithm_tbl.make_data(data_field_list,"user_defined")
    algorithm_tbl.default_entry_set(dev_tgt, data_list)  