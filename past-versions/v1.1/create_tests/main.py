import time
import argparse
import subprocess
import os

import packet_generator as pm
import system_config as sc
import topology_generator as tg
import topology_visualization as tv
import entry_generator as eg
import start_capture as scap
import compare_pkts as cpkts

#Main function
if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Network simulation script with selectable components.")
    parser.add_argument("--new", action="store_true", help="Run with the default configuration.")
    parser.add_argument("--packets", action="store_true", help="Send packets with packet generator.")
    parser.add_argument("--all", action="store_true", help="Run all components.")
    
    args = parser.parse_args()
    
    if args.new:
        # TOPOLOGY MANAGER
        total_ports, user_ports, switch_ports, interconnect_links, routes, port_labels = tg.setup_network()
        print("Interconnect Links:")
        for link in interconnect_links:
            print(link)
        #TOPOLOGY VISUALIZATION
        tv.draw_labels_on_image(port_labels)
    else:
        print("Running with the default routes and interconnect links.")
        routes = [
            #Case1 
            # ['u0',0,'u1',1,[['sw1']],'No VLAN translation',[10],[101]],
            # #Case2
            # ['u0',0,'u1',1,[['sw1']],'With VLAN range (No translation)',[20],[201]],
            # #Case3
            # ['u0',0,'u1',1,[['sw1']],'No VLAN U1 with VLAN U2',[30],[301]],
            # #Case4
            # ['u0',0,'u1',1,[['sw1']],'VLAN translation',[40],[401]],
            # #Case5
            # ['u1',1,'u0',0,[['sw1']],'No VLAN',[50],[501]],

            # #Case6
            # ['u2',8,'u1',1,[['sw6-sw5',11,12],['sw5-sw3',13,14],['sw3-sw1',15,16]],'No VLAN translation',[60],[601]],
            #Case7
            ['u3',9,'u1',1,[['sw6-sw5',11,12],['sw5-sw3',13,14],['sw3-sw1',15,16]],'With VLAN range (No translation)',[70],[701]],
            #Case8
            ['u2',8,'u1',1,[['sw6-sw5',11,12],['sw5-sw3',13,14],['sw3-sw1',15,16]],'No VLAN U1 with VLAN U2',[80],[801]],
            #Case9
            ['u3',9,'u1',1,[['sw6-sw5',11,12],['sw5-sw3',13,14],['sw3-sw1',15,16]],'VLAN translation',[90],[901]],
            #Case10
            ['u1',1,'u4',10,[['sw1-sw2',2,3],['sw2-sw4',4,5],['sw4-sw6',6,7]],'No VLAN',[100],[1001]]
            ]

        interconnect_links = [
            ['sw1-sw2',2,3],
            ['sw2-sw4',4,5],
            ['sw4-sw6',6,7],
            ['sw1-sw3',16,15],
            ['sw3-sw5',14,13],
            ['sw5-sw6',12,11]
        ]

    # SYSTEM CONFIGURATION
    sc.configure_network(interconnect_links)
    #ENTRY GENERATOR AND GENERATE PACKETS
    pkt_route_details,pkt_in_out = eg.generate_entries(routes)
    # Run bfshell command using subprocess and suppress all output
    command = ["bash", "/home/xdp-int/P4-INT/mysde/bf-sde-9.13.1/run_bfshell.sh", 
        "-b", "/home/xdp-int/INT-P4-Project/v1.1/create_tests/bfrt_python/entries.py"]
    # Run the command and suppress all output
    result = subprocess.run(" ".join(command), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    case = 1
    # Main packet generation loop
    for pkt in pkt_route_details:
        print(f"\n\n\n")
        print(f"\n#*-------------------------------------------------------------------------------------------------------------------------------*")
        print(f"*------------ {pkt[3]} ------------*")
        print(f"#*-------------------------------------------------------------------------------------------------------------------------------*")
        # Start packet capture in the background
        scap.start_capture(5,case)
        time.sleep(3)
        # Generate the packet
        pm.create_packet(pkt[0], pkt[1])
        # Allow some time between packets
        time.sleep(3)
        cpkts.compare_packets(case)
        case += 1

