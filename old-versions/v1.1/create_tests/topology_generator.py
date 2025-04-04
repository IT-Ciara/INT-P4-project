import matplotlib.pyplot as plt
import networkx as nx
import random
import os 

# Constants
MAX_SWITCH_PORTS = 17
MAX_USER_PORTS = 8
VLAN_C_RANGES = list(range(10, 2000, 10))
VLAN_S_RANGES = list(range(2010, 4000, 10))
USE_CASES = [
    "No VLAN translation",
    "With VLAN range (No translation)",
    "No VLAN U1 with VLAN U2",
    "VLAN translation",
    "No VLAN",
]


# Define topologies in a dictionary
topologies = {
    "2_u_2_i": {
        "user_switches": ["sw1", "sw4"],
        "intermediate_switches": ["sw2", "sw3"],
        "edges": [("sw1", "sw2"), ("sw1", "sw3"), ("sw2", "sw3"), ("sw2", "sw4"), ("sw3", "sw4")],
        "positions": {
            # "sw1": (-1, 0), "sw2": (0, 1), "sw3": (0, -1), "sw4": (1, 0)
            "sw1": (-1, 0), "sw2": (0, 0.2), "sw3": (0, -0.2), "sw4": (1, 0)
        },
        "title": "Network Topology with 2 User and 2 Intermediate Switches"
    },
    "2_u_3_i": {
        "user_switches": ["sw1", "sw5"],
        "intermediate_switches": ["sw2", "sw3", "sw4"],
        "edges": [
            ("sw1", "sw2"), ("sw1", "sw3"), ("sw1", "sw4"), ("sw2", "sw3"), 
            ("sw2", "sw5"), ("sw3", "sw4"), ("sw3", "sw5"), ("sw4", "sw5")
        ],
        "positions": {
            "sw1": (-1, 0), "sw2": (0, 1), "sw3": (0, 0), "sw4": (0, -1), "sw5": (1, 0)
        },
        "title": "Network Topology with 2 User and 3 Intermediate Switches"
    },
    "3_u_3_i": {
        "user_switches": ["sw1", "sw2", "sw6"],
        "intermediate_switches": ["sw3", "sw4", "sw5"],
        "edges": [
            ("sw1", "sw3"), ("sw1", "sw4"), ("sw2", "sw4"), ("sw2", "sw5"), 
            ("sw3", "sw4"), ("sw4", "sw5"), ("sw3", "sw6"), ("sw4", "sw6"), ("sw5", "sw6")
        ],
        "positions": {
            "sw1": (-1, 1), "sw2": (-1, -1), "sw3": (0, 2), "sw4": (0, 0), "sw5": (0, -2), "sw6": (1, 0)
        },
        "title": "Network Topology with 3 User and 3 Intermediate Switches"
    },
    "4_u_3_i": {
        "user_switches": ["sw1", "sw2", "sw6", "sw7"],
        "intermediate_switches": ["sw3", "sw4", "sw5"],
        "edges": [
            ("sw1", "sw3"), ("sw1", "sw4"), ("sw2", "sw5"), ("sw2", "sw4"), 
            ("sw3", "sw4"), ("sw4", "sw5"), ("sw3", "sw6"), ("sw4", "sw6"), 
            ("sw4", "sw7"), ("sw5", "sw7")
        ],
        "positions": {
            "sw1": (-1, 1), "sw2": (-1, -1), "sw3": (0, 2), "sw4": (0, 0), "sw5": (0, -2), 
            "sw6": (1, 1), "sw7": (1, -1)
        },
        "title": "Network Topology with 4 User and 3 Intermediate Switches"
    },
    "4_u_4_i": {
        "user_switches": ["sw1", "sw2", "sw7", "sw8"],
        "intermediate_switches": ["sw3", "sw4", "sw5", "sw6"],
        "edges": [
            ("sw1", "sw3"), ("sw1", "sw4"), ("sw2", "sw5"), ("sw2", "sw6"), 
            ("sw3", "sw4"), ("sw3", "sw7"), ("sw4", "sw7"), ("sw4", "sw5"),
            ("sw5", "sw6"), ("sw5", "sw8"), ("sw6", "sw8")
        ],
        "positions": {
            "sw1": (-1, 2), "sw2": (-1, -2), "sw3": (0, 3), "sw4": (0, 1), 
            "sw5": (0, -1), "sw6": (0, -3), "sw7": (1, 2), "sw8": (1, -2)
        },
        "title": "Network Topology with 4 User and 4 Intermediate Switches"
    }
}

