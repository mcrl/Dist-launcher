#!/bin/bash

# Set master address and port
MASTER_ADDR=b0        # Bind to all interfaces
MASTER_PORT=12350     # Choose an available port number

NNODES=2              # Number of nodes
NPERNODES=2           # Number of processes per node

salloc -w b0,b1 --exclusive --partition=PB \
    srun --nodes=$NNODES --ntasks-per-node=$NPERNODES \
        python -u main.py \
            --task example_task.py \
            --master_addr=$MASTER_ADDR \
            --master_port=$MASTER_PORT \
            --nnodes=$NNODES \
            --nproc_per_node=$NPERNODES
