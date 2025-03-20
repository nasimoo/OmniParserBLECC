#!/bin/bash
# Script to run element existence check using MPS (Apple Silicon GPU)

# Ensure the virtual environment is activated (if you're using one)
# source myenv/bin/activate

# Install or update the required packages
echo "============================="
echo "Installing/updating required packages..."
echo "============================="
pip install -U accelerate transformers

# Create backup of original script
if [ ! -f "elementexists.py.bak" ]; then
    cp elementexists.py elementexists.py.bak
    echo "Created backup of original script as elementexists.py.bak"
fi

# Try with 4B model first
echo "============================="
echo "Running with 4B model - MPS using FP16 precision (default)"
echo "This uses less memory but may be less precise"
echo "============================="
python elementexists.py

# If the above fails, try with FP32 precision
if [ $? -ne 0 ]; then
    echo "============================="
    echo "FP16 failed, trying with FP32 precision"
    echo "This uses more memory but may be more stable"
    echo "============================="
    python elementexists.py --precision fp32
fi

# If that also fails, try with 2B model
if [ $? -ne 0 ]; then
    echo "============================="
    echo "4B model failed, trying with 2B model"
    echo "This uses significantly less memory"
    echo "============================="
    
    # Replace the model ID in the script
    sed -i.tmp 's/model_id = "google\/gemma-3-4b-it"/model_id = "google\/gemma-3-2b-it"/' elementexists.py
    python elementexists.py
    
    # Restore the original model ID
    sed -i.tmp 's/model_id = "google\/gemma-3-2b-it"/model_id = "google\/gemma-3-4b-it"/' elementexists.py
    rm -f elementexists.py.tmp
fi

# If that also fails, try with CPU fallback
if [ $? -ne 0 ]; then
    echo "============================="
    echo "MPS failed, falling back to CPU with 2B model"
    echo "This will be slower but more compatible"
    echo "============================="
    
    # Replace the model ID in the script
    sed -i.tmp 's/model_id = "google\/gemma-3-4b-it"/model_id = "google\/gemma-3-2b-it"/' elementexists.py
    python elementexists.py --fallback
    
    # Restore the original model ID
    sed -i.tmp 's/model_id = "google\/gemma-3-2b-it"/model_id = "google\/gemma-3-4b-it"/' elementexists.py
    rm -f elementexists.py.tmp
fi

echo "Done!" 