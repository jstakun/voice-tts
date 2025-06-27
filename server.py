from fastapi import FastAPI, Response, Request, Header
from pydantic import BaseModel
import tempfile
import os
import logging
import torch
    
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USE_GPU = False
if torch.cuda.is_available():
  USE_GPU = True  
  logger.info("CUDA is available")
else:
  logger.info("CUDA is not available")

app = FastAPI()

# Load model from environment variable or use default
os.environ["COQUI_TOS_AGREED"] = "1"
MODEL_NAME = os.getenv("TTS_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2")
SPEAKER = os.getenv("TTS_SPEAKER", "Ludvig Milivoj") #"Andrew Chipper" "Claribel Dervla"

#set this env before TTS import
os.environ["NUMBA_CACHE_DIR"] = "/tmp" 

from TTS.api import TTS

tts = TTS(model_name=MODEL_NAME, gpu=USE_GPU)

logger.info(f"Available speakers '{tts.speakers}'")

logger.info(f"Selected model is '{MODEL_NAME}'")

logger.info(f"Selected speaker is '{SPEAKER}'")

class TTSRequest(BaseModel):
    text: str

@app.post("/synthesize")
def synthesize(request_data: TTSRequest, request: Request, accept_language: str = Header(default="en")):
    # Log the incoming request text
    logger.info(f"Received TTS request: text='{request_data.text}', language='{accept_language}'")

    synth_args = {
        "text": request_data.text,
        "speaker": SPEAKER
    }

    if "multilingual" in MODEL_NAME or "multi" in MODEL_NAME:
        synth_args["language"] = accept_language

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        synth_args["file_path"] = f.name
        tts.tts_to_file(**synth_args)
        audio_path = f.name

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    os.remove(audio_path)
    return Response(content=audio_data, media_type="audio/wav")

