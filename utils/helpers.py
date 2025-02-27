import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def ensure_dir(path: str) -> Path:
    """Ensure directory exists and return Path object"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def cleanup_temp_files(directory: str) -> None:
    """Remove temporary files from directory"""
    try:
        p = Path(directory)
        if p.exists():
            for f in p.glob('*'):
                if f.is_file():
                    f.unlink()
    except Exception as e:
        logger.error(f"Error cleaning temp files: {e}")
