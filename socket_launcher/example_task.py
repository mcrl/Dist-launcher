# example_task.py

def run_task(rank=0, size=1, total_sum=None):
    import socket
    hostname = socket.gethostname()
    print(f"[Node: {hostname}] Executing task on Process {rank}/{size}.")

    # Print the Allreduce result
    if total_sum is not None:
        print(f"Process {rank} Allreduce (SUM) Output: {total_sum}")
    else:
        print(f"Process {rank} did not receive the Allreduce result.")

if __name__ == "__main__":
    run_task()