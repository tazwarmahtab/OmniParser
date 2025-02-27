import torch
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor
import yaml
import os

class OmniParserV2:
    def __init__(self, config_path="config/model_config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load detection model
        self.detect_model = torch.hub.load(
            self.config['model_paths']['icon_detect'],
            'custom',
            path='model.pt',
            source='local'
        )
        
        # Load caption model
        self.caption_model = AutoModelForVision2Seq.from_pretrained(
            self.config['model_paths']['icon_caption']
        )
        self.processor = AutoProcessor.from_pretrained(
            self.config['model_paths']['icon_caption']
        )

    def parse_screen(self, image_path):
        image = Image.open(image_path)
        
        # Detect UI elements
        results = self.detect_model(image)
        boxes = results.xyxy[0].cpu().numpy()
        
        # Generate captions for detected regions
        outputs = []
        for box in boxes:
            region = image.crop(box[:4])
            inputs = self.processor(images=region, return_tensors="pt")
            generated = self.caption_model.generate(
                **inputs,
                max_length=self.config['caption']['max_length'],
                num_beams=self.config['caption']['num_beams']
            )
            caption = self.processor.decode(generated[0], skip_special_tokens=True)
            outputs.append({
                'box': box[:4].tolist(),
                'caption': caption,
                'confidence': float(box[4])
            })
        
        return outputs

if __name__ == "__main__":
    parser = OmniParserV2()
    
    # Example usage
    results = parser.parse_screen("example_screen.png")
    for result in results:
        print(f"Found: {result['caption']} at {result['box']} (conf: {result['confidence']:.2f})")
