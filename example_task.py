# example_task.py

import os
import socket
import time

def main():
    rank = int(os.environ.get('RANK', '0'))
    world_size = int(os.environ.get('WORLD_SIZE', '1'))
    hostname = socket.gethostname()

    print(f"[Node: {hostname}] Process {rank}/{world_size} is starting.")

    # EX) Each process performs its task
    print(f"Process {rank} is performing its task.")
    
    time.sleep(2)  # Simulate task execution time

    print(f"Process {rank} has completed its task.")

if __name__ == "__main__":
    main()