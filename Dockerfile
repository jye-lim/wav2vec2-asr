# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /usr/src/app

# Install libsndfile1 for soundfile
RUN apt-get update && apt-get install -y libsndfile1

# Install requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the codes last
COPY asr/ asr/
COPY config.yaml .

# Expose port
EXPOSE 8001

# Run main.py when the container launches
CMD ["uvicorn", "asr.asr_api:app", "--host", "0.0.0.0", "--port", "8001"]