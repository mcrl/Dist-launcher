# main.py

import sys
import argparse
import os
import socket
import subprocess
import importlib.util

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, required=True, help='Path to the task Python code (e.g., example_task.py)')
    args = parser.parse_args()

    # Retrieve rank and size from Slurm environment variables
    rank = int(os.environ.get('SLURM_PROCID', '0'))
    size = int(os.environ.get('SLURM_NTASKS', '1'))
    hostname = socket.gethostname()
    port = 5000  # Port number for communication
    job_id = int(os.environ.get('SLURM_JOB_ID', '0'))
    port = 5000 + job_id % 10000  # Prevent port conflicts

    # Function to get the list of hostnames
    def get_hostnames():
        nodelist = os.environ['SLURM_NODELIST']
        output = subprocess.check_output(['scontrol', 'show', 'hostnames', nodelist])
        hostnames = output.decode().split()
        return hostnames

    # Implementing Allreduce operation
    if rank == 0:
        # Server process
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', port))
        server_socket.listen(size - 1)
        sum_of_ranks = rank  # Start with own rank

        connections = []

        print(f"[Rank {rank}] Server listening on {hostname}:{port}")

        for _ in range(size - 1):
            conn, addr = server_socket.accept()
            data = conn.recv(1024)
            other_rank = int(data.decode())
            sum_of_ranks += other_rank
            connections.append(conn)
            print(f"[Rank {rank}] Received rank {other_rank} from {addr}")

        # Send the total sum to all clients
        total_sum_str = str(sum_of_ranks)
        for conn in connections:
            conn.sendall(total_sum_str.encode())
            conn.close()

        server_socket.close()
        print(f"[Rank {rank}] Allreduce result: {sum_of_ranks}")

    else:
        # Client process
        # Get the hostname of rank 0
        hostnames = get_hostnames()
        master_hostname = hostnames[0]

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((master_hostname, port))
            s.sendall(str(rank).encode())
            print(f"[Rank {rank}] Sent rank {rank} to the server")
            data = s.recv(1024)
            total_sum = int(data.decode())
            s.close()
            print(f"[Rank {rank}] Received Allreduce result: {total_sum}")
        except Exception as e:
            print(f"[Rank {rank}] Cannot connect to the server: {e}")
            s.close()
            total_sum = None  # Handle error

    # Load and execute the task module
    task_module_path = args.task
    task_module_name = os.path.splitext(os.path.basename(task_module_path))[0]

    spec = importlib.util.spec_from_file_location(task_module_name, task_module_path)
    task_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(task_module)

    # Execute the task function
    if hasattr(task_module, 'run_task'):
        task_module.run_task(rank=rank, size=size, total_sum=sum_of_ranks if rank == 0 else total_sum)
    else:
        print(f"'{task_module_path}' does not define a 'run_task' function.")

if __name__ == '__main__':
    main()