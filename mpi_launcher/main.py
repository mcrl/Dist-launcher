# Description: distribute launcher using mpi4py
# Usage: python main.py --host host1,host2 --np 4 --task example_task.py

import sys
import subprocess
import argparse
import socket
import importlib.util
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='', help='Host list (comma-separated)')
    parser.add_argument('--np', type=int, default=1, help='Total number of processes')
    parser.add_argument('--task', type=str, required=True, help='Path to task python code (e.g, example_task.py)')
    parser.add_argument('--launcher', action='store_true', help='Launcher flag')
    args = parser.parse_args()

    if args.launcher:
        # Worker process code
        from mpi4py import MPI

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
        hostname = socket.gethostname()
        print(f"[Node: {hostname}] Process {rank}/{size} is running.")

        # Load task module (file)
        task_module_path = args.task
        task_module_name = os.path.splitext(os.path.basename(task_module_path))[0]

        spec = importlib.util.spec_from_file_location(task_module_name, task_module_path)
        task_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_module)

        # Execute task funcion (e.g., task_module.run_task)
        if hasattr(task_module, 'run_task'):
            task_module.run_task(comm, rank, size)
        else:
            print(f"'{task_module_path}' not found 'run_task' function.")

    else:
        # Main (Master) process code
        if args.host == '':
            print("Need to specify the host list as an argument.")
            sys.exit(1)
        hosts = args.host.split(',')

        if len(hosts) > args.np:
            print("Number of hosts is greater than the total number of processes.")
            sys.exit(1)

        # mpirun command generation
        cmd = [
            'mpirun',
            '-np', str(args.np),
            '--host', ','.join(hosts),
            '--map-by', 'node',
            sys.executable, sys.argv[0],
            '--task', args.task,
            '--launcher'
        ]

        # Execute process
        subprocess.run(cmd)

if __name__ == "__main__":
    main()