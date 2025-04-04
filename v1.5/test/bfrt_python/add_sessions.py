import random

p4 = bfrt

# This function can clear all the tables and later on other fixed objects
# once bfrt support is added.
def clear_all(verbose=True, batching=True):
    global p4
    global bfrt

    # The order is important. We do want to clear from the top, i.e.
    # delete objects that use other objects, e.g. table entries use
    # selector groups and selector groups use action profile members

    for table_types in (['MATCH_DIRECT', 'MATCH_INDIRECT_SELECTOR'],
                        ['SELECTOR'],
                        ['ACTION_PROFILE']):
        for table in p4.info(return_info=True, print_info=False):
            if table['type'] in table_types:
                if verbose:
                    print("Clearing table {:<40} ... ".
                          format(table['full_name']), end='', flush=True)
                table['node'].clear(batch=batching)
                if verbose:
                    print('Done')
def unicast_session(session,port):
    bfrt.mirror.cfg.add_with_normal(sid=session, session_enable=True,
                                    direction="INGRESS", ucast_egress_port=port,
                                    ucast_egress_port_valid=True)

def multicast_session(session, ports):
    node_entry = bfrt.pre.node.get(MULTICAST_NODE_ID=session, from_hw=True)
    if node_entry != -1:
        print(f"Deleting existing pre.node entry for session {session}")
        bfrt.pre.node.delete(MULTICAST_NODE_ID=session)
    print(f"Adding pre.node entry for session {session}")
    bfrt.pre.node.add(
        MULTICAST_NODE_ID=session,
        MULTICAST_RID=0,
        DEV_PORT=ports
    )
    mgid_entry = bfrt.pre.mgid.get(MGID=session, from_hw=True)
    if mgid_entry != -1:
        print(f"Deleting existing pre.mgid entry for session {session}")
        bfrt.pre.mgid.delete(MGID=session)
    print(f"Adding pre.mgid entry for session {session}")
    bfrt.pre.mgid.add(
        MGID=session,
        MULTICAST_NODE_ID=[session],
        MULTICAST_NODE_L1_XID_VALID=[True],
        MULTICAST_NODE_L1_XID=[session],
    )
    bfrt.mirror.cfg.add_with_normal(
        sid=session,
        session_enable=True,
        direction="INGRESS",
        mcast_grp_a=session,
        mcast_grp_a_valid=True
    )   


def create_entries():
    """
    Fill in ipv4_host table with random entries, determined by using the
    provided function until failure

    Keyword arguments:
    keyfunc  -- A function that gets "count" as an arg and returns the
                IP address for that entry (default is use count)
    batching -- Batch all the commands (default is True)

    Examples:  create_entries(lambda c: randint(0, 0xFFFFFFFF), True)
               create_entries(lambda c: c + 0xC0a80101, True)
    """
    global p4
    global random
    # global clear_all
    bfrt.mirror.cfg.clear()

    unicast_session(session=100, port=14)
    unicast_session(session=150, port=15)

    multicast_session(session=200, ports=[14, 15])
    multicast_session(session=250, ports=[14, 15, 16])
    multicast_session(session=300, ports=[15, 16])
    multicast_session(session=350, ports=[14, 16])
    

    print("Done")
    print(bfrt.mirror.cfg.dump())
    print(bfrt.pre.node.dump())
    print(bfrt.pre.mgid.dump())
    # print(help(bfrt.mirror.cfg.add_with_normal))


    
    

# clear_all()
create_entries()
print("""
*** Run this script in the interactive mode
***
*** Use create_entries() to test the capacity of a multi-way hash table.
*** Use clear_all() to clear the tables
*** Use help(<function>) to learn more
""")