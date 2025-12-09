import os

import chainlit as cl
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.runnable import RunnableConfig

from confluence_qa import ConfluenceQA

confluence_url = os.environ.get(
    "CONFLUENCE_URL", "https://templates.atlassian.net/wiki/"
)
confluence_username = os.environ.get("CONFLUENCE_USERNAME", None)
confluence_api_key = os.environ.get("CONFLUENCE_API_KEY", None)
confluence_space_key = os.environ.get("CONFLUENCE_SPACE_KEY", "RD")


@cl.on_chat_start
async def on_chat_start():
    confluence_qa = ConfluenceQA(
        config={
            "confluence_url": confluence_url,
            "username": confluence_username,
            "api_key": confluence_api_key,
            "space_key": confluence_space_key,
        }
    )

    cl.user_session.set("confluence_qa", confluence_qa)

    # Send action button to load confluence data
    actions = [
        cl.Action(
            name="Load Confluence data",
            value="load_confluence_data",
            description="Click to load confluence data",
        )
    ]

    await cl.Message(
        content="Click the button to load confluence data", actions=actions
    ).send()


@cl.action_callback("Load Confluence data")
async def on_load_confluence_data(action: cl.Action):
    confluence_qa = cl.user_session.get("confluence_qa")
    if confluence_qa is None:
        await cl.Message(content="Confluence QA not initialized").send()

    confluence_qa.init_embeddings()
    confluence_qa.init_models()
    await confluence_qa.vector_db_confluence_docs()
    confluence_qa.retreival_qa_chain()

    await cl.Message(content="Successfully loaded Confluence data").send()


@cl.on_message
async def on_message(message: cl.Message):
    confluence_qa = cl.user_session.get("confluence_qa")
    if confluence_qa is None:
        await cl.Message(content="Confluence QA not initialized").send()
    msg = cl.Message(content="")

    class PostMessageHandler(BaseCallbackHandler):
        """
        Callback handler for handling the retriever and LLM processes.
        Used to post the sources of the retrieved documents as a Chainlit element.
        """

        def __init__(self, msg: cl.Message):
            BaseCallbackHandler.__init__(self)
            self.msg = msg
            self.sources = set()  # To store unique pairs

        def on_retriever_end(self, documents, *, run_id, parent_run_id, **kwargs):
            for d in documents:
                print(f"Metadata: {d.metadata}")
                source_page_pair = (d.metadata["source"], d.metadata["title"])
                self.sources.add(source_page_pair)

        def on_llm_end(self, response, *, run_id, parent_run_id, **kwargs):
            if len(self.sources):
                sources_text = "\n".join([f"{source}" for source, _ in self.sources])
                self.msg.elements.append(
                    cl.Text(name="Sources", content=sources_text, display="inline")
                )

    async for chunk in confluence_qa.qa.astream(
        message.content,
        config=RunnableConfig(
            callbacks=[cl.LangchainCallbackHandler(), PostMessageHandler(msg)]
        ),
    ):
        await msg.stream_token(chunk)

    await msg.send()
