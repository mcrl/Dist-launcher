#!/bin/bash

# Set master address and port
MASTER_ADDR=v00       # Bind to all interfaces
MASTER_PORT=12345     # Choose an available port number

NNODES=2              # Number of nodes
NPERNODES=2           # Number of processes per node
NODE_RANK=$1          # Rank of the current node

for (( LOCAL_RANK=0; LOCAL_RANK<$NPERNODES; LOCAL_RANK++ ))
do
    python -u main.py \
        --task example_task.py \
        --master_addr=$MASTER_ADDR \
        --master_port=$MASTER_PORT \
        --nnodes=$NNODES \
        --nproc_per_node=$NPERNODES \
        --node_rank=$NODE_RANK \
        --local_rank=$LOCAL_RANK &
done

wait