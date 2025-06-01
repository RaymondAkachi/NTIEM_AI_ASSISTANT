from fastapi import FastAPI
import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

# Replace with your AssemblyAI API key
# API_KEY = "f16b132ff9384d2b9d546aeffe1ea5e1"
# BASE_URL = "https://api.assemblyai.com/v2"


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Load the ML model
#     logging.info("Application starting now")
#     asyncio.create_task(process_batch())
#     yield
#     # Clean up the ML models and release the resources
#     logging.info("Application shutting down")

# app = FastAPI(lifespan=lifespan)

# # Define request and response models


# class TranscriptionRequest(BaseModel):
#     audio_url: str


# class TranscriptionResponse(BaseModel):
#     text: str


# # Queue to hold incoming requests
# request_queue = asyncio.Queue()
# # Dictionary to store futures for each request
# futures: Dict[str, asyncio.Future] = {}


# async def submit_transcription(session, audio_urls):
#     """Submit a batch of audio URLs to AssemblyAI."""
#     headers = {
#         "authorization": API_KEY,
#         "content-type": "application/json"
#     }
#     payload = {"audio_urls": audio_urls}
#     async with session.post(f"{BASE_URL}/transcripts", headers=headers, json=payload) as response:
#         if response.status == 200:
#             data = await response.json()
#             return data["id"]
#         else:
#             raise Exception(f"Submission failed: {await response.text()}")


# async def poll_transcription(session, transcript_id):
#     """Poll until transcription is complete."""
#     headers = {"authorization": API_KEY}
#     while True:
#         async with session.get(f"{BASE_URL}/transcript/{transcript_id}", headers=headers) as response:
#             if response.status == 200:
#                 data = await response.json()
#                 if data["status"] == "completed":
#                     return data["transcripts"]
#                 elif data["status"] == "failed":
#                     raise Exception(f"Transcription failed: {data['error']}")
#                 await asyncio.sleep(5)  # Wait before polling again
#             else:
#                 raise Exception(f"Polling failed: {await response.text()}")


# async def process_batch():
#     """Process batched requests every 3 seconds."""
#     while True:
#         await asyncio.sleep(3)  # Wait 3 seconds to collect requests
#         if not request_queue.empty():
#             batch_urls = []
#             while not request_queue.empty():
#                 url, future = await request_queue.get()
#                 batch_urls.append(url)
#                 futures[url] = future

#             async with aiohttp.ClientSession() as session:
#                 try:
#                     transcript_id = await submit_transcription(session, batch_urls)
#                     results = await poll_transcription(session, transcript_id)
#                     for url, result in zip(batch_urls, results):
#                         future = futures.pop(url)
#                         future.set_result(result["text"])
#                 except Exception as e:
#                     for url in batch_urls:
#                         future = futures.pop(url)
#                         future.set_exception(e)

# # @app.on_event("startup")
# # async def startup_event():
# #     """Start the batch processor when the app starts."""
# #     asyncio.create_task(process_batch())


# @app.post("/transcribe", response_model=TranscriptionResponse)
# async def transcribe_audio(request: TranscriptionRequest):
#     """Endpoint to transcribe audio URLs with batching."""
#     future = asyncio.Future()
#     await request_queue.put((request.audio_url, future))
#     try:
#         result = await future
#         return TranscriptionResponse(text=result)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# from fastapi import FastAPI
# from pydantic import BaseModel
# # import openai
# # from sklearn.metrics.pairwise import cosine_similarity
# # import os
# from contextlib import asynccontextmanager
# import logging


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Load the ML model
#     logging.info("Application starting now")
#     John_wick = 1
#     yield
#     # Clean up the ML models and release the resources
#     logging.info("Application shutting down")

# app = FastAPI(lifespan=lifespan)
# # Initialize FastAPI app

# # Define department keywords (static data)
# # department_keywords = {
# #     "HR": "hiring employee benefits payroll",
# #     "IT": "computer software hardware network",
# #     "Sales": "customer order product delivery"
# # }

# # # Global dictionary to store precomputed embeddings
# # department_embeddings = {}

# # # Configure OpenAI API key (preferably from environment variables)
# # openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# # # Startup event to precompute department embeddings
# # @app.lifespan("startup")
# # async def startup_event():
# #     """Compute and store embeddings for department keywords when the app starts."""
#     # for dept, keywords in department_keywords.items():
#     #     # Generate embedding for the department keywords
#     #     response = openai.Embedding.create(
#     #         input=keywords,
#     #         model="text-embedding-ada-002"  # Example model
#     #     )
#     #     embedding = response["data"][0]["embedding"]
#     #     department_embeddings[dept] = embedding
#     # print("Department embeddings precomputed:", list(department_embeddings.keys()))

# # Pydantic model for request body
# class QuestionRequest(BaseModel):
#     question: str

# # API endpoint to route user questions
# @app.post("/route")
# async def route_question(request: QuestionRequest):
#     # """Route the user's question to the most similar department."""
#     # # Embed the user's question
#     # response = openai.Embedding.create(
#     #     input=request.question,
#     #     model="text-embedding-ada-002"
#     # )
#     # question_embedding = response["data"][0]["embedding"]

#     # # Compute similarity with each department's embedding
#     # similarities = {}
#     # for dept, dept_embedding in department_embeddings.items():
#     #     similarity = cosine_similarity([question_embedding], [dept_embedding])[0][0]
#     #     similarities[dept] = similarity

#     # # Find the department with the highest similarity
#     # best_dept = max(similarities, key=similarities.get)
#     # return {"department": best_dept, "similarity": similarities[best_dept]}
#     return {"John Wick": John_wick}


def fake_answer_to_everything_ml_model(x: float):
    return x * 42


ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/predict")
async def predict(x: float):
    result = ml_models["answer_to_everything"](x)
    return {"result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
