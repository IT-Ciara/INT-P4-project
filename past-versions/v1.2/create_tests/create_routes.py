import random
from itertools import combinations

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
    "1.5u-6s": {
        "users": [("u0", "port0"), ("u1", "port1"), ("u2", "port8"), ("u3", "port9"), ("u4", "port10")],
        "u_switches": ["sw1", "sw6"],
        "paths": [
            [("sw1", "port2"), ("port3", "sw2", "port4"), ("port5", "sw4", "port6"), ("port7", "sw6")],
            [("sw1", "port16"), ("port15", "sw3", "port14"), ("port13", "sw5", "port12"), ("port11", "sw6")],
        ],
        "total_ports": 17,
    },
    "2.7u-4s": {
        "users": [("u0", "port0"), ("u1", "port1"), ("u2", "port2"), ("u3", "port3"), ("u4", "port8"), ("u5", "port9"), ("u6", "port10")],
        "u_switches": ["sw1", "sw4"],
        "paths": [
            [("sw1", "port4"), ("port5", "sw2", "port6"), ("port7", "sw4")],
            [("sw1", "port14"), ("port13", "sw3", "port12"), ("port11", "sw4")],
        ],
        "total_ports": 14,
    },
    "3.5u-7s": {
        "users": [("u0", "port0"), ("u1", "port1"), ("u2", "port8"), ("u3", "port9"), ("u4", "port10")],
        "u_switches": ["sw1", "sw4", "sw5"],
        "paths": [
            [("sw1", "port2"), ("port3", "sw2", "port4"), ("port5", "sw3", "port6"), ("port7", "sw4")],
            [("sw1", "port16"), ("port15", "sw7", "port14"), ("port13", "sw6", "port12"), ("port11", "sw5")],
            [("sw4", "port7"), ("port6", "sw3", "port5"), ("port4", "sw2", "port3"), ("port2", "sw1", "port16"), ("port15", "sw7", "port14"), ("port13", "sw6", "port12"), ("port11", "sw5")],
        ],
        "total_ports": 17,
    },
    "4.5u-6s": {
        "users": [("u0", "port0"), ("u1", "port1"), ("u2", "port8"), ("u3", "port9"), ("u4", "port10")],
        "u_switches": ["sw1", "sw4", "sw6"],
        "paths": [
            [("sw1", "port2"), ("port3", "sw2", "port4"), ("port5", "sw3", "port6"), ("port7", "sw4")],
            [("sw1", "port2"), ("port3", "sw2", "port4"), ("port5", "sw3", "port12"), ("port11", "sw6")],
            [("sw1", "port16"), ("port15", "sw5", "port14"), ("port13", "sw3", "port6"), ("port7", "sw4")],
            [("sw1", "port16"), ("port15", "sw5", "port14"), ("port13", "sw3", "port12"), ("port11", "sw6")],
            [("sw4", "port7"), ("port6", "sw3", "port12"), ("port11", "sw6")],

        ],
        "total_ports": 17,
    },
    "5.3u-7s": {
        "users": [("u0", "port0"), ("u1", "port9"), ("u2", "port10")],
        "u_switches": ["sw1", "sw5", "sw6"],
        "paths": [
            [("sw1", "port1"), ("port2", "sw2", "port3"), ("port4", "sw3", "port5"), ("port6", "sw4", "port7"), ("port8", "sw5")],
            [("sw1", "port1"), ("port2", "sw2", "port3"), ("port4", "sw3", "port12"), ("port11", "sw6")],
            [("sw1", "port16"), ("port15", "sw7", "port14"), ("port13", "sw3", "port5"), ("port6", "sw4", "port7"), ("port8", "sw5")],
            [("sw1", "port16"), ("port15", "sw7", "port14"), ("port13", "sw3", "port12"), ("port11", "sw6")],
            [("sw5","port8"),("port7","sw4","port6"),("port5","sw3","port12"),("port11","sw6")],
        ],
        "total_ports": 17,
    },
}


def replace_ports_with_random_numbers(users, paths, total_ports):
    
    available_numbers = list(range(0, 18))
    random_ports = [f"port{num}" for num in range(total_ports + 1)]

    random.shuffle(available_numbers)

    port_map = {port: available_numbers.pop() for port in random_ports}

    def replace_path_item(item):
        if isinstance(item, tuple):
            return tuple(port_map.get(x, x) for x in item)
        return port_map.get(item, item)

    updated_paths = [[replace_path_item(x) for x in path] for path in paths]
    updated_users = [replace_path_item(user) for user in users]

    return updated_users, updated_paths


def user_communications(users):
    return list(combinations(users, 2))


