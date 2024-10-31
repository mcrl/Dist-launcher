# Distributed Launcher

Distributed launcher using Python socket module.

## Setup

```bash
conda create -n <env_name> python=<python_version>
conda activate <env_name>
```
- Tested with Python `3.11` but may work with other versions too.

## Run

### Single node

To launch on a single node:

```bash
python main.py --task example_task.py --nproc_per_node=4
```

### Multi-nodes

To launch on multi-nodes:

```bash
# On the master node (e.g., v00)
python main.py --task example_task.py --nnodes=2 --nproc_per_node=2 --node-rank=0 --master_addr=<master_IP>

# On the worker node (e.g., v01)
python main.py --task example_task.py --nnodes=2 --nproc_per_node=2 --node-rank=1 --master_addr=<master_IP>
```
Also available to use scripts as follows:
```bash
# On the master node (e.g., v00)
bash distributed_run.sh 0  # NODE_RANK: 0

# On the worker node (e.g., v01)
bash distributed_run.sh 1  # NODE_RANK: 1
```

## Distributed Launcher using MPI

To launch on multi-nodes using MPI:

```bash
bash distributed_mpirun.sh
```