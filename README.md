# CPU Scheduler Simulator

A Python-based CPU scheduling simulator with a graphical user interface that allows users to visualize and compare different CPU scheduling algorithms.

## Features

### Scheduling Algorithms
- **First Come First Serve (FCFS)**
- **Shortest Job First (SJF)**
- **Round Robin (RR)**
- **Priority Scheduling**

### Process Management
- Add processes with:
  - Process ID (PID)
  - Arrival Time
  - Burst Time
  - Priority Level
- Delete processes
- Reset process table

### Performance Metrics
- Average Waiting Time
- Average Turnaround Time
- CPU Utilization
- Throughput
- Per-process metrics:
  - Completion Time
  - Turnaround Time
  - Waiting Time

## Requirements

- Python 3.x
- tkinter
- ttkbootstrap

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
```

2. Install the required packages:
```bash
pip install ttkbootstrap
```

## Usage

1. Run the application:
```bash
python osproject.py
```

2. Add processes using the input fields:
   - Enter Process ID
   - Set Arrival Time
   - Set Burst Time
   - Set Priority Level
   - Click "Add Process"

3. Select a scheduling algorithm:
   - FCFS
   - SJF
   - Round Robin (with time quantum)
   - Priority

4. Click "Calculate" to see the scheduling results and performance metrics

## Features in Detail

### First Come First Serve (FCFS)
- Processes are executed in the order they arrive
- Simple and easy to implement
- May lead to convoy effect

### Shortest Job First (SJF)
- Executes the process with the shortest burst time first
- Optimal for minimizing average waiting time
- May lead to starvation of longer processes

### Round Robin
- Each process gets a fixed time slice (quantum)
- Processes are executed in a circular order
- Prevents starvation
- Adjustable time quantum

### Priority Scheduling
- Processes are executed based on priority
- Lower priority number indicates higher priority
- May lead to starvation of lower priority processes

## Performance Metrics Explanation

- **Waiting Time**: Time a process waits in the ready queue
- **Turnaround Time**: Total time from arrival to completion
- **CPU Utilization**: Percentage of time CPU is busy
- **Throughput**: Number of processes completed per time unit

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and tkinter
- UI styling with ttkbootstrap
- Created for educational purposes in Operating Systems 
