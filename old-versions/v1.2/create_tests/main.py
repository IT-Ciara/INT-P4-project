import argparse
import time
import subprocess
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


import packet_generator as pg
import entry_generator as eg
import system_config as sc
import start_capture as scap
import compare_pkts as cpkts
import create_routes as tg
import final_results as fr


if __name__ == '__main__':
    # Argument parsing
    parser = argparse.ArgumentParser(description="Network simulation script with selectable components.")
    parser.add_argument("--new", action="store_true", help="Run with the default configuration.")
    parser.add_argument("--packets", action="store_true", help="Send packets with packet generator.")
    parser.add_argument("--all", action="store_true", help="Run all components.")
    
    args = parser.parse_args()
    
    if args.new:    
        # # TOPOLOGY MANAGER
        routes, interconnect_links = tg.setup_network()
    else:
        print("Running with the default routes and interconnect links.")
        routes = [
            #Case1 
            ['u0',0,'u1',1,[['sw1']],'No VLAN translation',[10],[101]],
            #Case2
            ['u0',0,'u1',1,[['sw1']],'With VLAN range (No translation)',[20],[201]],
            #Case3
            ['u0',0,'u1',1,[['sw1']],'No VLAN U1 with VLAN U2',[30],[301]],
            #Case4
            ['u0',0,'u1',1,[['sw1']],'VLAN translation',[40],[401]],
            #Case5
            ['u4',10,'u3',9,[['sw6']],'No VLAN',[50],[501]],
            #Case6
            ['u2',8,'u1',1,[['sw6-sw5',11,12],['sw5-sw3',13,14],['sw3-sw1',15,16]],'No VLAN translation',[60],[601]],
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

    # Generate entries
    pkt_route_details, pkt_in_out = eg.generate_entries(routes)

    # Run bfshell command using subprocess and suppress all output
    command = ["bash", "/home/xdp-int/P4-INT/mysde/bf-sde-9.13.1/run_bfshell.sh", 
        "-b", "/home/xdp-int/INT-P4-Project/v1.2/create_tests/bfrt_python/entries.py"]

    # Run the command and suppress all output
    result = subprocess.run(" ".join(command), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    case = 1
    # Main packet generation loop
    for pkt in pkt_route_details:
        image = mpimg.imread(f"figures/case{case}.png")
        print("\n\n\n")
        
        # Define constants
        total_characters = 140
        array_str = str(pkt[3])
        
        # Calculate remaining dashes
        remaining = total_characters - len(array_str) - len("*---------------------- ") - len(" ----------------------*")
        left_dashes = remaining // 2
        right_dashes = remaining - left_dashes
        
        # Print the header dynamically
        print("#" + "*" * (total_characters - 2) + "*")
        print(f"*{'-' * left_dashes} {array_str} {'-' * right_dashes}*")
        print("#" + "*" * (total_characters - 2) + "*")
        # Display the topology image using matplotlib
        plt.imshow(image)
        plt.axis('off')  # Disable axis for cleaner visualization
        plt.title(f"Topology: Case {case}. Use case: {pkt[3][5]}")
        plt.show(block=False)  # Show non-blocking image
        plt.pause(6)  # Keep the image displayed for 6 seconds
        # Start packet capture in the background
        scap.start_capture(4, case)
        time.sleep(3)
        # Generate the packet
        pg.create_packet(pkt[0], pkt[1])
        # Allow some time between packets
        time.sleep(3)
        cpkts.compare_packets(case)
        plt.close()  # Close the figure

        # Get the final results of the test case
        print("\n\n\n############################################################################")
        print(f"- - - - - F I N A L   R E S U L T S - - - - -")
        fr.get_final_results(case, pkt[3][5], len(pkt[3][4]))
        print("############################################################################n\n\n")
        case += 1



