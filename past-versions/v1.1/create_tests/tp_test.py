import random
import itertools
import matplotlib.pyplot as plt
import networkx as nx
import random

# Constants
MAX_SWITCH_PORTS = 12
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
    "two_u_two_i": {
        "user_switches": ["sw1", "sw4"],
        "intermediate_switches": ["sw2", "sw3"],
        "edges": [("sw1", "sw2"), ("sw1", "sw3"), ("sw2", "sw3"), ("sw2", "sw4"), ("sw3", "sw4")],
        "positions": {
            # "sw1": (-1, 0), "sw2": (0, 1), "sw3": (0, -1), "sw4": (1, 0)
            "sw1": (-1, 0), "sw2": (0, 0.2), "sw3": (0, -0.2), "sw4": (1, 0)
        },
        "title": "Network Topology with 2 User and 2 Intermediate Switches"
    },
    "two_u_three_i": {
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
    "three_u_three_i": {
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
    "four_u_three_i": {
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
    "four_u_four_i": {
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


def assign_ports(edges):
    """
    Assigns random ports to each edge in a bidirectional network.
    """
    total_ports = list(range(MAX_SWITCH_PORTS))
    random.shuffle(total_ports)
    interconnect_links = []
    switch_ports = []

    for edge in edges:
        port1, port2 = total_ports.pop(), total_ports.pop()
        interconnect_links.append([f"{edge[0]}-{edge[1]}", port1, port2])
        interconnect_links.append([f"{edge[1]}-{edge[0]}", port2, port1])
        switch_ports.extend([port1, port2])

    return total_ports, interconnect_links, switch_ports

def draw_topology(edges, positions, title, users):
    """
    Draws a network topology with switches and users.
    """
    G = nx.DiGraph()
    G.add_edges_from(edges)

    user_positions = {}
    user_edges = []
    user_offset = {switch: 0.5 for switch in positions.keys()}

    for user_info in users:
        user, switch = user_info['user'], user_info['switch']
        user_positions[user] = (
            positions[switch][0] * 1.5,
            positions[switch][1] + user_offset[switch]
        )
        user_offset[switch] -= 0.5
        user_edges.append((user, switch))

    combined_positions = {**positions, **user_positions}
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_nodes(
        G, combined_positions, node_size=2000, node_color='lightblue',
        nodelist=positions.keys(), label="Switches"
    )
    nx.draw_networkx_edges(G, combined_positions, edgelist=edges, arrows=True)
    nx.draw_networkx_labels(G, combined_positions, labels={node: node for node in positions.keys()})
    G.add_edges_from(user_edges)
    nx.draw_networkx_nodes(
        G, combined_positions, node_size=1000, node_color='orange',
        nodelist=user_positions.keys(), label="Users"
    )
    nx.draw_networkx_edges(G, combined_positions, edgelist=user_edges, style="dashed")
    nx.draw_networkx_labels(G, combined_positions, labels={node: node for node in user_positions.keys()})
    plt.title(title, fontsize=16)
    plt.axis("off")
    plt.show()

def find_all_paths(edges, source, target):
    """
    Finds all possible paths between source and target in a directed graph.
    """
    G = nx.DiGraph()
    G.add_edges_from(edges)
    all_paths = list(nx.all_simple_paths(G, source=source, target=target))
    return [path for path in all_paths if len(path) <= 5]

def assign_labels(ports, interconnect_links, users):
    """
    Assigns labels to ports based on interconnect links and user ports.
    """
    port_labels = {link[1]: link[0] for link in interconnect_links}
    port_labels.update({link[2]: link[0] for link in interconnect_links})
    port_labels.update({user[1]: user[0] for user in users})
    return dict(sorted(port_labels.items()))

def find_communication_combinations(user_assignments, edges):
    """
    Finds communication combinations and their paths between users.
    """
    communications = []
    for i in range(len(user_assignments)):
        for j in range(i + 1, len(user_assignments)):
            user1, user2 = user_assignments[i], user_assignments[j]
            source_switch, target_switch = user1[1], user2[1]
            all_paths = find_all_paths(edges, source_switch, target_switch)
            if all_paths:
                path = random.choice(all_paths)
                communications.append({
                    "from_user": user1[0],
                    "to_user": user2[0],
                    "from_switch": source_switch,
                    "to_switch": target_switch,
                    "all_paths": path
                })
    return communications

# Main Function to Orchestrate the Setup
def setup_network():
    """Orchestrates network setup by allocating ports, creating interconnect links, generating routes with VLAN details, and assigning labels."""
    total_ports = list(range(MAX_SWITCH_PORTS))  # Define total available ports
    
    # Get topology details
    topology = topologies["two_u_two_i"].copy()
    edges = topology["edges"].copy()

    # Add reverse edges for bidirectional all_paths
    edges += [(b, a) for a, b in edges]
    positions = topology["positions"]
    title = topology["title"]

    user_ports, interconnect_links, switch_ports = assign_ports(topology["edges"])
    num_users = random.randint(2, len(user_ports))
    user_assignments = [
        (f"u{i + 1}", random.choice(topology["user_switches"]), user_ports.pop())
        for i in range(num_users)
    ]
    users = [{"user": ua[0], "switch": ua[1], "port": ua[2]} for ua in user_assignments]

    draw_topology(edges, positions, title, users)

    communications = find_communication_combinations(user_assignments, edges)
    routes = []

    for communication in communications:
        from_user, to_user = communication["from_user"], communication["to_user"]
        from_user_info = next(user for user in users if user["user"] == from_user)
        to_user_info = next(user for user in users if user["user"] == to_user)
        temp = [
            from_user, from_user_info["port"], to_user, to_user_info["port"],
            communication["all_paths"],
            random.choice(USE_CASES),
            random.sample(VLAN_C_RANGES, 1),
            random.sample(VLAN_S_RANGES, 1)
        ]
        routes.append(temp)

    port_labels = assign_labels(range(MAX_SWITCH_PORTS), interconnect_links, users)
    return user_ports, switch_ports, interconnect_links, routes, port_labels

setup_network()


