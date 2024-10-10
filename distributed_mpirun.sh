#!/bin/bash

# Set master address and port
MASTER_ADDR=v00       # Choose a master address
MASTER_PORT=12345     # Choose an available port number

NNODES=2              # Number of nodes
NPERNODES=2           # Number of processes per node

TOTAL_PROCESSES=$((NNODES * NPERNODES))

echo "> MASTER_ADDR: $MASTER_ADDR, MASTER_PORT: $MASTER_PORT, NNODES: $NNODES, NPERNODES: $NPERNODES, TOTAL_PROCESSES: $TOTAL_PROCESSES"

mpirun -mca btl ^openib -mca pml ucx -H v00,v01 -np $TOTAL_PROCESSES \
    --oversubscribe \
    -x MASTER_ADDR=$MASTER_ADDR \
    -x MASTER_PORT=$MASTER_PORT \
    -x NNODES=$NNODES \
    -x NPERNODES=$NPERNODES \
    -x PATH=$PATH \
    -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH \
    bash run_with_mpi.sh
