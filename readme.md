# Natural Language Querying over PDF Documents Using a RAG-Based Conversational Agent

## Introduction

In today's fast-paced world, efficient access to information is crucial for organizations. DocuGenie, our cutting-edge AI bot, is designed to revolutionize the way you handle and extract information from your local PDF files.

## Demo

<a href="https://drive.google.com/file/d/1KI1r9M6jVKRDYc2VzmoZrpF2j3EcIpCJ/view?usp=sharing">Click here to watch a demo</a>

## Features

1. Chat History: The app provides a chat history feature, allowing users to access previous chat sessions.

2. Multiple PDF Upload: Users can upload multiple PDFs, with a maximum file size of 200MB.

3. Automatic Chat History Saving: The app automatically saves chat history to their respective chat sessions.

4. Contextual Answering: The app filters out invalid or offensive questions and only answers questions related to the uploaded PDFs. Out-of-context questions are not answered.

5. Accurate Answers: The app guarantees 100% accuracy in retrieving answers from the uploaded PDFs.

## How It Works

The application follows these steps to provide responses to your questions:

1. PDF Loading: The app reads multiple PDF documents and extracts their text content.

2. Text Chunking: The extracted text is divided into smaller chunks that can be processed effectively.

3. Language Model: The application utilizes a language model to generate vector representations (embeddings) of the text chunks.

4. Similarity Matching: When you ask a question, the app compares it with the text chunks and identifies the most semantically similar ones.

5. Response Generation: The selected chunks are passed to the language model, which generates a response based on the relevant content of the PDFs.

## Dependencies and Installation

---

To install the MultiPDF Chat App, please follow these steps:

1. Clone the repository to your local machine.

2. Install the required dependencies by running the following command:

   ```
   pip install -r requirements.txt
   ```

3. Download Ollama and install llamma3 into your system locally -- <a href="https://ollama.com/download">Ollama Download</a>

## Usage

To use the MultiPDF Chat App, follow these steps:

1. Ensure that you have installed the required dependencies and make sure Ollama is running in the background.

2. Run the `app.py` file using the Streamlit CLI. Execute the following command:

   ```
   streamlit run app.py
   ```

3. The application will launch in your default web browser, displaying the user interface.

4. Load multiple PDF documents into the app by following the provided instructions.

5. Ask questions in natural language about the loaded PDFs using the chat interface.
