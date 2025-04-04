import sys

def clear_table(table):
    print(f"CLEAR TABLE: {table}")
    table.clear()


def create_entries(table):
    print(f"CREATE ENTRIES IN {table}")
    for i in range(0,15):
        if i >= 0 and i < 8 :
            table.add_with_user_port(ingress_port=i,user_flag=1)
        else:
            table.add_with_user_port(ingress_port=i,user_flag=0)
    # table.dump()

def main_function():
    # Use the correct table name directly
    table = bfrt.p4_main_v1_4.pipe.Ingress.ig_ingress_port.ingress_port_tbl
    clear_table(table)
    create_entries(table)

if __name__ == "__main__":
    main_function()
