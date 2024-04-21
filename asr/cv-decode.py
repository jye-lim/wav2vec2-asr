#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
from pathlib import Path

# Libs
import pandas as pd
import requests
import yaml

# Custom


##################
# Configurations #
##################

# Load configurations
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Load inference API URL
INFER_URL = config["api"]["infer_url"]

# Load data paths
CSV_NAME = config["paths"]["csv_name"]
DATA_PATH = Path(config["paths"]["data_dir"])
OUTPUT_PATH = Path(config["paths"]["output_dir"])

#############
# Functions #
#############


def transcribe_audio(file_path: str) -> dict[str, str]:
    """
    Transcribe audio file using inference API.

    Args:
        file_path (str): Path to audio file.

    Returns:
        dict[str, str]: Transcription result.
    """
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "audio/mpeg")}
        response = requests.post(INFER_URL, files=files)
        if response.status_code == 200:
            return response.json()
        else:
            return {"transcription": None, "duration": None}


def process_audio_files(df: pd.DataFrame, audio_folder: Path) -> pd.DataFrame:
    """
    Process audio files in DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing audio file paths.
        audio_folder (Path): Path to folder containing audio files.

    Returns:
        pd.DataFrame: Updated DataFrame with transcriptions.
    """
    print(f"Processing {len(df)} audio files...")

    # Iterate over each row in DataFrame
    for i, row in df.iterrows():
        # Transcribe audio
        audio_path = audio_folder / row["filename"]
        if audio_path.exists():
            result = transcribe_audio(audio_path)
            df.at[i, "generated_text"] = result["transcription"]

        # Delete audio file when done
        audio_path.unlink()

    print(f"Done processing {len(df)} audio files!")
    return df


def main():
    """
    Main function to process audio files and update CSV.
    """
    # Load mappings from CSV file
    csv_path = DATA_PATH / CSV_NAME
    df = pd.read_csv(csv_path)

    # Add column for transcription
    df["generated_text"] = None

    # Process audio files
    df_updated = process_audio_files(df, DATA_PATH)

    # Save updated CSV
    updated_csv_name = CSV_NAME.replace(".csv", "_updated.csv")
    updated_csv_path = OUTPUT_PATH / updated_csv_name
    df_updated.to_csv(updated_csv_path, index=False)


###########
# Classes #
###########


##########
# Script #
##########


if __name__ == "__main__":
    main()
