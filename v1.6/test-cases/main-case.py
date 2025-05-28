from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
import time
import json
import numpy as np

# === Your actual logic ===
from functions.config_interface_utils import *
from functions.pipeline_stage_mapper import *
from functions.grpc_connection_utils import *
from polka_fns.polka_fn import *
from functions.case_utils import *
from functions.packet_utils import *
from functions.table_entry_utils import *
from functions.sniff_utils import *
from results_fns.validate_results import *
from scapy.all import *
import os

console = Console()

pipeline_steps = [
    "Clear Previous Entries",
    "Prepare Test Case Data",
    "Create Packet",
    "Install Entries",
    "Start Sniffer",
    "Send Packet",
    "Capture Results",
    "Validate Results"
]

def convert_to_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def create_status_table(status_map, case_number=1):
    table = Table(title=f"[bold blue]Test Case {case_number} Execution Status", expand=True)
    table.add_column("Step", style="cyan")
    table.add_column("Status", style="magenta")
    for step, status in status_map.items():
        table.add_row(step, status)
    return table

def create_summary_table(results):
    table = Table(title="[bold magenta]Final Test Summary", expand=True)
    table.add_column("Test Case ID", style="cyan", justify="center")
    table.add_column("Pkt Match", justify="center")
    table.add_column("Counter Match", justify="center")
    table.add_column("Final Result", justify="center")

    for test_id, pkt_result, counter_result, final_result in results:
        pkt_color = "green" if pkt_result == "Passed" else "red"
        ctr_color = "green" if counter_result == "Passed" else "red"
        final_color = "green" if final_result == "Passed" else "red"

        table.add_row(
            str(test_id),
            f"[{pkt_color}]{pkt_result}",
            f"[{ctr_color}]{counter_result}",
            f"[{final_color}]{final_result}"
        )

    return table

def main():
    interface, dev_tgt, bfrt_info = gc_connect()
    cases_df, Stg_tbls_df, indirect_counter_df, counters_df = get_all_dfs('./functions/cases.xlsx')
    stages = get_main_stages(bfrt_info, Stg_tbls_df, indirect_counter_df)
    add_polka_registers(dev_tgt, bfrt_info, selected_node=1, TARGET="tf1_model")

    test_results = []
    case=10
    # for idx in range(0,case):
    for idx in range(len(cases_df)):
        case_tmp = cases_df.iloc[idx]
        case_id = case_tmp['Case'] if 'Case' in case_tmp else idx + 1

        step_status = {step: "[yellow]Pending" for step in pipeline_steps}

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            expand=True
        )
        task = progress.add_task("Running Test Case", total=len(pipeline_steps))

        layout = Group(create_status_table(step_status, case_id), progress)
        os.system('cls' if os.name == 'nt' else 'clear')

        with Live(layout, refresh_per_second=10, console=console):
            current_step = None

            def update_step(step_name):
                nonlocal current_step
                current_step = step_name
                step_status[step_name] = "[blue]In Progress"
                layout.renderables[0] = create_status_table(step_status, case_id)
                progress.update(task, description=step_name)

            def complete_step(step_name):
                progress.advance(task)
                step_status[step_name] = "[green]Done"
                layout.renderables[0] = create_status_table(step_status, case_id)

            try:
                update_step("Clear Previous Entries")
                clear_all(stages, dev_tgt, bfrt_info)
                complete_step("Clear Previous Entries")

                update_step("Prepare Test Case Data")
                case_stg = update_case_staging(case_tmp, {})
                case_stg = add_stages_tables(case_tmp, stages, case_stg)
                case_stg = add_pkt_values(case_tmp, case_stg)
                with open(f"case.json", "w") as f:
                    json.dump(convert_to_serializable(case_stg), f, indent=4)
                complete_step("Prepare Test Case Data")

                update_step("Create Packet")
                original_pkt = create_pkts(case_stg['pkt_values'])
                complete_step("Create Packet")

                update_step("Install Entries")
                create_entries_main(case_stg, dev_tgt, bfrt_info, original_pkt, print_details=False)
                complete_step("Install Entries")

                update_step("Start Sniffer")
                interfaces = get_interfaces('tf1_model')
                initial_ingress_port = case_stg['pkt_values']['ig_intr_md.ingress_port']
                ingress_veth = f"veth{initial_ingress_port * 2}"
                if case_stg['Output'].lower() != "ingress port":
                    interfaces.remove(ingress_veth)
                sniff_threads, capture_results, packet_storage = start_multi_sniffer_in_background(
                    interfaces, timeout=7, print_layers=False)
                time.sleep(0.65)
                complete_step("Start Sniffer")

                update_step("Send Packet")
                parse_pkts(original_pkt, print_layers=False)
                sendp(original_pkt, iface=ingress_veth, verbose=False)
                time.sleep(0.35)
                complete_step("Send Packet")

                update_step("Capture Results")
                for thread in sniff_threads:
                    thread.join()
                complete_step("Capture Results")

                update_step("Validate Results")
                # Mock validation results (replace with actual logic)
                pkt_result = "Passed"  # Replace with actual packet comparison outcome
                counter_result = "Passed"  # Replace with actual counter check result
                final_result = "Passed" if pkt_result == "Passed" and counter_result == "Passed" else "Failed"

                # Call validate_results (assumes it raises exception on failure)
                validate_results(
                    counters_df.iloc[idx], packet_storage, dev_tgt, bfrt_info,
                    case_stg, idx, [], printing=False
                )
                complete_step("Validate Results")

                test_results.append((case_id, pkt_result, counter_result, final_result))

            except Exception as e:
                step_status[current_step] = f"[red]Failed: {str(e)}"
                layout.renderables[0] = create_status_table(step_status, case_id)
                test_results.append((case_id, "Failed", "Failed", "Failed"))

        console.print(f"\n[bold green]✅ Test Case {case_id} completed!\n")
        time.sleep(1.0)

    console.clear()
    console.print(create_summary_table(test_results))

    interface.tear_down_stream()

if __name__ == "__main__":
    main()
