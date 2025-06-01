# print("Hello my name is akachi raymond and i am also the fastst guy in the world")\
import base64
import aiohttp
import asyncio
import logging
from typing import Union, List
from together import Together
import os
from uuid import uuid4

# Optional: Configure logging to see output
logging.basicConfig(level=logging.INFO)


class TogetherImageGenerator:
    """
    A client for generating images using the Together API asynchronously.

    Attributes:
        api_key (str): The API key for authentication.
        base_url (str): The base URL of the Together API.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.
        logger (logging.Logger): Logger for the class.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.together.ai/v1", max_concurrency: int = 5):
        """
        Initialize the image generator with an API key.

        Args:
            api_key (str): The API key for authentication.
            base_url (str): The base URL of the Together API (default: "https://api.together.ai/v1").
            max_concurrency (int): Maximum number of concurrent requests (default: 5).

        Raises:
            ValueError: If the API key is not provided.
        """
        if not api_key:
            raise ValueError("API key must be provided")
        self.api_key = api_key
        self.base_url = base_url
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.logger = logging.getLogger(__name__)
        self.together_client = Together(api_key=self.api_key)

    # async def generate_image(self, prompt: str, model: str, width: int, height: int) -> bytes:
    #     """
    #     Generate an image asynchronously based on the provided prompt.

    #     Args:
    #         prompt (str): The text prompt to generate the image from.
    #         model (str): The model identifier for image generation.
    #         width (int): Desired width of the image in pixels.
    #         height (int): Desired height of the image in pixels.

    #     Returns:
    #         bytes: The generated image data.

    #     Raises:
    #         Exception: If the API request fails after retries.
    #     """
    #     url = f"{self.base_url}/images/generations"
    #     headers = {
    #         "Authorization": f"Bearer {self.api_key}",
    #         "Content-Type": "application/json"
    #     }
    #     payload = {
    #         "prompt": prompt,
    #         "model": model,
    #         "width": width,
    #         "height": height,
    #         "response_format": "b64_json"
    #     }

    #     retries = 3
    #     for attempt in range(retries):
    #         try:
    #             async with aiohttp.ClientSession() as session:
    #                 self.logger.info(f"Generating image for prompt: '{prompt}'")
    #                 async with session.post(url, json=payload, headers=headers) as response:
    #                     if response.status == 200:
    #                         image_data = await response.read()
    #                         self.logger.info(f"Image generated successfully for prompt: '{prompt}'")
    #                         return image_data
    #                     else:
    #                         error_detail = await response.text()
    #                         raise Exception(f"API error: {response.status} - {error_detail}")
    #         except Exception as e:
    #             if attempt < retries - 1:
    #                 self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in 1 second...")
    #                 await asyncio.sleep(1)
    #             else:
    #                 self.logger.error(f"Failed to generate image for prompt '{prompt}' after {retries} attempts: {e}")
    #                 raise e

    async def generate_image(self, prompt: str, output_path: str = "") -> bytes:
        """Generate an image from a prompt using Together AI."""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            self.logger.info(f"Generating image for prompt: '{prompt}'")

            response = self.together_client.images.generate(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell-Free",
                width=1024,
                height=768,
                steps=4,
                n=1,
                response_format="b64_json",
            )

            image_data = base64.b64decode(response.data[0].b64_json)

            with open(output_path, "wb") as f:
                f.write(image_data)
            self.logger.info(f"Image saved to {output_path}")

            return image_data

        except Exception as e:
            print(e)

    # async def generate_images(self, prompts: List[str], output_paths: List[str]) -> List[Union[bytes, Exception]]:
    #     """
    #     Generate multiple images concurrently based on the provided prompts.

    #     Args:
    #         prompts (list[str]): List of prompts to generate images for.
    #         model (str): The model to use for generation.
    #         width (int): Image width in pixels.
    #         height (int): Image height in pixels.

    #     Returns:
    #         list[Union[bytes, Exception]]: A list where each element is either the image data or an exception.
    #     """
    #     async def generate_with_semaphore(prompt, output_path):
    #         async with self.semaphore:
    #             return await self.generate_image(prompt, output_path)

    #     tasks = [generate_with_semaphore(prompt) for prompt in prompts]
    #     return await asyncio.gather(*tasks, return_exceptions=True)


async def single_image():
    generator = TogetherImageGenerator(
        "49d29ffd4bd6b87e7a652ef93e35c7d90eab9a16b47a0fdabaf5c168e9404eed")
    # image_data = await generator.generate_image(
    #     prompt="A cozy cabin in the woods",
    #     model="black-forest-labs/FLUX.1-schnell-Free",
    #     width=1024,
    #     height=768
    # )
    image_data = await generator.generate_image(
        prompt="Generate a realistic picture of a large majestic lion",
        output_path=f"single_image{str(uuid4())}.png"
    )

    # enhanced_image_data = base64.b64decode(image_data.data[0].b64_json)
    # with open("single_image.png", "wb") as f:
    #     f.write(enhanced_image_data)
    # print("Saved single_image.png")

asyncio.run(single_image())
