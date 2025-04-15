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





