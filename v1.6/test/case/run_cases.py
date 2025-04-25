import subprocess
import os
import glob

try:
    log_files = glob.glob("../python_scripts/logs/*.txt")
    if log_files:
        print("Cleaning up old log files...")
        for f in log_files:
            os.remove(f)

    pkt_files = glob.glob("../python_scripts/pkt/*.txt")
    if pkt_files:
        print("Cleaning up old pkt files...")
        for f in pkt_files:
            os.remove(f)


    for case_number in range(1,48):
        print(f"\n🔧 Running case {case_number}...")

        # Build the shell command for each case
        command = f"""
        CASE={case_number}; 
        script --flush --command="python3 ind_cases/${{CASE}}_case.py" /dev/null | 
        sed 's/\\x1b\\[[0-9;]*m//g' > "../python_scripts/pkt_data.txt" && 
        python3 ../python_scripts/get_pkt.py > "../python_scripts/pkt/${{CASE}}_pkt.txt" && 
        cp ../python_scripts/pkt_data.txt ../python_scripts/logs/${{CASE}}_case.txt
        """

        # command = f"""
        # CASE={case_number}; 
        # script --flush --command="python3 ind_cases/${{CASE}}_case.py" /dev/null | 
        # sed 's/\\x1b\\[[0-9;]*m//g' | tee "../python_scripts/pkt_data.txt" | 
        # python3 ../python_scripts/get_pkt.py | tee "../python_scripts/pkt/${{CASE}}_pkt.txt"; 
        # cp ../python_scripts/pkt_data.txt ../python_scripts/logs/${{CASE}}_case.txt"
        # """

        # Run the command using subprocess
        subprocess.run(command, shell=True, check=True)

        print(f"✅ Case {case_number} completed.")

    # Combine all pkt files into one while keeping individual files
    combined_pkt_path = "../python_scripts/pkt/combined_pkt.txt"

    # Find all individual pkt files
    pkt_files = sorted(glob.glob("../python_scripts/pkt/[0-9]*_pkt.txt"))

    # Combine them
    with open(combined_pkt_path, "w") as combined_file:
        for pkt_file in pkt_files:
            with open(pkt_file, "r") as f:
                combined_file.write(f"--- {os.path.basename(pkt_file)} ---\n")
                combined_file.write(f.read())
                combined_file.write("\n\n")

    print(f"Combined pkt data saved to {combined_pkt_path}")

    #Combine all logs into one while keeping individual files
    combined_log_path = "../python_scripts/logs/combined_logs.txt"
    # Find all individual log files
    log_files = sorted(glob.glob("../python_scripts/logs/[0-9]*_case.txt"))

    # Combine them
    with open(combined_log_path, "w") as combined_file:
        for log_file in log_files:
            with open(log_file, "r") as f:
                combined_file.write(f"--- {os.path.basename(log_file)} ---\n")
                combined_file.write(f.read())
                combined_file.write("\n\n")



except KeyboardInterrupt:
    print("\n⛔ Execution interrupted by user. Exiting gracefully.")
