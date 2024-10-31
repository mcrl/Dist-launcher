#!/bin/bash

# Set master address and port
MASTER_ADDR=v00       # Choose a master address
MASTER_PORT=12345     # Choose an available port number

NNODES=2              # Number of nodes
NPERNODES=2           # Number of processes per node
NODE_RANK=$1          # Rank of the current node

python -u main.py \
    --task example_task.py \
    --nproc_per_node=$NPERNODES \
    --master_addr=$MASTER_ADDR \
    --master_port=$MASTER_PORT \
    --nnodes=$NNODES \
    --node_rank=$NODE_RANK