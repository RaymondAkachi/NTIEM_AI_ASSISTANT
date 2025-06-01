# from langchain_community.vectorstores import FAISS
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_core.documents import Document
# import numpy as np
# import os
# from dotenv import load_dotenv

# load_dotenv('.env')
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


# class OptimizedRAG:
#     def __init__(self, docs_dir="books"):
#         self.embeddings = OpenAIEmbeddings(
#             model="text-embedding-3-small",  # Cost-effective
#             show_progress_bar=False
#         )
#         self.vector_store = None
#         self.docs_dir = docs_dir
#         self._initialize()

#     def _initialize(self):
#         """Initialize with optimized parameters"""
#         if os.path.exists("general_vector_store"):
#             self._load_vector_store()
#         else:
#             self._process_documents()

#     def _process_documents(self):
#         """Efficient document processing pipeline"""
#         # 1. Smart Chunking
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=512,       # Optimized for dense retrieval
#             chunk_overlap=64,     # Balance context preservation
#             length_function=len,
#             is_separator_regex=False
#         )

#         # 2. Batch Processing with Progress
#         documents = self._load_documents()
#         chunks = text_splitter.split_documents(documents)

#         # 3. Quantized Embeddings
#         embeddings = self.embeddings.embed_documents(
#             [chunk.page_content for chunk in chunks],
#             chunk_size=128)       # Reduced dimensionality       # Optimized for API limits
#         # encoding_format="float",
#         # dimensions=512

#         # 4. Optimized FAISS Index
#         self.vector_store = FAISS.from_embeddings(
#             text_embeddings=list(zip(
#                 [chunk.page_content for chunk in chunks],
#                 embeddings
#             )),
#             embedding=self.embeddings,
#             normalize_L2=True  # Fast approximate search
#         )
#         self._save_vector_store()

#     def _load_documents(self):
#         """Memory-efficient document loading"""
#         from langchain_community.document_loaders import DirectoryLoader

#         return DirectoryLoader(
#             self.docs_dir,
#             glob="**/*.txt",  # Focus on markdown first was "**/*.md but changed it to **/*.txt"
#             use_multithreading=True,
#             max_concurrency=os.cpu_count(),
#             show_progress=True
#         ).load()

#     def _save_vector_store(self):
#         """Compressed storage"""
#         self.vector_store.save_local(
#             folder_path="general_vector_store",
#             index_name="optimized_index"
#         )

#     def _load_vector_store(self):
#         """Fast loading of precomputed index"""
#         self.vector_store = FAISS.load_local(
#             folder_path="general_vector_store",
#             embeddings=self.embeddings,
#             index_name="optimized_index",
#             allow_dangerous_deserialization=False
#         )

#     def retrieve(self, query: str, k=3, score_threshold=0.65):
#         """Efficient hybrid retrieval"""
#         # 1. Query Expansion
#         expanded_query = self._expand_query(query)

#         # 2. Pruned Vector Search
#         vector_results = self.vector_store.similarity_search_with_score(
#             expanded_query,
#             k=k*2,  # Over-fetch for pruning
#             filter=None,
#             search_type="similarity"
#         )

#         # 3. Result Pruning
#         filtered = [doc for doc,
#                     score in vector_results if score >= score_threshold]

#         # 4. Diversity Sampling
#         return self._max_marginal_relevance(filtered, final_k=k)

#     def _expand_query(self, query: str) -> str:
#         """Generate alternative query formulations"""
#         # Implement query expansion logic or use LLM
#         return query + " " + query.replace(" ", " OR ")

#     def _max_marginal_relevance(self, results, final_k=3):
#         """Ensure diverse results"""
#         return sorted(
#             results,
#             # Balance relevance and diversity
#             key=lambda x: (x[1], -abs(x[1] - 0.5)),
#         )[:final_k]


# # Usage
# rag = OptimizedRAG()
# results = rag.retrieve("How did juliet die")

import httpx
import asyncio


async def text_response(number, text):
    url = "https://graph.facebook.com/v22.0/634136199777636/messages"
    headers = {
        "Authorization": "Bearer EAAMzcBIJtngBOyFZBiMZBH0GnacrALWRADQmZCkso9XIwaSJHQhg8J68CNKxB5v8OHZBWs7WEpriZBPSMRbbwvCEioxDRIfJTIxGPO7a8TktBCl3ZC4uUdYqiCa0d9jcjxz4U6TZB0017DPcixW8xhiqQoZAEC1V7gg0vcnZCvaSuadT4I46G4K285ZBeiVHXbj9NfnQZDZD",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(number),
        "type": "text",
        "text": {"body": str(text)}
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise
        except Exception as e:
            print("An erro has occured: e")

        response.raise_for_status()
        upload_data = response.json()
        return upload_data

# result = asyncio.run(text_response('2349094540644', "Hello there!"))
# print(result)

rest = [{'hello': 'there', "tooso": 'your namae'},
        {"hello": 'there', 'what_is': 'your name?'}]
for i in rest:
    print(i['hello'])
