#!/bin/bash

salloc -w b0 --exclusive --partition=PB \
    srun \
        python main.py \
            --task example_task.py