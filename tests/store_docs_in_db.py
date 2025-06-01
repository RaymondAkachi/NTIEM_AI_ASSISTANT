import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
# from langchain_community.vectorstores import Qdrant
import asyncio
from langchain.docstore.document import Document
from qdrant_client import AsyncQdrantClient, QdrantClient
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant, QdrantVectorStore
from dotenv import load_dotenv
# from qdrant_client import AsyncQdrantClient
# from langchain.docstore.document import Document
from qdrant_client.models import VectorParams, Distance
load_dotenv('.env')

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# current_dir = os.path.dirname(os.path.abspath(__file__))
# docs_dir = os.path.join(current_dir, "church_documents")

# if not os.path.exists(docs_dir):
#     raise FileNotFoundError(
#         f"The directory {docs_dir} does not exist. Please check the path."
#     )

# book_files = [f for f in os.listdir(docs_dir) if f.endswith(".txt")]

# documents = []
# for doc_file in book_files:
#     file_path = os.path.join(docs_dir, doc_file)
#     loader = TextLoader(file_path, encoding="utf-8")
#     book_docs = loader.load()
#     for doc in book_docs:
#         # Add metadata to each document indicating its source
#         doc.metadata = {"source": doc_file}
#         documents.append(doc)

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=250, chunk_overlap=50)
# docs = text_splitter.split_documents(documents)

# # Display information about the split documents
# print("\n--- Document Chunks Information ---")
# print(f"Number of document chunks: {len(docs)}")

# # Create embeddings
# print("\n--- Creating embeddings ---")
# # Update to a valid embedding model if needed
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
# print("\n--- Finished creating embeddings ---")

# # Create the vector store and persist it
# print("\n--- Creating and persisting vector store ---")

# e.g., "https://your-cluster-id.qdrant.io"
QDRANT_URL = 'https://19df3277-f7fe-4676-95aa-8a9b7fe1568e.eu-west-2-0.aws.cloud.qdrant.io:6333'
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.K6P9M8eXXJmVl4rKMLqTc2L2EiSVs1InP78pe_J2Mws"
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
COLLECTION_NAME = "ntiem_document_collection"


async def create_collection():
    # Explicitly create the collection if it doesn't exist
    exists = await client.collection_exists(collection_name=COLLECTION_NAME)
    if not exists:
        await client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,  # Matches text-embedding-ada-002
                distance=Distance.COSINE
            )
        )
        print(f"Collection '{COLLECTION_NAME}' created successfully.")

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)


# async def add_docs():
#     await vector_store.aadd_documents(docs)
#     print("Documents added successfully!")


async def search_docs():
    # query = "christ is king"
    k = 5  # Number of results to return  # Metadata filter
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 3, 'fetch_k': 10}
    )
    # results = await retriever.ainvoke("Who is Apostle Uche Raymond")
    results = await vector_store.asimilarity_search("Can you book appoitments?", k=k)
    for doc in results:
        print(f"Content: {doc.page_content}, Metadata: {doc.metadata}")


# Step 7: Run the async functions
async def main():
    # await add_docs()
    await search_docs()
    pass

if __name__ == "__main__":
    asyncio.run(main())
# # asyncio.run(create_collection())
# # Set up Qdrant vector store
# vector_store = Qdrant(
#     client=client, collection_name=COLLECTION_NAME, embeddings=embeddings)

# # Add example documents
# docs = [
#     Document(page_content="Jesus is king", metadata={"source": "doc1"}),
#     Document(page_content="Jesus is lord", metadata={"source": "doc2"}),
# ]

# asyncio.run(vector_store.add_documents(docs))


# QDRANT_URL = 'https://19df3277-f7fe-4676-95aa-8a9b7fe1568e.eu-west-2-0.aws.cloud.qdrant.io:6333'
# QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.K6P9M8eXXJmVl4rKMLqTc2L2EiSVs1InP78pe_J2Mws"
# async_client = AsyncQdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
# client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
# COLLECTION_NAME = "ntiem_document_collection"

# Step 1: Create the AsyncQdrantClient
# async_client = AsyncQdrantClient(url="http://localhost:6333")  # Adjust URL as needed

# Step 2: Set up embeddings
# Replace with your embedding model
# embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# # Step 3: Initialize Qdrant vector store
# vector_store = Qdrant(
#     client=client,
#     async_client=async_client,
#     collection_name=COLLECTION_NAME,  # Replace with your collection name
#     embeddings=embeddings,
# )

# vector_store = QdrantVectorStore(
#     client=client,
#     collection_name=COLLECTION_NAME,
#     embedding=embeddings,
# )

# Step 4: Prepare documents
# documents = [
#     Document(page_content="Jesus Christ is king", metadata={"source": "doc1"}),
#     Document(page_content="Jesus Christ is Lord.",
#              metadata={"source": "doc2"}),
# ]
# documents = [
#     Document(page_content="Jesus Christ is my God",
#              metadata={"source": "doc3"})
# ]
# Step 5: Add documents asynchronously


# Step 6: Perform advanced search asynchronously
