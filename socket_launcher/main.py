# main.py

import sys
import argparse
import os
import socket
import threading
import time
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--master_addr', type=str, required=True, help='Address to bind the master server')
    parser.add_argument('--master_port', type=int, required=True, help='Port to bind the master server')
    parser.add_argument('--nnodes', type=int, required=True, help='Number of nodes')
    parser.add_argument('--nproc_per_node', type=int, required=True, help='Number of processes per node')
    parser.add_argument('--task', type=str, required=True, help='Path to the task script (e.g., example_task.py)')
    args, unknown = parser.parse_known_args()

    hostname = socket.gethostname()
    master_addr = args.master_addr
    master_port = args.master_port
    nnodes = args.nnodes
    nproc_per_node = args.nproc_per_node

    # Calculate the expected world size
    expected_world_size = nnodes * nproc_per_node

    # Try to become the master
    try:
        # Attempt to bind to the master address and port
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((master_addr, master_port))
        server_socket.listen()
        is_master = True
        print(f"[{hostname}] Became master at {master_addr}:{master_port}")
    except OSError:
        # If binding fails, this process is a worker
        is_master = False
        print(f"[{hostname}] Acting as worker, connecting to master at {master_addr}:{master_port}")

    # Shared data
    rank = None
    world_size = expected_world_size

    if is_master:
        # Master process
        client_sockets = []
        ranks_assigned = {}
        rank_counter = 1  # Start assigning ranks from 1 (master is rank 0)

        # Master assigns rank 0 to itself
        rank = 0

        print(f"[Master {hostname}] Waiting for worker connections...")

        # Accept connections until all workers have connected
        while len(client_sockets) < expected_world_size - 1:
            conn, addr = server_socket.accept()
            data = conn.recv(1024)
            worker_hostname = data.decode()

            # Assign a rank to the worker
            worker_rank = rank_counter
            rank_counter += 1
            client_sockets.append((conn, worker_rank))
            print(f"[Master] Assigned rank {worker_rank} to worker {worker_hostname}")

        print(f"[Master] Total world size: {world_size}")

        # Send assigned ranks and world_size to each worker
        for conn, worker_rank in client_sockets:
            conn.sendall(f"{worker_rank},{world_size}".encode())
            conn.close()

        server_socket.close()
        print(f"[Master] All workers have been assigned ranks.")

    else:
        # Worker process
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        while not connected:
            try:
                s.connect((master_addr, master_port))
                connected = True
            except ConnectionRefusedError:
                time.sleep(1)  # Wait before retrying
                continue

        # Send hostname to master
        s.sendall(hostname.encode())

        # Receive assigned rank and world_size from master
        data = s.recv(1024).decode()
        rank_str, world_size_str = data.split(',')
        rank = int(rank_str)
        world_size = int(world_size_str)
        s.close()

        print(f"[Worker {hostname}] Received rank {rank}, world size {world_size} from master")

    # Set environment variables for the task script
    os.environ['RANK'] = str(rank)
    os.environ['WORLD_SIZE'] = str(world_size)

    # Execute the task script
    # Pass along any additional arguments received
    task_command = [sys.executable, args.task] + unknown
    print(f"[Rank {rank}] Executing task: {' '.join(task_command)}")

    # Flush the output buffers before execv
    sys.stdout.flush()
    sys.stderr.flush()

    # Replace the current process with the task script
    os.execv(sys.executable, task_command)

if __name__ == '__main__':
    main()
