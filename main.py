# main.py

import sys
import argparse
import os
import socket
import threading
import time
import subprocess

def wait_for_worker_completion(conn, worker_rank, completion_event):
    # Wait for "DONE" message from worker
    data = conn.recv(1024)
    if data.decode() == "DONE":
        print(f"[Master] Worker {worker_rank} has completed its task.")
        completion_event.set()
    conn.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--master_addr', type=str, required=True, help='Address of the master node (hostname or IP)')
    parser.add_argument('--master_port', type=int, required=True, help='Port for the master server to bind')
    parser.add_argument('--nnodes', type=int, required=True, help='Number of nodes')
    parser.add_argument('--nproc_per_node', type=int, required=True, help='Number of processes per node')
    parser.add_argument('--node_rank', type=int, required=True, help='Rank of the node (0 to nnodes-1)')
    parser.add_argument('--local_rank', type=int, required=True, help='Rank of the process on the node (0 to nproc_per_node-1)')
    parser.add_argument('--task', type=str, required=True, help='Path to the task script (e.g., example_task.py)')
    args, unknown = parser.parse_known_args()

    hostname = socket.gethostname()
    master_addr = args.master_addr
    master_port = args.master_port
    nnodes = args.nnodes
    nproc_per_node = args.nproc_per_node
    node_rank = args.node_rank
    local_rank = args.local_rank

    # Calculate the global rank and world size
    rank = node_rank * nproc_per_node + local_rank
    world_size = nnodes * nproc_per_node

    # Determine if this process is the master
    is_master = (node_rank == 0 and local_rank == 0)

    if is_master:
        # Master process
        try:
            # Bind to all interfaces on the specified port
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('', master_port))
            server_socket.listen()
            print(f"[{hostname}] Became master at {hostname}:{master_port}")
        except OSError as e:
            print(f"[{hostname}] Failed to bind as master: {e}")
            sys.exit(1)

        connections = []
        completion_events = []

        print(f"[Master {hostname}] Waiting for worker connections...")

        # Accept connections from all workers
        expected_workers = world_size - 1  # Exclude master itself
        while len(connections) < expected_workers:
            try:
                conn, addr = server_socket.accept()
                data = conn.recv(1024)
                worker_rank = int(data.decode())
                print(f"[Master] Connected to worker {worker_rank}")
                connections.append((conn, worker_rank))
            except Exception as e:
                print(f"[Master] Error accepting connections: {e}")

        print(f"[Master] All workers are connected. Sending START signal to all workers.")

        # Send START signal to all workers
        for conn, worker_rank in connections:
            conn.sendall("START".encode())

        # Prepare to receive completion signals from workers
        for conn, worker_rank in connections:
            completion_event = threading.Event()
            t = threading.Thread(target=wait_for_worker_completion, args=(conn, worker_rank, completion_event))
            t.start()
            completion_events.append(completion_event)

        # Execute the task script
        os.environ['RANK'] = str(rank)
        os.environ['WORLD_SIZE'] = str(world_size)
        task_command = [sys.executable, args.task] + unknown
        print(f"[Rank {rank}] Executing task: {' '.join(task_command)}")
        sys.stdout.flush()
        sys.stderr.flush()
        result = subprocess.run(task_command, env=os.environ)

        # Wait for all workers to complete
        for event in completion_events:
            event.wait()

        print(f"[Master] All workers have completed their tasks.")
        server_socket.close()
        sys.exit(result.returncode)

    else:
        # Worker process
        connected = False
        while not connected:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((master_addr, master_port))
                connected = True
            except Exception:
                time.sleep(1)  # Wait before retrying
                continue

        # Send rank to master
        s.sendall(str(rank).encode())
        print(f"[Worker {hostname}] Connected to master at {master_addr}:{master_port}")

        # Wait for START signal from master
        data = s.recv(1024)
        if data.decode() == "START":
            print(f"[Worker {hostname}] Received START signal from master.")

        # Set environment variables for the task script
        os.environ['RANK'] = str(rank)
        os.environ['WORLD_SIZE'] = str(world_size)

        # Execute the task script
        task_command = [sys.executable, args.task] + unknown
        print(f"[Rank {rank}] Executing task: {' '.join(task_command)}")
        sys.stdout.flush()
        sys.stderr.flush()
        result = subprocess.run(task_command, env=os.environ)

        # After task completion, send completion signal to master
        s.sendall("DONE".encode())
        s.close()

        sys.exit(result.returncode)

if __name__ == '__main__':
    main()
