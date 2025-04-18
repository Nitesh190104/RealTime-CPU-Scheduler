import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from queue import PriorityQueue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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
    first_arrival = min(p['arrival'] for p in processes)
    total_time = max_completion_time - first_arrival
    total_execution_time = sum(end - start for _, start, end in schedule)
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
    
    # Create and display Gantt chart
    display_gantt_chart(schedule, process_dict)


def display_gantt_chart(schedule, process_dict):
    # Create a new frame for the Gantt chart
    gantt_frame = ttk.Frame(frame_metrics)
    gantt_frame.pack(pady=10, fill="both", expand=True)
    
    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 3))
    fig.subplots_adjust(bottom=0.2)
    
    # Get unique process IDs and assign colors
    unique_pids = list(set(pid for pid, _, _ in schedule))
    colors = plt.cm.tab20.colors  # Using a colormap for distinct colors
    
    # Plot each process segment
    for i, (pid, start, end) in enumerate(schedule):
        color = colors[unique_pids.index(pid) % len(colors)]
        ax.broken_barh([(start, end - start)], (5, 10), facecolors=color)
        # Add label in the middle of the bar
        ax.text((start + end) / 2, 10, f"P{pid}", ha='center', va='center', color='white')
    
    # Configure the chart
    ax.set_yticks([10])
    ax.set_yticklabels(['Processes'])
    ax.set_xlabel('Time')
    ax.set_title('Gantt Chart - Process Scheduling')
    
    # Calculate appropriate x-axis limits
    max_time = max(end for _, _, end in schedule)
    ax.set_xlim(0, max_time + 1)
    
    # Add grid lines for better readability
    ax.grid(True, axis='x')
    
    # Create a legend showing process colors
    legend_elements = []
    for pid in sorted(unique_pids):
        color = colors[unique_pids.index(pid) % len(colors)]
        legend_elements.append(plt.Rectangle((0, 0), 1, 1, fc=color, label=f"P{pid}"))
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, -0.1), ncol=min(10, len(unique_pids)))
    
    # Embed the matplotlib figure in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=gantt_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


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


# GUI Setup with ttkbootstrap
root = tk.Tk()
root.title("CPU Scheduler")
style = Style(theme="morph")

# Set initial window size
root.geometry("900x700")

# Create a main frame with scrollbars
main_container = ttk.Frame(root)
main_container.pack(fill="both", expand=True)

# Add a Canvas that will contain the scrollable content
canvas = tk.Canvas(main_container)
scrollbar_y = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
scrollbar_x = ttk.Scrollbar(main_container, orient="horizontal", command=canvas.xview)

# Configure the canvas
canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Place the scrollbars
scrollbar_y.pack(side="right", fill="y")
scrollbar_x.pack(side="bottom", fill="x")
canvas.pack(side="left", fill="both", expand=True)

# Create a frame inside the canvas that will contain all your UI elements
content_frame = ttk.Frame(canvas)
canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

# Adjust canvas window size when frame size changes
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    # Make the canvas window the width of the canvas
    canvas.itemconfig(canvas_window, width=canvas.winfo_width())

content_frame.bind("<Configure>", on_frame_configure)

# Add mousewheel scrolling
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Add a title label to explain the additions
ttk.Label(content_frame, text="CPU Scheduler",
          font=("Arial", 16)).pack(side="top", pady=(10, 0))

# Place all UI components inside content_frame instead of root
# IMPROVED INPUT UI
frame_input = ttk.LabelFrame(content_frame, text="Process Information")
frame_input.pack(pady=10, padx=10, fill="x")

# Create grid layout with better spacing
input_grid = ttk.Frame(frame_input)
input_grid.pack(pady=10, padx=10)

# Labels
ttk.Label(input_grid, text="PID:").grid(row=0, column=0, padx=(5, 2), sticky="e")
ttk.Label(input_grid, text="Arrival Time:").grid(row=0, column=2, padx=(10, 2), sticky="e")
ttk.Label(input_grid, text="Burst Time:").grid(row=1, column=0, padx=(5, 2), pady=5, sticky="e")
ttk.Label(input_grid, text="Priority:").grid(row=1, column=2, padx=(10, 2), pady=5, sticky="e")

# Entry fields
entry_pid = ttk.Entry(input_grid, width=8)
entry_arrival = ttk.Entry(input_grid, width=8)
entry_burst = ttk.Entry(input_grid, width=8)
entry_priority = ttk.Entry(input_grid, width=8)

entry_pid.grid(row=0, column=1, padx=(0, 10), sticky="w")
entry_arrival.grid(row=0, column=3, padx=(0, 5), sticky="w")
entry_burst.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="w")
entry_priority.grid(row=1, column=3, padx=(0, 5), pady=5, sticky="w")

# Button frame
button_frame = ttk.Frame(frame_input)
button_frame.pack(pady=(0, 10), fill="x")

# Center the buttons
buttons_container = ttk.Frame(button_frame)
buttons_container.pack(anchor="center")

ttk.Button(buttons_container, text="Add Process", command=add_process, bootstyle=SUCCESS, width=12).grid(row=0, column=0, padx=5)
ttk.Button(buttons_container, text="Delete", command=delete_process, bootstyle=DANGER, width=10).grid(row=0, column=1, padx=5)
ttk.Button(buttons_container, text="Reset", command=reset_table, bootstyle=WARNING, width=10).grid(row=0, column=2, padx=5)

frame_table = ttk.Frame(content_frame)
frame_table.pack()

columns = ("PID", "Arrival", "Burst", "Priority")
table = ttk.Treeview(frame_table, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=80)
table.pack()

frame_controls = ttk.Frame(content_frame)
frame_controls.pack(pady=10)

# Updated algorithm selection - removed SRTF
algo_var = tk.StringVar(value="FCFS")
algo_var.trace("w", update_time_quantum_visibility)
algo_menu = ttk.Combobox(frame_controls, textvariable=algo_var,
                         values=["FCFS", "SJF", "Round Robin", "Priority"],
                         state="readonly")
algo_menu.pack(side="left", padx=5)

label_quantum = ttk.Label(frame_controls, text="Time Quantum:")
time_quantum = ttk.Entry(frame_controls, width=5)
ttk.Button(frame_controls, text="Run Scheduler", command=calculate_scheduling, bootstyle=PRIMARY).pack(side="left",
                                                                                                       padx=5)

# Remove the chart frame
frame_metrics = ttk.Frame(content_frame)
frame_metrics.pack(pady=10, padx=10, fill="both", expand=True)

# Initialize UI based on current algorithm
update_time_quantum_visibility()

root.mainloop()
