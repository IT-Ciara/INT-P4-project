import sys

def clear_table(table):
    print(f"CLEAR TABLE: {table}")
    table.clear()

def create_entries(table):
    print(f"CREATE ENTRIES IN {table}")
    table.add_with_send_to_cpu(src_addr="00:00:00:00:00:01",stats_idx=1)
    # table.dump()

def main_function():
    # Use the correct table name directly
    table = bfrt.p4_main_v1_4.pipe.Ingress.ig_is_sdn_trace.is_sdn_tbl
    clear_table(table)
    create_entries(table)

if __name__ == "__main__":
    main_function()
