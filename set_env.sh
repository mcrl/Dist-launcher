# Start timer
start=$(date +%s)

# Set up conda environment
conda create -n dist-launcher python=3.11
conda activate dist-launcher

# Install necessary packages
#conda install -c conda-forge mpi4py

# End timer
end=$(date +%s)

# Print time taken
minutes=$(( ($end - $start) / 60 ))
seconds=$(( ($end - $start) % 60 ))
echo "Time taken: $minutes minutes and $seconds seconds"