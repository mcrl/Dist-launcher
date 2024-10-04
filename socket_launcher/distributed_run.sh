#!/bin/bash

salloc -w b0,b1 --exclusive --partition=PB \
    srun -n 4 \
        python main.py \
            --task example_task.py