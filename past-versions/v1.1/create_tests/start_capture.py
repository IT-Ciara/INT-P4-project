import os 

pcap_path ="./wireshark"
def start_capture(time,case):
    cmd = f"sudo tshark -i veth0 -i veth2 -i veth4 -i veth6 -i veth8 -i veth10 -i veth12 -i veth14 -i veth16 -i veth18 -i veth20 -i veth22 -i veth24 -i veth26 -i veth28 -i veth30 -i veth32 -i veth34 -i veth36 -i veth38 -i veth40 -i veth42 -i veth44 -i veth46 -i veth48 -i veth50 -i veth52 -w {pcap_path}/case{case}.pcap -a duration:{time} &"    
    os.system(cmd)
    print("Capture completed")