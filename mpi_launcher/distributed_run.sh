#!/bin/bash

salloc -w b0,b1 --exclusive --partition=PB \
	python main.py \
		--host=b0,b1 \
		--np=4 \
		--task example_task.py