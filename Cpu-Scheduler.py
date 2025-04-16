import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from queue import PriorityQueue


def calculate_scheduling():
    algorithm = algo_var.get()
    try:
        processes = []
        for row in table.get_children():
            values = table.item(row)['values']
            processes.append(
                {'pid': int(values[0]), 'arrival': int(values[1]), 'burst': int(values[2]), 'priority': int(values[3])})

        if algorithm == "FCFS":
            result = fcfs(processes)
        elif algorithm == "SJF":
            result = sjf(processes)
        elif algorithm == "Round Robin":
            quantum = int(time_quantum.get()) if time_quantum.get() else 2
            result = round_robin(processes, quantum)
        elif algorithm == "Priority":
            result = priority_scheduling(processes)
        else:
            return

        calculate_and_display_metrics(result, processes)
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")


def fcfs(processes):
    processes.sort(key=lambda x: x['arrival'])
    start_time, result = 0, []
    for process in processes:
        start_time = max(start_time, process['arrival'])
        result.append((process['pid'], start_time, start_time + process['burst']))
        start_time += process['burst']
    return result


def sjf(processes):
    if not processes:
        return []

    # Create a copy of processes to avoid modifying the original data
    processes = [p.copy() for p in processes]

    # Sort by arrival time
    processes.sort(key=lambda x: x['arrival'])

    result = []
    time = processes[0]['arrival']
    pq = PriorityQueue()  # queue for ready processes
    next_process_idx = 0
    
    while next_process_idx < len(processes) or not pq.empty():
        # Add all arrived processes to the priority queue
        while next_process_idx < len(processes) and processes[next_process_idx]['arrival'] <= time:
            # Arrival time used as a tie-breaker => burst time same
            p = processes[next_process_idx]
            pq.put((p['burst'], p['arrival'], p['pid']))
            next_process_idx += 1

        if pq.empty():
            # If no process is ready, jump to the next arrival
            if next_process_idx < len(processes):
                time = processes[next_process_idx]['arrival']
                continue
            else:
                break

        # Get the process with the shortest burst time
        burst, arrival, pid = pq.get()

        # Add to result
        result.append((pid, time, time + burst))

        # Update time
        time += burst

    return result

def round_robin(processes, quantum):
    if not processes:
        return []

    # a copy of processes to avoid modifying the original data
    processes = [p.copy() for p in processes]

    # Sort processes by arrival time
    processes.sort(key=lambda x: x['arrival'])

    # Initialize variables
    result = []
    ready_queue = []  # Processes that have arrived and are waiting for CPU
    time = processes[0]['arrival']  # Start time is the earliest arrival
    remaining_burst = {p['pid']: p['burst'] for p in processes}
    remaining_processes = len(processes)
    next_arrival_idx = 0

    while remaining_processes > 0:
        # Add newly arrived processes to the ready queue
        while next_arrival_idx < len(processes) and processes[next_arrival_idx]['arrival'] <= time:
            ready_queue.append(processes[next_arrival_idx])
            next_arrival_idx += 1

        if not ready_queue:
            # If no process is in the ready queue, jump to the next arrival time
            if next_arrival_idx < len(processes):
                time = processes[next_arrival_idx]['arrival']
                continue
            else:
                break  # No more processes to execute

        # Get the next process from the ready queue
        current_process = ready_queue.pop(0)
        pid = current_process['pid']

        # Calculate actual execution time (either quantum or remaining burst time)
        exec_time = min(quantum, remaining_burst[pid])

        # Add to result
        result.append((pid, time, time + exec_time))

        # Update time and remaining burst
        time += exec_time
        remaining_burst[pid] -= exec_time

        # Check if process is completed
        if remaining_burst[pid] == 0:
            remaining_processes -= 1
        else:
            # Process still has work to do, check if any new processes have arrived
            # before adding it back to the ready queue
            arrived_during_execution = []
            while next_arrival_idx < len(processes) and processes[next_arrival_idx]['arrival'] <= time:
                arrived_during_execution.append(processes[next_arrival_idx])
                next_arrival_idx += 1

            # Add the preempted process back to the ready queue after newly arrived processes
            ready_queue.extend(arrived_during_execution)
            ready_queue.append(current_process)

    return result if result else [(0, 0, 0)]  # Ensure non-empty result to avoid errors


