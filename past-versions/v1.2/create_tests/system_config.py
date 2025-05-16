import subprocess

# Step 5: Switch Configuration Management
def reset_bridge():
    """Resets the bridge by deleting and recreating it."""
    print("Resetting bridge configuration...")
    commands = [
        ("Deleting bridge", "sudo ovs-vsctl del-br ovs-br0"),
        ("Creating bridge", "sudo ovs-vsctl add-br ovs-br0"),
    ]
    for action, cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"{action}:", "Success" if result.returncode == 0 else result.stderr)

# Step 6: Veth Pair Creation for Interconnections
def create_veth_pairs(pair_count=34, additional_pairs=("veth250", "veth251")):
    """Creates veth pairs for switch-to-switch connections, clearing any existing pairs."""
    print("Removing existing veth pairs...")
    for i in range(pair_count):
        subprocess.run(f"sudo ip link del veth{i}", shell=True, capture_output=True, text=True)
    for pair in additional_pairs:
        subprocess.run(f"sudo ip link del {pair}", shell=True, capture_output=True, text=True)
    
    print("Creating new veth pairs...")
    for i in range(pair_count):
        peer = i + 1
        subprocess.run(f"sudo ip link add veth{i} type veth peer name veth{peer}", shell=True, capture_output=True, text=True)
        subprocess.run(f"sudo ip link set veth{i} up", shell=True, capture_output=True, text=True)
    
    for pair in additional_pairs:
        peer = pair.replace("veth", "veth" + str(int(pair[-1]) + 1))
        subprocess.run(f"sudo ip link add {pair} type veth peer name {peer}", shell=True, capture_output=True, text=True)
        subprocess.run(f"sudo ip link set {pair} up", shell=True, capture_output=True, text=True)

# Step 7: Adding Ports to the Bridge
def configure_bridge_ports(interconnect_links):
    """Adds specified veth pairs to the bridge and sets OpenFlow rules for bidirectional flow."""
    for link in interconnect_links:
        print(f"Configuring ports {link[1]} and {link[2]} on bridge {link[0]}...")
        veth_out, veth_in = f"veth{link[1]*2+1}", f"veth{link[2]*2+1}"
        print(f"Adding ports {veth_out} and {veth_in} to bridge {link[0]}...")
        
        subprocess.run(f"sudo ovs-vsctl add-port ovs-br0 {veth_out}", shell=True, capture_output=True, text=True)
        subprocess.run(f"sudo ovs-vsctl add-port ovs-br0 {veth_in}", shell=True, capture_output=True, text=True)
        
        # Add OpenFlow rules for bidirectional communication
        flows = [
            f"sudo ovs-ofctl add-flow ovs-br0 \"in_port={veth_out},actions=output:{veth_in}\"",
            f"sudo ovs-ofctl add-flow ovs-br0 \"in_port={veth_in},actions=output:{veth_out}\""
        ]
        for flow in flows:
            subprocess.run(flow, shell=True, capture_output=True, text=True)
    
    print("\nBridge configuration complete.")
    subprocess.run("sudo ovs-vsctl show", shell=True, capture_output=True, text=True)

# Main function to configure the network
def configure_network(interconnect_links):
    """Main function to orchestrate the network setup by resetting the bridge, creating veth pairs, and configuring bridge ports."""
    
    # Step 1: Reset the bridge
    reset_bridge()
    
    # Step 2: Create veth pairs for interconnections
    # create_veth_pairs()
    
    # Step 3: Configure bridge ports and set up flows
    configure_bridge_ports(interconnect_links)


