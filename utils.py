import torch
from transformers import AutoModelForVision2Seq, AutoProcessor
import yaml
import os

def get_yolo_model():
    with open("config/model_config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    model = torch.hub.load('ultralytics/yolov5', 'custom', 
                          path=config['model']['icon_detect']['weights'])
    return model

def get_caption_model_processor():
    with open("config/model_config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    model_path = config['model']['icon_caption']['path']
    model = AutoModelForVision2Seq.from_pretrained(model_path)
    processor = AutoProcessor.from_pretrained(model_path)
    return model, processor

def check_ocr_box(box):
    return len(box) == 4 and all(isinstance(x, (int, float)) for x in box)