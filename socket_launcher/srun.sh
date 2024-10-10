#!/bin/bash

salloc -w b0 --exclusive --partition=PB \
    srun \
        python example_task.py