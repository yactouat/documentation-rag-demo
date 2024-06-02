from datetime import datetime
from dotenv import load_dotenv
from llama_index.core import (
    # function to create better responses
    get_response_synthesizer,
    SimpleDirectoryReader,
    Settings,
    # abstraction that integrates various storage backends
    StorageContext,
    VectorStoreIndex
)
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.postgres import PGVectorStore
import os
import psycopg2
from sqlalchemy import make_url


def set_local_models(model: str = "deepseek-coder:1.3b"):
    # use Nomic
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="nomic-ai/nomic-embed-text-v1.5",
        trust_remote_code=True
    )
    # setting a high request timeout in case you need to build an answer based on a large set of documents
    Settings.llm = Ollama(model=model, request_timeout=120)


def get_streamed_rag_query_engine():
    # time the execution
    start = datetime.now()

    # of course, you can store db credentials in some secret place if you want
    connection_string = "postgresql://postgres:postgres@localhost:5432"
    db_name = "postgres"
    conn = psycopg2.connect(connection_string)
    conn.autocommit = True

    load_dotenv()

    set_local_models()

    db_url = make_url(connection_string)
    vector_store = PGVectorStore.from_params(
        database=db_name,
        host=db_url.host,
        password=db_url.password,
        port=db_url.port,
        user=db_url.username,
        table_name="knowledge_base_vectors",
        # embed dim for this model can be found on https://huggingface.co/nomic-ai/nomic-embed-text-v1.5
        embed_dim=768
    )

    # if index does not exist create it
    # storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # documents = SimpleDirectoryReader(os.environ.get("KNOWLEDGE_BASE_DIR"), recursive=True).load_data()
    # index = VectorStoreIndex.from_documents(
    #     documents, storage_context=storage_context, show_progress=True
    # )

    # if index already exists, load it
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=10,
    )
    # configure response synthesizer
    response_synthesizer = get_response_synthesizer(streaming=True)
    # assemble query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        # discarding nodes which similarity is below a certain threshold
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
    )

    end = datetime.now()
    # print the time it took to execute the script
    print(f"RAG time: {(end - start).total_seconds()}")

    return query_engine
