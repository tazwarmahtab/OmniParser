import torch
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor, PretrainedConfig
import yaml
from pathlib import Path
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OmniParserV2:
    def __init__(self, config_path="config/model_config.yaml"):
        self.load_config(config_path)
        self.setup_models()
        
    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise

    def setup_models(self):
        try:
            # Initialize models with error handling and logging
            self.detect_model = self._load_detection_model()
            self.caption_model, self.processor = self._load_caption_model()
            
            # Move models to GPU if available
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.detect_model.to(self.device)
            self.caption_model.to(self.device)
            
            logger.info(f"Models loaded successfully. Using device: {self.device}")
        except Exception as e:
            logger.error(f"Error setting up models: {e}")
            raise

    def _load_detection_model(self):
        detect_config = self.config['model_paths']['icon_detect']
        model_path = os.path.join(detect_config['path'], detect_config['model_file'])
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        try:
            from ultralytics import YOLO
            model = YOLO(model_path)
            logger.info(f"Successfully loaded YOLO model from {model_path}")
            return model
        except Exception as e:
            logger.error(f"Error loading detection model: {e}")
            raise

    def _load_caption_model(self):
        caption_config = self.config['model_paths']['icon_caption']
        model_dir = caption_config['path']
        
        # Verify model files exist
        required_files = [
            caption_config['model_file'],
            caption_config['config_file'],
            caption_config['generation_config']
        ]
        
        for file in required_files:
            if not os.path.exists(os.path.join(model_dir, file)):
                raise FileNotFoundError(f"Missing required file: {os.path.join(model_dir, file)}")

        # Load model with specific config files
        config = PretrainedConfig.from_pretrained(
            model_dir,
            local_files_only=True
        )
        
        model = AutoModelForVision2Seq.from_pretrained(
            model_dir,
            config=config,
            local_files_only=True
        )
        
        processor = AutoProcessor.from_pretrained(
            model_dir,
            local_files_only=True
        )
        
        return model, processor

    @torch.no_grad()
    def parse_screen(self, image_path):
        try:
            image = Image.open(image_path)
            
            # Run detection with YOLO model directly
            results = self.detect_model.predict(image, device=self.device)[0]
            boxes = results.boxes.data.cpu().numpy()  # Get boxes in numpy format
            
            # Process detected regions in batches
            batch_size = 16
            outputs = []
            
            for i in range(0, len(boxes), batch_size):
                batch_boxes = boxes[i:i + batch_size]
                batch_regions = [image.crop(box[:4]) for box in batch_boxes]
                
                # Process batch
                inputs = self.processor(images=batch_regions, return_tensors="pt", padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                generated = self.caption_model.generate(
                    **inputs,
                    max_length=self.config['caption']['max_length'],
                    num_beams=self.config['caption']['num_beams']
                )
                
                captions = self.processor.batch_decode(generated, skip_special_tokens=True)
                
                for box, caption in zip(batch_boxes, captions):
                    outputs.append({
                        'box': box[:4].tolist(),
                        'caption': caption,
                        'confidence': float(box[4])
                    })
            
            return outputs
            
        except Exception as e:
            logger.error(f"Error in parse_screen: {e}")
            raise

