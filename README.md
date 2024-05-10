# PrivateGPT-with-gpt4all

PrivateGPT-with-gpt4all is a Streamlit application that allows users to upload their documents and interact with the contents using advanced AI models, including local AI implementations and LangChain. This tool is designed to provide a private and secure environment for AI interactions with user data.

## Features

- **File Upload**: Users can upload various types of documents to query information or generate content based on the uploaded material.
- **AI Interaction**: Utilizes both LangChain and local AI models for processing and generating responses.
- **Docker Support**: Includes a Dockerfile for easy and consistent deployment.

## Prerequisites

- Docker installed on your machine
- Basic knowledge of Docker and Streamlit if you wish to modify the app

## Installation and Running with Docker

1. **Clone the repository:**

```bash
git clone https://github.com/abdulzain6/PrivateGPT-with-gpt4all.git
cd PrivateGPT-with-gpt4all
```

2. **Build the Docker container:**

```bash
docker build -t privategpt-with-gpt4all .
```

3. **Run the application:**

```bash
docker run -p 8501:8501 privategpt-with-gpt4all
```

After running the command, open your web browser and navigate to `http://localhost:8501` to start using the application.

## Usage

- **Uploading Files**: Drag and drop your files into the upload area within the Streamlit interface.
- **Interacting with AI**: After uploading, you can type in queries or prompts, and the AI will respond based on the contents of your uploaded documents.

## Contributing

Your contributions are welcome! Please fork this repository, make your changes, and submit a pull request.
