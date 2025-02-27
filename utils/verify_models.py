import os
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)

def verify_model_files():
    """Verify all required model files are present"""
    with open('config/model_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    missing_files = []
    
    # Check detection model files
    detect_config = config['model_paths']['icon_detect']
    for file in ['model_file', 'train_args', 'model_config']:
        path = Path(detect_config['path']) / detect_config[file]
        if not path.exists():
            missing_files.append(str(path))
    
    # Check caption model files
    caption_config = config['model_paths']['icon_caption']
    for file in ['model_file', 'config_file', 'generation_config']:
        path = Path(caption_config['path']) / caption_config[file]
        if not path.exists():
            missing_files.append(str(path))
    
    if missing_files:
        logger.error("Missing model files: %s", '\n'.join(missing_files))
        logger.error("""
Please download the model files using:
for f in icon_detect/{train_args.yaml,model.pt,model.yaml} icon_caption/{config.json,generation_config.json,model.safetensors}; do 
    huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights
done
""")
        return False
    
    return True

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    verify_model_files()
