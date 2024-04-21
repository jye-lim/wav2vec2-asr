#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in


# Libs
import librosa
import soundfile as sf
import torch
import yaml

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

# Custom


##################
# Configurations #
##################

# Load configurations
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Load model and processor
processor = Wav2Vec2Processor.from_pretrained(config["model"]["name"])
model = Wav2Vec2ForCTC.from_pretrained(config["model"]["name"])

# Set model in evaluation mode since we're only running inference
model.eval()

# Set sampling rate to 16kHz
TARGET_SR = config["sampling_rate"]["target"]

# Define FastAPI app
app = FastAPI()

#############
# Functions #
#############


@app.get("/ping")
async def ping() -> JSONResponse:
    """
    Check if the API is running.

    Returns:
        JSONResponse: A JSON response indicating that the API is running.
    """
    return JSONResponse(content={"message": "pong"})


@app.post("/asr")
async def transcribe_audio(file: UploadFile = File(...)) -> JSONResponse:
    """
    Transcribe an audio file using the Wav2Vec2 model.

    Args:
        file (UploadFile): The audio file to transcribe.

    Returns:
        JSONResponse: The transcription and duration of the audio file.
    """
    # Load audio file
    data, sample_rate = sf.read(file.file, dtype="float32")

    # Check if resampling is needed
    if sample_rate != TARGET_SR:
        data = librosa.resample(data, orig_sr=sample_rate, target_sr=TARGET_SR)

    # Prepare input
    input_values = processor(
        data, return_tensors="pt", sampling_rate=TARGET_SR
    ).input_values

    # Model inference
    with torch.no_grad():
        logits = model(input_values).logits

    # Decode transcription
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)

    # Compute duration
    duration = len(data) / sample_rate

    return JSONResponse(
        content={"transcription": transcription[0], "duration": f"{duration:.2f}"}
    )


###########
# Classes #
###########


##########
# Script #
##########


if __name__ == "__main__":
    pass
