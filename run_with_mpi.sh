#!/bin/bash

# Get MPI environment variables
GLOBAL_RANK=${OMPI_COMM_WORLD_RANK}
GLOBAL_SIZE=${OMPI_COMM_WORLD_SIZE}

if [ -z "$GLOBAL_RANK" ]; then
    echo "Error: Unable to determine GLOBAL_RANK from MPI environment variables."
    exit 1
fi

if [ -z "$GLOBAL_SIZE" ]; then
    echo "Error: Unable to determine GLOBAL_SIZE from MPI environment variables."
    exit 1
fi

# Get NNODES and NPERNODES from environment variables
if [ -z "$NNODES" ] || [ -z "$NPERNODES" ]; then
    echo "Error: NNODES and NPERNODES must be set as environment variables."
    exit 1
fi

# Set NODE_RANK and LOCAL_RANK
NODE_RANK=$(( GLOBAL_RANK / NPERNODES ))
LOCAL_RANK=$(( GLOBAL_RANK % NPERNODES ))

echo ">> NODE: $(hostname), GLOBAL_RANK: $GLOBAL_RANK, GLOBAL_SIZE: $GLOBAL_SIZE, NODE_RANK: $NODE_RANK, LOCAL_RANK: $LOCAL_RANK"

python -u main.py \
    --task example_task.py \
    --master_addr=$MASTER_ADDR \
    --master_port=$MASTER_PORT \
    --nnodes=$NNODES \
    --nproc_per_node=$NPERNODES \
    --node_rank=$NODE_RANK \
    --local_rank=$LOCAL_RANK "$@"
