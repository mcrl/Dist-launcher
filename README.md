# Distributed Launcher

Distributed launcher using Python socket module.

## Setup

```bash
conda create -n <env_name> python=<python_version>
conda activate <env_name>
```
- Tested with Python `3.11` but may work with other versions too.

## Run

### Distributed Launcher  

```bash
# On the master node (e.g., v00)
bash distributed_run.sh 0  # NODE_RANK: 0

# On the worker node (e.g., v01)
bash distributed_run.sh 1  # NODE_RANK: 1
```

### Distributed Launcher using MPI

```bash
bash distributed_mpirun.sh
```