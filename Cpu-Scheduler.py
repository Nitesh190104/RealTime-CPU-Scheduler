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


