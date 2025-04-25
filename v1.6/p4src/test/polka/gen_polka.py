from polka.tools import create_list_irrpoly_mod2, calculate_routeid
import random
import json

# --- Input: Number of Core Nodes ---
while True:
    try:
        num_core_nodes = int(input("Enter the number of core nodes (1-4): "))
        if 1 <= num_core_nodes <= 4:
            break
        print("Please enter a number between 1 and 4.")
    except ValueError:
        print("Invalid input. Please enter a number.")

print(f"\nNumber of core nodes: {num_core_nodes}")

# --- Generate Core Node Polynomials & Output Ports ---
polys = create_list_irrpoly_mod2(16)
nodes, output_ports = [], []
ports = [2,2,2]
# ports = [64,64,64]

for _ in range(num_core_nodes):
    poly = polys.pop(0)  # Use and remove the first available irreducible polynomial
    # port = random.randint(1, 15)  # Avoid 0 to reduce risk of invalid routes
    port = ports.pop(0)  # Use and remove the first available port
    port_bits = [int(b) for b in bin(port)[2:].zfill(4)]

    nodes.append(poly)
    output_ports.append(port_bits)

# --- Calculate Route ID ---
routeid = calculate_routeid(nodes, output_ports)
binary_string = "".join(str(bit) for bit in routeid)

print("\n\n====================== Route ID ======================")
print("List Route ID:     ", routeid)
print("Decimal Route ID:  ", int(binary_string, 2))
print("Hex Route ID:      ", hex(int(binary_string, 2)))
print("Binary Route ID:   ", binary_string)
print("======================================================\n")

# --- Build JSON Output ---
nodes_json = {
    "route": {
        "values": {
            "int_route_id": int(binary_string, 2),
            "bin_route_id": binary_string,
            "hex_route_id": hex(int(binary_string, 2)),
        },
        "nodes": {
            "num_of_nodes": num_core_nodes
        }
    },
    "nodes": {}
}

# --- Print & Store Each Node's Info ---
print("========================= Nodes =========================")
for i in range(num_core_nodes):
    node = nodes[i]
    port = output_ports[i]

    node_str = ''.join(map(str, node))
    port_str = ''.join(map(str, port))

    dec_node = int(node_str, 2)
    hex_node = hex(dec_node)
    bin_node = node_str

    dec_port = int(port_str, 2)
    hex_port = hex(dec_port)
    bin_port = port_str

    print(f"\n---------------------- Node {i + 1} ----------------------")
    print("Node ID:")
    print("  List:     ", node)
    print("  Decimal:  ", dec_node)
    print("  Hex:      ", hex_node)
    print("  Binary:   ", bin_node)

    print("Output Port:")
    print("  List:     ", port)
    print("  Decimal:  ", dec_port)
    print("  Hex:      ", hex_port)
    print("  Binary:   ", bin_port)

    nodes_json["nodes"][f"node_{i+1}"] = {
        "id": {
            "hex_node_id": hex_node,
            "bin_node_id": bin_node,
            "dec_node_id": dec_node
        },
        "output_port": {
            "hex_output_port": hex_port,
            "bin_output_port": bin_port,
            "dec_output_port": dec_port
        }
    }

# --- Write JSON to File ---
with open("./polka/route_info.json", "w") as f:
    json.dump(nodes_json, f, indent=4)

print("\n✅ Route information saved to 'route_info.json'")
