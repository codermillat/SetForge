"""
Vertex AI Generator for SetForge
Utilizes the Vertex AI SDK for direct calls to Google's Gemini models.
"""

import os
import asyncio
import logging
import random
from typing import Optional

import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.api_core import exceptions

from src.utils.rate_limiter import AsyncRateLimiter

class VertexAIGenerator:
    """A generator that uses the Vertex AI SDK to call Gemini models."""

    def __init__(self, project_id: str, location: str, model_name: str, rate_limiter: AsyncRateLimiter):
        """
        Initializes the Vertex AI generator.

        Args:
            project_id: The Google Cloud project ID.
            location: The Google Cloud location for the model.
            model_name: The name of the Gemini model to use.
            rate_limiter: An instance of AsyncRateLimiter.
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.logger = logging.getLogger("SetForge")
        self.rate_limiter = rate_limiter
        
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            self.logger.info(f"✅ Vertex AI initialized successfully for model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Vertex AI: {e}", exc_info=True)
            self.model = None

    async def generate_text(self, prompt: str, retries: int = 5, backoff_factor: float = 2.5) -> Optional[str]:
        """
        Generates text using the configured Gemini model on Vertex AI with rate limiting and retries.

        Args:
            prompt: The text prompt to send to the model.
            retries: The number of times to retry on failure.
            backoff_factor: The factor by which to increase the backoff time for each retry.

        Returns:
            The generated text as a string, or None if generation fails.
        """
        if not self.model:
            self.logger.error("Vertex AI model is not initialized. Cannot generate text.")
            return None

        for attempt in range(retries):
            try:
                await self.rate_limiter.wait()
                
                response = await self.model.generate_content_async(
                    [Part.from_text(prompt)]
                )
                if response.candidates and response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text
                else:
                    self.logger.warning("Received an empty response from Vertex AI.")
                    return None
            
            except exceptions.ResourceExhausted as e:
                # Exponential backoff with jitter
                wait_time = (backoff_factor ** attempt) + random.uniform(0, 1)
                self.logger.warning(f"Rate limit exceeded. Retrying in {wait_time:.2f}s. (Attempt {attempt + 1}/{retries})")
                await asyncio.sleep(wait_time)
            
            except Exception as e:
                self.logger.error(f"❌ An error occurred during Vertex AI text generation: {e}", exc_info=True)
                return None
        
        self.logger.error(f"Failed to generate text after {retries} attempts.")
        return None

def create_vertex_ai_generator(rate_limiter: Optional[AsyncRateLimiter] = None) -> Optional[VertexAIGenerator]:
    """
    Factory function to create a VertexAIGenerator instance from environment variables.
    Initializes lazily.
    """
    project_id = os.getenv("VERTEX_AI_PROJECT")
    location = os.getenv("VERTEX_AI_LOCATION")
    model_name = os.getenv("VERTEX_AI_MODEL")

    if not all([project_id, location, model_name]):
        logging.warning("⚠️ Missing essential Vertex AI configuration (project, location, or model) in environment variables. Cannot create generator.")
        return None

    # If no rate limiter is provided, create a default one.
    if rate_limiter is None:
        rate_limiter = AsyncRateLimiter(max_calls=2000, period=60)

    return VertexAIGenerator(
        project_id=project_id,
        location=location,
        model_name=model_name,
        rate_limiter=rate_limiter
    )
