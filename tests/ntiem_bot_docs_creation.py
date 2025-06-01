# from qdrant_client import AsyncQdrantClient, QdrantClient
# from qdrant_client.models import VectorParams, Distance
# import asyncio

# QDRANT_URL = 'https://19df3277-f7fe-4676-95aa-8a9b7fe1568e.eu-west-2-0.aws.cloud.qdrant.io:6333'
# QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.K6P9M8eXXJmVl4rKMLqTc2L2EiSVs1InP78pe_J2Mws"
# # client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
# client = AsyncQdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
# COLLECTION_NAME = "ntiem_bot_docs"


# async def create_collection():
#     # Explicitly create the collection if it doesn't exist
#     exists = await client.collection_exists(collection_name=COLLECTION_NAME)
#     if not exists:
#         await client.create_collection(
#             collection_name=COLLECTION_NAME,
#             vectors_config=VectorParams(
#                 size=1536,  # Matches text-embedding-ada-002
#                 distance=Distance.COSINE
#             )
#         )
#         print(f"Collection '{COLLECTION_NAME}' created successfully.")


# print(asyncio.run(create_collection()))


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
from langchain.docstore.document import Document
from qdrant_client.models import VectorParams, Distance
load_dotenv('.env')

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# current_dir = os.path.dirname(os.path.abspath(__file__))
# docs_dir = os.path.join(current_dir, "ntiem_bot_docs_files")

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
#     chunk_size=700, chunk_overlap=300)
# docs = text_splitter.split_documents(documents)

# # Display information about the split documents
# print("\n--- Document Chunks Information ---")
# print(f"Number of document chunks: {len(docs)}")

# # Create embeddings
# print("\n--- Creating embeddings ---")
# Update to a valid embedding model if needed
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
# print("\n--- Finished creating embeddings ---")

# # Create the vector store and persist it
# print("\n--- Creating and persisting vector store ---")

# e.g., "https://your-cluster-id.qdrant.io"
QDRANT_URL = 'https://19df3277-f7fe-4676-95aa-8a9b7fe1568e.eu-west-2-0.aws.cloud.qdrant.io:6333'
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.K6P9M8eXXJmVl4rKMLqTc2L2EiSVs1InP78pe_J2Mws"
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
COLLECTION_NAME = "ntiem_bot_docs"


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
    k = 3  # Number of results to return  # Metadata filter
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 3, 'fetch_k': 10}
    )
    # results = await vector_store.asimilarity_search(query="Can you book appointments?", k=7)
    # results = await retriever.ainvoke("Can you book appointments")
    results = await vector_store.asimilarity_search("Can you book appointments", k=k)
    for doc in results:
        print(f"Content: {doc.page_content}, Metadata: {doc.metadata}")


# Step 7: Run the async functions
async def main():
    try:
        # await add_docs()
        await search_docs()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())


# from dotenv import load_dotenv
# from langchain_core.output_parsers import StrOutputParser
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.prompts import PromptTemplate
# from langchain_core.messages import HumanMessage, AIMessage
# from langchain_core.runnables import RunnableConfig
# import asyncio

# load_dotenv('.env')

# contextualize_q_system_prompt = (
#     """Given a chat history and the latest user input, reformulate the user input to be standalone by incorporating any necessary context from the chat history, while preserving its original form as a statement or a question. If the user input is a statement, ensure the reformulated output is also a statement. If it is a question, ensure the reformulated output is a question. Do not answer the input. If the input is already standalone and does not reference the chat history, return it as is.

# Examples:

# Chat History: [Human: What day is today? AI: Today is Thursday.]
# User Input: I need prayer for marriage.
# Reformulated Output: I need prayer for marriage.
# Chat History: [Human: I need prayer. AI: Contact our prayer team.]
# User Input: For marriage.
# Reformulated Output: I need prayer for marriage.
# Chat History: [Human: What is the weather like? AI: It’s sunny.]
# User Input: What about tomorrow?
# Reformulated Output: What is the weather like tomorrow?"""
# )
# contextualize_q_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", contextualize_q_system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ]
# )

# llm_1 = ChatOpenAI(model="gpt-3.5-turbo-0125")
# history_aware_chain = contextualize_q_prompt | llm_1 | StrOutputParser()

# chat_history = ["Human: What day is today", "AI: Today is Thursday", "Human: What about tomorrow",
#                 "AI: Tomorrow will Friday", "Human: Elon Musk age?", "AI: Elon Musk age is 47"]

# prompt_template = """
# **Instructions:**
# Given a user's question, rewrite it according to the following rules:

# 1. **Church-Related Questions:**
#    - If the question is about a church or ministry(e.g., asking about service times, location, events, mission) and does *not* mention a specific church name, rewrite it to refer to "New Testament International Evangelical Ministry."
#    - If the question already mentions a specific church name (e.g., "Dance Battle Church," "First Baptist Church"), leave it unchanged.

# 2. **Leadership-Related Questions:**
#    - If the question refers to a leadership role (e.g., "leader," "Apostle," "founder," "supervisor," "pastor") and does *not* include a specific person's name, rewrite it to refer to "Apostle Uche Raymond" as the subject, incorporating his role and the church name "New Testament International Evangelical Ministry" for context.
#    - If the question already includes a specific person's name (e.g., "Pastor John," "Reverend Smith"), leave it unchanged.

# **Additional Guidelines:**
# - Maintain the form of a question in the rewritten output.
# - Do not answer the question; only rewrite it according to the rules.
# - Provide only the rewritten question as output, without additional text.

# **Examples:**
# - **Input:** "What are the service times?"
#   **Output:** "What are the service times at New Testament International Evangelical Ministry?"
# - **Input:** "What are the service times at Battle Church?"
#   **Output:** "What are the service times at Battle Church?"
# - **Input:** "Who is the leader?"
#   **Output:** "Who is Apostle Uche Raymond"
# - **Input:** "What is the founder's vision?"
#   **Output:** "What is Apostle Uche Raymond's vision as the founder of New Testament International Evangelical Ministry?"
# - **Input:** "Tell me about Pastor John."
#   **Output:** "Tell me about Pastor John."
# - **Input:** "Who is the founder of John Wick"
#   **Output:** "Who is the founder of John Wick."
# - **Input:** "Who is the founder"
#   **Output:** "Who is Apostle Uche Raymond"
# **User Question:**
# {user_question}

# **Rewritten Question:**
# """


# # Create the PromptTemplate
# prompt = PromptTemplate(
#     input_variables=["user_question"],
#     template=prompt_template
# )

# # Initialize the language model (replace with your actual LLM and configuration)
# # Using OpenAI as an example; adjust as needed
# llm_2 = ChatOpenAI(model="gpt-3.5-turbo")

# # Create the LLMChain
# query_rewriter_chain = prompt | llm_2 | StrOutputParser()

# chain_comb = history_aware_chain | query_rewriter_chain
# # result = chain_comb.invoke({"chat_history": chat_history, "input": "Who is the founder of the ministry"})


# async def get_result(user_input):
#     config = RunnableConfig(configurable={})
#     result = await chain_comb.ainvoke({'chat_history': chat_history, "input": user_input}, config)
#     return result

# print(asyncio.run(get_result("What the names of his kids")))
