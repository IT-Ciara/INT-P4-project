import subprocess
import argparse
import unittest

def run_script(script_name, all_flag):
    command = f"python3 main_tests/{script_name}"
    if all_flag:
        command += " --all"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run all main test scripts.")
    parser.add_argument("--all", action="store_true", help="Run all steps in each script.")

    args = parser.parse_args()

    run_script("main_stage_2.py", args.all)
    run_script("main_stage_3.py", args.all)
    run_script("main_stage_4.py", args.all)
    run_script("main_stage_5.py", args.all)
    # run_script("main_stage_6.py", args.all)
    

    print("All tests completed.")

if __name__ == "__main__":
    main()