def priority_scheduling(processes):
    if not processes:
        return []

    # Create a copy of processes to avoid modifying the original data
    processes = [p.copy() for p in processes]

    # Sort by arrival time initially
    processes.sort(key=lambda x: x['arrival'])

    result = []
    time = processes[0]['arrival']
    remaining = len(processes)
    completed = set()

    while remaining > 0:
        # Find available processes that have arrived
        available = [p for p in processes if p['arrival'] <= time and p['pid'] not in completed]

        if not available:
            # Jump to next process arrival
            next_arrival = min([p['arrival'] for p in processes if p['pid'] not in completed])
            time = next_arrival
            continue

        # Find process with highest priority (lowest priority number)
        selected = min(available, key=lambda x: x['priority'])

        # Schedule the process
        result.append((selected['pid'], time, time + selected['burst']))

        # Update time and mark process as completed
        time += selected['burst']
        completed.add(selected['pid'])
        remaining -= 1

    return result

def calculate_and_display_metrics(schedule, processes):
    if not schedule:
        return

    # Create a dictionary for processes for easy lookup
    process_dict = {p['pid']: p for p in processes}

    # Get the end time of the last process to complete
    max_completion_time = max(task[2] for task in schedule)

    # Dictionary to track completion time for each process
    completion_times = {}

    # Dictionary to calculate total running time for each process
    running_times = {}

    # For each process, find its segments in the schedule
    for pid, start, end in schedule:
        if pid not in running_times:
            running_times[pid] = 0
        running_times[pid] += (end - start)

        # Update completion time (we want the max time when the process finishes)
        completion_times[pid] = max(completion_times.get(pid, 0), end)

    # Calculate waiting and turnaround times for each process
    waiting_times = {}
    turnaround_times = {}

    for pid in completion_times:
        # Turnaround time = completion time - arrival time
        turnaround_times[pid] = completion_times[pid] - process_dict[pid]['arrival']

        # Waiting time = turnaround time - burst time
        waiting_times[pid] = turnaround_times[pid] - process_dict[pid]['burst']

    # Calculate averages
    avg_waiting_time = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0
    avg_turnaround_time = sum(turnaround_times.values()) / len(turnaround_times) if turnaround_times else 0

    # Calculate CPU utilization
    # Get the first arrival time
    first_arrival = min(p['arrival'] for p in processes)

    # Total time from first arrival to completion
    total_time = max_completion_time - first_arrival

    # Sum of all process execution times
    total_execution_time = sum(end - start for _, start, end in schedule)

    # CPU utilization as a percentage
    cpu_utilization = (total_execution_time / total_time) * 100 if total_time > 0 else 0

    # Calculate throughput (processes per unit time)
    number_of_processes = len(set(pid for pid, _, _ in schedule))
    throughput = number_of_processes / total_time if total_time > 0 else 0

    # Display the metrics
    for widget in frame_metrics.winfo_children():
        widget.destroy()

    metrics_text = f"""
    Performance Metrics:
    - Average Waiting Time: {avg_waiting_time:.2f} time units
    - Average Turnaround Time: {avg_turnaround_time:.2f} time units
    - CPU Utilization: {cpu_utilization:.2f}%
    - Throughput: {throughput:.4f} processes/time unit
    """

    # Create a table for individual process metrics
    ttk.Label(frame_metrics, text=metrics_text, justify="left").pack(anchor="w", padx=10)

    # Create a table for detailed per-process metrics
    process_metrics_frame = ttk.Frame(frame_metrics)
    process_metrics_frame.pack(pady=5, fill="x", expand=True)

    columns = ("Process ID", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time", "Waiting Time")
    process_metrics_table = ttk.Treeview(process_metrics_frame, columns=columns, show="headings")

    for col in columns:
        process_metrics_table.heading(col, text=col)
        process_metrics_table.column(col, width=120)

    for pid in sorted(completion_times.keys()):
        process_metrics_table.insert("", "end", values=(
            pid,
            process_dict[pid]['arrival'],
            process_dict[pid]['burst'],
            completion_times[pid],
            turnaround_times[pid],
            waiting_times[pid]
        ))

    process_metrics_table.pack(fill="both", expand=True)


def add_process():
    try:
        pid = int(entry_pid.get())
        arrival = int(entry_arrival.get())
        burst = int(entry_burst.get())
        priority = int(entry_priority.get())
        table.insert("", "end", values=(pid, arrival, burst, priority))
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter valid numbers.")


def delete_process():
    selected_item = table.selection()
    if selected_item:
        table.delete(selected_item)


def reset_table():
    for row in table.get_children():
        table.delete(row)


def update_time_quantum_visibility(*args):
    if algo_var.get() == "Round Robin":
        label_quantum.pack(side="left", padx=5)
        time_quantum.pack(side="left", padx=5)
    else:
        label_quantum.pack_forget()
        time_quantum.pack_forget()






