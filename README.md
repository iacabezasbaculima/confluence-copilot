# Confluence Copilot

A powerful Q&A chatbot that enables natural language querying of your Confluence spaces using RAG (Retrieval-Augmented Generation) technology. Built with LangChain, Google Vertex AI, and PostgreSQL with pgvector for semantic search.

## Features

- 🤖 **AI-Powered Q&A**: Ask questions about your Confluence content in natural language
- 🔍 **Semantic Search**: Uses advanced embeddings to find relevant content across your Confluence space
- 🎯 **RAG Architecture**: Retrieval-Augmented Generation for accurate, context-aware answers
- 📊 **Dual Interface**: Both Streamlit web app and Chainlit chat interface
- 🔒 **Authentication Support**: Works with both public and private Confluence spaces
- 📚 **Source Attribution**: Shows which Confluence pages were used to generate answers

## Tech Stack

- **LangChain**: Framework for building LLM applications
- **Google Vertex AI**: LLM (Gemini 1.5 Flash) and embeddings (text-embedding-004)
- **PostgreSQL + pgvector**: Vector database for semantic search
- **Streamlit**: Web application interface
- **Chainlit**: Interactive chat interface
- **Atlassian Python API**: Confluence content extraction

## Prerequisites

- Python 3.9+
- Docker (for PostgreSQL with pgvector)
- Google Cloud Platform account with Vertex AI enabled
- Confluence access (API key for private spaces)

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd confluence-copilot
   ```

2. **Install dependencies using Poetry**:

   ```bash
   poetry install
   ```

3. **Start PostgreSQL with pgvector**:

   ```bash
   make docker-up
   ```

   To stop pgvector or view its logs:

   ```bash
   make docker-down
   make docker-logs
   ```

## Configuration

Set up the following environment variables:

```bash
# Confluence Configuration
export CONFLUENCE_URL="https://your-domain.atlassian.net/wiki/"
export CONFLUENCE_USERNAME="your-email@domain.com"  # Optional for public spaces
export CONFLUENCE_API_KEY="your-api-key"           # Optional for public spaces
export CONFLUENCE_SPACE_KEY="SPACE"                # Your confluence space key

# Database Configuration
export DB_USER="pgvector"                          # PostgreSQL username (default: pgvector)
export DB_PASSWORD="password"                      # PostgreSQL password (default: password)

# Google Cloud Configuration (ensure you're authenticated with gcloud)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### Getting Confluence API Key

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create an API token
3. Use your email as username and the token as password

### Setting up Google Cloud

1. Create a project in Google Cloud Console
2. Enable Vertex AI API
3. Create a service account with Vertex AI permissions
4. Download the service account key file
5. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## Usage

### Streamlit Web App

Run the interactive web application:

```bash
make run
```

The app will be available at `http://localhost:8787`

**Features:**

- Configure Confluence connection through the sidebar
- Enter your Confluence URL, credentials, and space key
- Ask questions about your Confluence content
- Get AI-powered answers with source attribution

### Chainlit Chat Interface

Run the chat interface:

```bash
make run-cl
```

**Features:**

- Interactive chat experience
- Real-time streaming responses
- Source document attribution
- Click-to-load Confluence data

## How It Works

1. **Document Extraction**: Loads content from specified Confluence space using the Atlassian API
2. **Text Processing**: Splits documents into chunks optimized for embeddings
3. **Vector Storage**: Creates embeddings using Vertex AI and stores them in pgvector
4. **Semantic Search**: Retrieves relevant chunks based on user questions
5. **Answer Generation**: Uses Gemini 1.5 Flash to generate contextual answers
6. **Source Attribution**: Shows which Confluence pages contributed to the answer

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Confluence    │────│  Document       │────│   Text          │
│     Space       │    │  Extraction     │    │  Splitting      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Vector       │────│   Embeddings    │────│   Chunked       │
│   Database      │    │  (Vertex AI)    │    │  Documents      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │
        ├── Retrieval ──┐
                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Answer      │────│      LLM        │────│   Retrieved     │
│                 │    │ (Gemini Flash)  │    │   Context       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Project Structure

```
confluence-copilot/
├── src/
│   ├── app.py              # Streamlit web application
│   ├── cl_app.py           # Chainlit chat application
│   ├── confluence_qa.py    # Core Q&A functionality
│   └── constants.py        # Configuration constants
├── chainlit.md             # Chainlit welcome page
├── pyproject.toml          # Poetry dependencies
├── Makefile               # Convenience commands
└── README.md              # This file
```

## Troubleshooting

### Common Issues

1. **PostgreSQL Connection Error**:
   - Ensure Docker is running: `docker ps`
   - Restart pgvector: `docker restart pgvector`
   - Check if `DB_USER` and `DB_PASSWORD` environment variables are set correctly
   - Verify the database credentials match between your environment and the Docker container

2. **Vertex AI Authentication Error**:
   - Check `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
   - Verify service account has Vertex AI permissions
   - Run `gcloud auth application-default login`

3. **Confluence API Error**:
   - Verify API key is correct and not expired
   - Check if the space key exists and you have access
   - For public spaces, leave username/API key empty

4. **Out of Memory Error**:
   - Reduce `limit` in ConfluenceLoader (default: 100)
   - Adjust `chunk_size` in text splitters

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

- Built with [LangChain](https://langchain.com/) framework
- Powered by [Google Vertex AI](https://cloud.google.com/vertex-ai)
- Vector storage with [pgvector](https://github.com/pgvector/pgvector)
- UI components from [Streamlit](https://streamlit.io/) and [Chainlit](https://chainlit.io/)