def assign_users_to_switches(users, switches):
    random.shuffle(users)  # Shuffle the users randomly
    switch_user_map = {switch: [] for switch in switches}  # Initialize switch-to-user mapping

    for i, user in enumerate(users):
        switch = switches[i % len(switches)]  # Assign switch based on index
        switch_user_map[switch].append(user)  # Add user to the switch mapping
        
        # Convert the user tuple to a list, add additional attributes, and convert back to tuple
        user = list(user)
        user.extend([switch, random.choice(USE_CASES), random.choice(VLAN_C_RANGES), random.choice(VLAN_S_RANGES)])
        users[i] = tuple(user)  # Update the user in the original list
        
        print(f"User: {user}")  # Debugging output

    return switch_user_map, users



def find_path_between_users(user1, user2, paths):
    available_paths = []
    if user1[2] == user2[2]:  # Same switch
        return [user1[2]]
    # f"Same switch: {user1[2]}"
    else:
        for path in paths:
            if (path[0][0] == user1[2] and path[-1][1] == user2[2]) or (path[0][0] == user2[2] and path[-1][1] == user1[2]):
                available_paths.append(path)

        if available_paths:
            return random.choice(available_paths)
        else:
            return "No available path"

def invert_route(route):
    # Invert the route
    inverted_route = []
    #Iterate backwards through the route
    for i in range(len(route)-1, -1, -1):
        temp = []
        # Invert the switch names
        switches = route[i][0].split("-")
        # print(f"Switches: {switches}")
        # print(f"{switches[1]}-{switches[0]}")
        temp.append(f"{switches[1]}-{switches[0]}")
        # Invert the ports
        temp.append(route[i][2])
        temp.append(route[i][1])
        # print(f"Temp: {temp}")
        inverted_route.append(temp)

    return inverted_route

def convert_path_format(user1, user2, path):
    """
    Converts the path between two users into the desired format.
    """
    temp = []
    user1_id = user1[0]
    port1 = user1[1]
    # print("\n\nUser1:", user1, "User1_id:", user1_id, "Port1:", port1)
    user2_id = user2[0]
    port2 = user2[1]
    # print("User2:", user2, "User2_id:", user2_id, "Port2:", port2)
    # print("Path:", path)
    temp.append(user1_id)
    temp.append(port1)
    temp.append(user2_id)
    temp.append(port2)
    route = []
    reverse = False
    if len(path) >1:
        for i in range(len(path)):
            if i == 0:
                if path[i][0] != user1[2]:
                    reverse = True
                    # print(f"{path[i][0]},{user1[2]},Reverse, {reverse}")
                    
                # print(f"[\"{path[i][0]}-{path[i+1][1]}\",{path[i][1]},{path[i+1][0]}]")
                route.append([f"{path[i][0]}-{path[i+1][1]}", path[i][1], path[i+1][0]])
            elif i != len(path)-1:
                # print(f"[\"{path[i][1]}-{path[i+1][1]}\",{path[i][2]},{path[i+1][0]}]")
                route.append([f"{path[i][1]}-{path[i+1][1]}", path[i][2], path[i+1][0]])
    else:
        route.append(user1[2])
        

    if reverse:
        route = invert_route(route)

    temp.append(route)
    temp.append(user2[3])
    temp.append([user2[4]])
    temp.append([user2[5]])
    return temp


def get_interconnect_links(routes):
    interconnect_links = []
    for user1,port1,user2,port2,route,use_case,vlan_c,vlan_s in routes:
        if(len(route)>1):
            for i in range(len(route)-1):
                #Check if the link already exists
                if (route[i] not in interconnect_links):
                    interconnect_links.append(route[i])
    print("\nInterconnect Links:")
    print(interconnect_links)
    return interconnect_links


def setup_network():
    topology_name = random.choice(list(topologies.keys()))
    # topology_name = "4.5u-6s"
    topology = topologies[topology_name]
    print(f"Selected topology: {topology_name}")

    updated_users, updated_paths = replace_ports_with_random_numbers(
        topology["users"], topology["paths"], topology["total_ports"]
    )

    print("Updated users with random port numbers:")
    print(updated_users)

    print("Updated paths with random port numbers:")
    for path in updated_paths:
        print(path)

    user_to_switch_map, updated_users = assign_users_to_switches(updated_users, topology["u_switches"])
    print("\nUser-to-Switch Mapping:")
    for switch, assigned_users in user_to_switch_map.items():
        print(f"{switch}: {assigned_users}")

    print("\nUpdated users with switch:")
    for user in updated_users:
        print(user)

    communications = user_communications(updated_users)
    print("\nUser Communications:")
    for comm in communications:
        print(comm)

    routes = []
    print("\nPaths Between Users:")
    for comm in communications:
        user1, user2 = comm
        path = find_path_between_users(user1, user2, updated_paths)
        print(f"\nPath between {user1} and {user2}: {path}")
        converted_path = convert_path_format(user1, user2, path)
        print(f"Converted path: {converted_path}")
        routes.append(converted_path)

    interconnect_links = get_interconnect_links(routes)

    ##Total ports
    return routes, interconnect_links