def get_topology(users_s,intermediate_s):
    return topologies[f"{users_s}_u_{intermediate_s}_i"]

def get_total_ports():
    return list(range(1, MAX_SWITCH_PORTS + 1))

def get_switch_ports(topology):
    edges = topology["edges"]
    # edges += [(b, a) for a, b in edges]
    """
    Assigns random ports to each edge in a bidirectional network.
    """
    remaining_ports = list(range(MAX_SWITCH_PORTS))
    random.shuffle(remaining_ports)
    interconnect_links = []
    switch_ports = []
    for edge in edges:
        port1, port2 = remaining_ports.pop(), remaining_ports.pop()
        interconnect_links.append([f"{edge[0]}-{edge[1]}", port1, port2])
        interconnect_links.append([f"{edge[1]}-{edge[0]}", port2, port1])
        switch_ports.extend([port1, port2])
    return remaining_ports, interconnect_links, switch_ports

def get_user_ports(remaining_ports, topology):
    """
    Assigns ports to users, ensuring every switch has at least one user assigned.
    Parameters:
        remaining_ports (list): List of available ports.
        topology (dict): Dictionary containing the topology, with a "user_switches" key.
    Returns:
        tuple: A list of user ports and a list of user assignments.
    """
    # Ensure we have enough ports for at least one user per switch
    num_switches = len(topology["user_switches"])
    if len(remaining_ports) < num_switches:
        raise ValueError("Not enough ports to assign at least one user per switch.")
    user_ports = []
    user_assignments = []
    # Step 1: Assign at least one user to each switch
    for i, switch in enumerate(topology["user_switches"]):
        port = remaining_ports.pop()
        user_ports.append(port)
        user_assignments.append((f"u{i + 1}", switch, port,random.choice(VLAN_C_RANGES),random.choice(VLAN_S_RANGES),random.choice(USE_CASES)))
    # Step 2: Randomly assign additional users
    remaining_users = random.randint(0, len(remaining_ports))  # Decide how many more users to assign
    for i in range(remaining_users):
        port = remaining_ports.pop()
        user_ports.append(port)
        user_assignments.append((f"u{len(user_assignments) + 1}", random.choice(topology["user_switches"]), port,random.choice(VLAN_C_RANGES),random.choice(VLAN_S_RANGES),random.choice(USE_CASES)))
    return user_ports, user_assignments

def find_interconnect_link(interconnect_links, switch1, switch2):
    found = False
    for link in interconnect_links:
        if link[0] == switch1 + "-" + switch2:
            return link
    if found == False:
        return switch1



def find_in_user_assignments(user_assignments, user1, user2):
    for user in user_assignments:
        if user[0] == user1:
            port1 = user[2]
            s_vlan1 = user[4]
            c_vlan1 = user[3]
            use_case1 = user[5]
        if user[0] == user2:
            port2 = user[2]
            s_vlan2 = user[4]
            c_vlan2 = user[3]
            use_case2 = user[5]
    return user1,port1,user2,port2,s_vlan1,s_vlan2,c_vlan1,c_vlan2,use_case1,use_case2

