import os

from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
from langchain_community.document_loaders import ConfluenceLoader
from langchain_community.document_loaders.confluence import ContentFormat
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from sqlalchemy.ext.asyncio import create_async_engine

from constants import *

# https://python.langchain.com/docs/tutorials/rag/
# https://github.com/langchain-ai/langchain-postgres/blob/main/examples/vectorstore.ipynb


class ConfluenceQA:
    def __init__(self, config: dict = {}):
        self.config = config
        self.embedding = None
        self.vectordb = None
        self.llm = None
        self.qa = None
        self.retriever = None

    def init_embeddings(self) -> None:
        # VertexAI embeddings API
        self.embedding = VertexAIEmbeddings(
            project=os.environ.get("GCP_PROJECT"),
            location="europe-west1",
            model_name=EMB_VERTEXAI,
        )
        print("Initialized embeddings")

    def init_models(self) -> None:
        # VertexAI models API
        self.llm = ChatVertexAI(
            project=os.environ.get("GCP_PROJECT"),
            location="europe-west1",
            model_name=LLM_VERTEXAI,
            temperature=0.0,
        )
        print("Initialized models")

    async def vector_db_confluence_docs(self) -> None:
        """
        creates vector db for the embeddings and persists them or loads a vector db from the persist directory
        """
        confluence_url = self.config.get("confluence_url", None)
        username = self.config.get("username", None)
        api_key = self.config.get("api_key", None)
        space_key = self.config.get("space_key", None)

        ## 1. Extract the documents
        loader = ConfluenceLoader(
            url=confluence_url,
            username=username,
            api_key=api_key,
            space_key=space_key,
            limit=100,
            content_format=ContentFormat.VIEW,
        )
        documents = loader.load()

        for doc in documents:
            print(f"Metadata: {doc.metadata}")
            print(f"Content: {doc.page_content}")
            print("\n")

        ## 2. Split the texts
        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        text_splitter = TokenTextSplitter(
            chunk_size=1000, chunk_overlap=10, encoding_name="cl100k_base"
        )
        texts = text_splitter.split_documents(texts)
        for text in texts:
            print(text)

        ## 3. Create Embeddings and add to vector db
        engine = create_async_engine(PGVECTOR_CONNECTION)
        self.vectordb = PGVector(
            connection=engine,
            collection_name="confluence_docs",
            embeddings=self.embedding,
            use_jsonb=True,
            async_mode=True,
        )
        await self.vectordb.aadd_documents(texts)

    def retreival_qa_chain(self):
        """
        Creates retrieval qa chain using vectordb as retriever and LLM to complete the prompt
        """
        prompt_template = """You are a Confluence chatbot answering questions. Use the following pieces of context to answer the question at the end. If you don't know the answer, say that you don't know, don't try to make up an answer.

        Context: {context}
        Question: {question}
        Answer:
        """
        custom_prompt = PromptTemplate(template=prompt_template)

        def format_docs(docs):
            return "\n\n".join([d.page_content for d in docs])

        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 4})
        self.qa = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | custom_prompt
            | self.llm
            | StrOutputParser()
        )

    def answer_confluence(self, question: str) -> str:
        """
        Answer the question
        """
        answer = self.qa.invoke(question)
        return answer
