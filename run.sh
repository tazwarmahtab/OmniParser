#!/bin/bash

# Activate conda environment
conda activate omni || {
    echo "Creating new conda environment 'omni'..."
    conda create -n "omni" python==3.12 -y
    conda activate omni
}

# Install dependencies
pip install -r requirements.txt

# Create weights directory structure if it doesn't exist
mkdir -p weights/icon_detect weights/icon_caption_florence

# Download model weights if they don't exist
if [ ! -f "weights/icon_detect/model.pt" ]; then
    echo "Downloading model weights..."
    for f in icon_detect/{train_args.yaml,model.pt,model.yaml} icon_caption/{config.json,generation_config.json,model.safetensors}; do 
        huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights
    done
    
    # Rename caption folder
    mv weights/icon_caption weights/icon_caption_florence
fi

# Run the demo
python demo.py
