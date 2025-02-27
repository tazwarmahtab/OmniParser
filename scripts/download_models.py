import os
import logging
from pathlib import Path
import requests
from tqdm import tqdm
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_URLS = {
    "icon_detect": {
        "model.pt": "https://huggingface.co/omniparser/icon-detect/resolve/main/model.pt",
    },
    "icon_caption": {
        "model.safetensors": "https://huggingface.co/omniparser/icon-caption/resolve/main/model.safetensors",
        "config.json": "https://huggingface.co/omniparser/icon-caption/resolve/main/config.json",
        "generation_config.json": "https://huggingface.co/omniparser/icon-caption/resolve/main/generation_config.json"
    }
}

def download_file(url: str, dest_path: Path, desc: str = None) -> None:
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(dest_path, 'wb') as f, tqdm(
        desc=desc,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)

def main():
    weights_dir = Path("weights")
    
    for model_type, files in MODEL_URLS.items():
        logger.info(f"\nDownloading {model_type} files...")
        for filename, url in files.items():
            dest_path = weights_dir / model_type / filename
            if dest_path.exists():
                logger.info(f"File already exists: {dest_path}")
                continue
                
            try:
                download_file(url, dest_path, desc=f"Downloading {filename}")
                logger.info(f"Successfully downloaded {filename}")
            except Exception as e:
                logger.error(f"Error downloading {filename}: {e}")
                if dest_path.exists():
                    dest_path.unlink()

if __name__ == "__main__":
    main()