def get_routes(user_assignments, interconnect_links,paths   ):
    routes = []
    for path in paths:
        temp = []
        user1,port1,user2,port2,s_vlan1,s_vlan2,c_vlan1,c_vlan2,use_case1,use_case2 = find_in_user_assignments(user_assignments, path[0][0], path[0][1])
        if len(path[0][2]) == 1:
            temp.append(find_interconnect_link(interconnect_links, path[0][2][0], path[0][2][0]))

        for i in range(len(path[0][2])-1):
            temp.append(find_interconnect_link(interconnect_links, path[0][2][i], path[0][2][i+1]))
        routes.append([user1, port1, user2, port2, temp,use_case1,[c_vlan1],[s_vlan1]])
    return routes
            
def pick_path_btwn_users(user_assignments, all_paths_btwn_sws):
    user_paths = []
    for user1, switch1, port1, vlan_c1, vlan_s1, use_case1 in user_assignments:
        for user2, switch2, port2, vlan_c2, vlan_s2,use_case2 in user_assignments:
            if user1 != user2:
                if switch1 != switch2:
                    for paths in all_paths_btwn_sws:
                        if (switch1==paths[0] and switch2==paths[1]):
                            temp = []
                            temp.append([user1,user2,random.choice(paths[2])])
                            user_paths.append(temp)
                else:
                    user_paths.append([[user1,user2,[switch1]]])

    return user_paths

def find_all_paths(edges, source, target):
    """
    Finds all possible paths between source and target in a directed graph, 
    including bidirectional paths.
    Returns a list containing the source, target, and all paths.
    """
    # Create the directed graph
    G = nx.DiGraph()
    # Add bidirectional edges (both directions for each edge)
    for u, v in edges:
        G.add_edge(u, v)
        G.add_edge(v, u)
    # Find all simple paths
    all_paths = list(nx.all_simple_paths(G, source=source, target=target))
    # Filter paths of length 5 or less
    filtered_paths = [path for path in all_paths if len(path) <= 5]
    # Store the source, target, and paths
    result = [source, target, filtered_paths]
    return result

def get_paths_btwn_sws(topology):
    user_switches = topology["user_switches"]
    intermediate_switches = topology["intermediate_switches"]
    all_switches = user_switches + intermediate_switches
    sws_communication = []
    for i in range(len(all_switches)):
        for j in range(i+1, len(all_switches)):
            sws_communication.append(find_all_paths(topology["edges"], all_switches[i], all_switches[j]))
            sws_communication.append(find_all_paths(topology["edges"], all_switches[j], all_switches[i]))
    return sws_communication

def assign_labels(ports, interconnect_links, users):
    """
    Assigns labels to ports based on interconnect links and user ports.
    """
    # Assign interconnect link labels
    port_labels = {link[1]: link[0] for link in interconnect_links}
    port_labels.update({link[2]: link[0] for link in interconnect_links})
    
    # Assign user port labels
    port_labels.update({user["port"]: user["user"] for user in users})
    
    return dict(sorted(port_labels.items()))


def setup_network():
    total_ports = get_total_ports()
    print("Total ports: ", total_ports)
    #Get the topology
    topology = get_topology(2,2).copy()
    remaining_ports, interconnect_links, switch_ports = get_switch_ports(topology)
    print("Switch Ports: ", switch_ports)
    print("Interconnect Links: ", interconnect_links)
    user_ports, user_assignments = get_user_ports(remaining_ports, topology)
    print("User Ports: ", user_ports)
    print("User Assignments: ", user_assignments)
    all_paths_btwn_sws = get_paths_btwn_sws(topology)
    users_paths = pick_path_btwn_users(user_assignments, all_paths_btwn_sws)
    print("Users Paths: ", users_paths)
    routes = get_routes(user_assignments, interconnect_links, users_paths)
    #print("Routes: ", routes)
    for route in routes:
        print(route)
    users = [{"user": ua[0], "switch": ua[1], "port": ua[2]} for ua in user_assignments]
    port_labels = assign_labels(range(MAX_SWITCH_PORTS), interconnect_links, users)
    print("Port Labels: ", port_labels)

    return total_ports, user_ports, switch_ports, interconnect_links, routes, port_labels




    


# setup_network()