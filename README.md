# wav2vec2 for ASR

This repository contains the code to use the `wav2vec2-large-960h` model developed by Facebook and pretrained and fine-tuned on Librispeech dataset on 16kHz sampled speech audio. Although the model is trained on 16kHz sampled audio, users can still use it for other sampling rates as there will be an automatic resampling step in the code.

The project includes code for API development, containerization with Docker, data processing scripts, deployment design using AWS, and files for setting up the ASR service and Elasticsearch backend with a Search-UI frontend.

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Git
- Python 3.10 or newer
- Docker
- Docker Compose (for running multi-container Docker applications)

### Repository Structure

The repository is structured as follows:

- `/asr`: Contains the ASR API code, Dockerfile, and requirements for the ASR service. (Task 2)
- `/common_voice`: Contains the Common Voice dataset and the original `cv-valid-dev.csv` file. You may ignore this folder.
- `/deployment-design`: Contains the proposed deployment architecture design in PDF. (Task 3)
- `/elastic-backend`: Contains the Elasticsearch backend setup files. (Task 3)
- `/search-ui`: Contains the Search-UI frontend setup files. (Task 3)
- `/.gitignore`: Specifies intentionally untracked files to ignore.
- `/README.md`: This file, detailing setup and usage instructions.

---

## Task 2: Automatic Speech Recognition (ASR) Service Setup

In the `/asr` directory.

This task focuses on deploying an ASR service using the `wav2vec2-large-960h` model to transcribe audio files. The service will be containerized using Docker and will provide an API endpoint for transcription requests. It also includes the resulting `cv-valid-dev.csv` file with generated transcriptions and updated duration columns.

### ASR Directory Structure

- `/asr/asr_api.py`: The main Python script for the ASR API.
  - **API Endpoints**:
    - `/ping`: GET request to check if the API is running.
    - `/asr`: POST request to transcribe audio files.
- `/asr/config.yaml`: Configuration file for the ASR service.
- `/asr/cv-decode.py`: Script to transcribe audio files using the ASR API.
- `/asr/cv-valid-dev.csv`: Common Voice dataset with generated transcriptions and updated duration columns.
- `/asr/Dockerfile`: Dockerfile to containerize the ASR API.
- `/asr/requirements.txt`: Specific Python libraries required for the ASR service.

### Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/jye-lim/wav2vec2-asr.git
    cd wav2vec2-asr
    ```

2. **Install Dependencies (Optional)**

    If you want to run the ASR service locally, install the required Python libraries:

    ```bash
    cd asr
    pip install -r requirements.txt
    ```

### Setting Up the ASR Service

1. **API Development**
    - **Ping API**: `http://localhost:8001/ping` (GET) returns "pong".
    - **ASR API**: `http://localhost:8001/asr` (POST)
        - Accepts `multipart/form-data` with a field named `file` for the audio file.
        - Returns JSON containing `transcription` and `duration`.
        - Example:

        ```json
        {
            "transcription": "BE CAREFUL WITH YOUR PROGNOSTICATIONS SAID THE STRANGER",
            "duration": "1.69"
        }
        ```

2. **Containerization**

    - Ensure you are in the `asr` directory.

    ```bash
    cd asr
    ```

    - Build a Docker container for the ASR API:

    ```bash
    docker build -t asr-api .
    ```

    - Run the container:

    ```bash
    docker run -p 8001:8001 asr-api
    ```

3. **Testing the API**

    - Use CURL to test the Ping API:

    ```bash
    curl http://localhost:8001/ping
    ```

    - Use CURL to test the ASR API:

    ```bash
    curl -F 'file=@/home/jye/cv-valid-dev/sample-000000.mp3' http://localhost:8001/asr
    ```

4. **Transcribing Audio Files**

    - Use `cv-decode.py` to transcribe audio files. Please adjust the file paths accordingly in the `config.yaml` file.

    ```bash
    python cv-decode.py
    ```

5. **Additional Notes**:

    - After running the `cv-decode.py` script, the transcriptions will be added to the `cv-valid-dev.csv` file and the processed audio file used will be removed, as per the task requirements.
    - Hence, the `/common_voice` directory does not contain any audio files as they are processed and removed during the transcription process.
    - For the transcribed results, refer to the updated `cv-valid-dev.csv` file in the `asr` directory.

---

## Task 3: Deployment Architecture Design

In the `/deployment-design` directory.

