# Start by making sure the `assemblyai` package is installed.
# If not, you can install it by running the following command:
# pip install -U assemblyai

# Note: Some macOS users may need to use `pip3` instead of `pip`.

# import assemblyai as aai

# # Replace with your API key
# aai.settings.api_key = "f16b132ff9384d2b9d546aeffe1ea5e1"

# # URL of the file to transcribe
# FILE_URL = "voices\my_akachi_vn.aac"

# # You can also transcribe a local file by passing in a file path
# # FILE_URL = './path/to/file.mp3'

# transcriber = aai.Transcriber()
# transcript = transcriber.transcribe(FILE_URL)

# if transcript.status == aai.TranscriptStatus.error:
#     print(transcript.error)
# else:
#     print(transcript.text)

# import assemblyai as aai
# import time
# import aiohttp
# import asyncio
# import time

# # a = time.time()
# # aai.settings.api_key = "f16b132ff9384d2b9d546aeffe1ea5e1"

# # audio_url = "voices\my_akachi_vn.aac"

# # # config = aai.TranscriptionConfig(language_detection=True)
# # config = aai.TranscriptionConfig()

# # transcriber = aai.Transcriber(config=config)

# # transcript = transcriber.transcribe(audio_url)
# # b = time.time()
# # diff = a - b

# # print("Time taken: ", diff)
# # print(transcript.text)

# # Transcribe with AssemblyAI
# import aiohttp
# import asyncio

# ASSEMBLYAI_API_KEY = "f16b132ff9384d2b9d546aeffe1ea5e1"


# async def transcribe_web_audio(audio_url):
#     async with aiohttp.ClientSession() as session:
#         transcript_response = await session.post(
#             "https://api.assemblyai.com/v2/transcript",
#             headers={"authorization": ASSEMBLYAI_API_KEY},
#             json={"audio_url": audio_url}
#         )
#         transcript_data = await transcript_response.json()
#         transcript_id = transcript_data["id"]

#         while True:
#             result_response = await session.get(
#                 f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
#                 headers={"authorization": ASSEMBLYAI_API_KEY}
#             )
#             result_data = await result_response.json()

#             if result_data["status"] == "completed":
#                 return [result_data["text"], result_data["language_code"]]
#             elif result_data["status"] == "error":
#                 return None
#             await asyncio.sleep(5)

# # Example usage:


# async def main():
#     a = time.time()
#     # replace with a real url.
#     web_audio_url = "https://assembly.ai/wildfires.mp3"
#     # web_audio_url = "voices\my_akachi_vn.aac"
#     transcription = await transcribe_web_audio(web_audio_url)
#     b = time.time()
#     diff = b - a
#     print("Time taken: ", diff)
#     if transcription:
#         print("Transcription text:", transcription[0])
#         print("Transcription lanmguage code:", transcription[1])
#     else:
#         print("Transcription failed.")

# if __name__ == "__main__":
#     asyncio.run(main())

import aiohttp
import asyncio
import time

# Replace with your AssemblyAI API key
API_KEY = "f16b132ff9384d2b9d546aeffe1ea5e1"
BASE_URL = "https://api.assemblyai.com/v2"


async def submit_transcription_request(session, audio_url: str):
    """Submit an audio file for transcription to AssemblyAI."""
    headers = {
        "authorization": API_KEY,
        "content-type": "application/json"
    }
    payload = {
        "audio_url": audio_url,
        "language_detection": True
    }
    async with session.post(f"{BASE_URL}/transcript", headers=headers, json=payload) as response:
        if response.status == 200:
            data = await response.json()
            return data["id"]
        else:
            raise Exception(f"Failed to submit transcription: {response.status} - {await response.text()}")


async def poll_transcription_result(session, transcript_id):
    """Poll the transcription result until it’s ready."""
    headers = {"authorization": API_KEY}
    while True:
        async with session.get(f"{BASE_URL}/transcript/{transcript_id}", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data["status"] == "completed":
                    return data["text"]
                elif data["status"] == "failed":
                    raise Exception(f"Transcription failed: {data['error']}")
                else:
                    # Wait 5 seconds before polling again
                    await asyncio.sleep(5)
            else:
                raise Exception(f"Failed to poll transcription: {response.status} - {await response.text()}")


async def async_transcribe(audio_url, semaphore):
    """Transcribe an audio file asynchronously."""
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            try:
                transcript_id = await submit_transcription_request(session, audio_url)
                transcription = await poll_transcription_result(session, transcript_id)
                return transcription
            except Exception as e:
                return str(e)  # Return error as string for simplicity


async def main():
    """Main function to transcribe audio files concurrently."""
    # Example list of audio URLs (replace with your own)
    # Add more URLs as needed
    # "https://assembly.ai/wildfires.mp3",
    audio_urls = ["https://ntiembotbucket.s3.eu-north-1.amazonaws.com/audio/response_1743262057.mp3"]
    start_time = time.time()

    # Semaphore to limit concurrent requests (adjust based on API limits)
    semaphore = asyncio.Semaphore(5)

    # Create tasks for each audio URLs
    tasks = [async_transcribe(url, semaphore) for url in audio_urls]

    # Run tasks concurrently and gather results
    results = await asyncio.gather(*tasks)

    end_time = time.time()

    # Display results
    print("Transcription Results:")
    for url, result in zip(audio_urls, results):
        print(f"- {url}: {result}")

    print(f"Total time taken: {end_time - start_time:.2f} seconds")

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
