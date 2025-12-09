import os

# Constants
EMB_VERTEXAI = "text-embedding-004"
LLM_VERTEXAI = "gemini-1.5-flash"

# Database connection with environment variables
DB_USER = os.environ.get("DB_USER", "pgvector")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "pgvector")
PGVECTOR_CONNECTION = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@localhost:5432/{POSTGRES_DB}"
)
