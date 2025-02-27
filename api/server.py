from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import io
import os
from core.parser import OmniParserV2
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class APIServer:
    def __init__(self):
        self.app = FastAPI(title="OmniParser API")
        self.setup_middleware()
        self.setup_routes()
        self.parser = OmniParserV2()
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)

    def setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        @self.app.post("/parse")
        async def parse_image(file: UploadFile = File(...)):
            try:
                temp_path = self.temp_dir / f"{file.filename}"
                await self.save_upload(file, temp_path)
                
                results = self.parser.parse_screen(str(temp_path))
                
                temp_path.unlink()  # Clean up
                return JSONResponse(content={"results": results})
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "model_status": "loaded"}

    async def save_upload(self, file: UploadFile, path: Path):
        try:
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            image.save(path)
        except Exception as e:
            logger.error(f"Error saving upload: {e}")
            raise HTTPException(status_code=400, detail="Invalid image file")

    def run(self, host="0.0.0.0", port=8000):
        uvicorn.run(self.app, host=host, port=port, log_level="info")