The architecture will be deployed on AWS and includes 2 nodes of Elasticsearch for data storage and a Search-UI frontend for querying the transcriptions.

You may find the architecture design at `/deployment-design/design.pdf`.

The Elasticsearch cluster will store the transcriptions and the 2 nodes will be deployed on separate instances for redundancy and scalability. Hence, when one node fails, the other can still serve requests.

The Search-UI frontend will allow users to query the transcriptions based on various fields such as `generated_text`, `duration`, `age`, `gender`, and `accent`.

These 3 components will be deployed using Docker Compose in their respective instances on AWS, and these instances will be in the same security group to allow communication between the services.

## Task 4: Elasticsearch Backend Setup

In the `/elastic-backend` directory.

This task involves setting up the Elasticsearch backend to store the transcriptions and metadata. The backend will be deployed using Docker Compose with a 2-node Elasticsearch cluster in their respective instances.

- `/elastic-backend/cv-index.py`: Python script to read `cs-valid-dev.csv` and index records into Elasticsearch under the index `cv-transcriptions`.
- `/elastic-backend/docker-compose-node1.yml`: Docker Compose file for the first Elasticsearch node in the first instance.
- `/elastic-backend/docker-compose-node2.yml`: Docker Compose file for the second Elasticsearch node in the second instance.

To set up the Elasticsearch backend locally:

1. **Start the Elasticsearch Nodes**

    - Ensure you are in the `elastic-backend` directory.

    ```bash
    cd elastic-backend
    ```

    - Start the first Elasticsearch node:

    ```bash
    docker-compose -f docker-compose-node1.yml up -d
    ```

    - Start the second Elasticsearch node:

    ```bash
    docker-compose -f docker-compose-node2.yml up -d
    ```

2. **Indexing Transcriptions**

    - Run the `cv-index.py` script to index the transcriptions into Elasticsearch.

    ```bash
    python cv-index.py
    ```

3. **Additional Notes**:

    - Please modify the `docker-compose-node_.yml` fields to adjust the Elasticsearch endpoint to point to the correct Elasticsearch instance.
    - If you encounter a exit code 78 error, please run the following command:

        ```bash
        sudo sysctl -w vm.max_map_count=262144
        ```

### Task 5: Search-UI Frontend Setup

In the `/search-ui` directory.

This task involves setting up the Search-UI frontend to query the transcriptions stored in the Elasticsearch backend. The frontend will be deployed using Docker Compose in its respective instance.

The files in the `search-ui` directory are referenced from the [Elasticsearch Search-UI](https://docs.elastic.co/search-ui/tutorials/elasticsearch) template for indexing and querying movie data.

The files have been modified to query the `cv-transcriptions` index and to accommodate the search fields such as `generated_text`, `duration`, `age`, `gender`, and `accent`.

To set up the Search-UI frontend locally:

1. **Start the Search-UI**

    - Ensure you are in the `search-ui` directory.

    ```bash
    cd search-ui
    ```

    - Start the Search-UI frontend:

    ```bash
    docker-compose up -d
    ```

2. **Accessing the Search-UI**

    - Open your browser and go to `http://localhost:3000` to access the Search-UI frontend.

3. **Querying Transcriptions**

    - Use the Search-UI to query the transcriptions based on the available fields.

4. **Additional Notes**:

    - Please modify the `docker-compose.yml` fields to adjust the Elasticsearch endpoint to point to the correct Elasticsearch instance.
    - Please modify the `search-ui/src/App.js` file to adjust the Elasticsearch endpoint to point to the correct Elasticsearch instance.
    - When querying the transcriptions using the search box, the following error may occur: `TypeError: Cannot convert undefined or null to object`. This is likely due to the template's code and may require further debugging. But due to time constraints, this issue has not been resolved.

---

## Task 6: AWS Cloud Deployment

This task involves deploying the ASR service, Elasticsearch backend, and Search-UI frontend on AWS using the proposed architecture design.

1. **Deploy Elasticsearch Nodes**

    - Deploy the Elasticsearch nodes on separate instances using the provided Docker Compose files.

2. **Deploy Search-UI Frontend**

    - Deploy the Search-UI frontend on a separate instance using the provided Docker Compose file.

## Task 7: Deployment URL

The deployment URL for the Search-UI frontend is:

[http://18.140.85.243:3000/](http://18.140.85.243:3000/)

## Task 8: Essay Question

The essay question has been answered in the `essay.pdf` file in the root directory.
