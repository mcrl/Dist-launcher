# Example code for distributed task execution

def run_task(comm=None, rank=0, size=1):
    import socket
    hostname = socket.gethostname()
    print(f"[Node: {hostname}] Executing the task on Process {rank}/{size}.")

    # Task: Allreduce (SUM) operation
    # Distributed task execution
    if comm is not None:
        from mpi4py import MPI
        total_rank = comm.allreduce(rank, op=MPI.SUM)
        print(f"Process {rank} Allreduce (SUM) Output: {total_rank}")
    # Non-distributed task execution
    else:
        total_rank = sum(range(size))
        print(f"Process {rank} Allreduce (SUM) Output: {total_rank}")

if __name__ == "__main__":
    run_task()