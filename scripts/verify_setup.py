import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_setup():
    required_dirs = [
        'weights/icon_detect',
        'weights/icon_caption',
        'temp',
    ]
    
    required_files = [
        'weights/icon_detect/model.pt',
        'weights/icon_caption/model.safetensors',
        'weights/icon_caption/config.json',
        'weights/icon_caption/generation_config.json',
    ]
    
    # Check directories
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True)
            logger.info(f"Created directory: {dir_path}")
    
    # Check files
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error("Missing required model files:")
        for file in missing_files:
            logger.error(f"  - {file}")
        return False
    
    logger.info("All required directories and files are present")
    return True

if __name__ == "__main__":
    verify_setup()
