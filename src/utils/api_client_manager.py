#!/usr/bin/env python3
"""
SetForge API Client Manager
A sophisticated, resilient, and rate-limited client for managing multiple LLM APIs.
"""

import asyncio
import time
from collections import deque
from typing import List, Dict, Any, Optional, TypedDict
from logging import Logger
import aiohttp
import vertexai
from vertexai.generative_models import GenerativeModel
from google.api_core import exceptions as google_exceptions

from src.utils.config_manager import ConfigManager
from src.utils.rate_limiter import AsyncRateLimiter


class ClientConfig(TypedDict):
    """Strongly typed dictionary for an API client's configuration."""
    name: str
    provider: str
    model: str
    api_key: str
    tier: str
    rate_limiter: AsyncRateLimiter
    tpm_limiter: AsyncRateLimiter
    project_id: Optional[str]

class ResponseData(TypedDict):
    """Strongly typed dictionary for the response from the API."""
    success: bool
    content: str
    model_used: str


class APIClientManager:
    """
    Manages a pool of API clients, handling intelligent rotation, rate limiting,
    and tiered access to maximize throughput and cost-effectiveness.
    """

    def __init__(self, config: ConfigManager, logger: Logger):
        self.config = config
        self.logger = logger
        self.clients = self._initialize_clients()
        self.session = aiohttp.ClientSession()
        self.cool_down_times: Dict[str, float] = {}
        self.client_queue = deque(self.clients)

    def _initialize_clients(self) -> List[ClientConfig]:
        """Load and initialize API clients from the configuration."""
        clients: List[ClientConfig] = []
        api_providers: List[Dict[str, Any]] = self.config.get('api_providers', [])
        if not api_providers:
            self.logger.warning("No API providers configured in config.yaml.")
            return []

        for provider_config in api_providers:
            client: ClientConfig = {
                'name': provider_config.get('name', 'default-client'),
                'provider': provider_config.get('provider', 'unknown'),
                'model': provider_config.get('model', 'default-model'),
                'api_key': provider_config.get('api_key', ''),
                'tier': provider_config.get('tier', 'free'),
                'rate_limiter': AsyncRateLimiter(
                    max_calls=provider_config.get('rpm', 10),
                    period=60
                ),
                'tpm_limiter': AsyncRateLimiter(
                    max_calls=provider_config.get('tpm', 100000),
                    period=60
                ),
                'project_id': provider_config.get('project_id')
            }
            clients.append(client)
            self.logger.info(f"Initialized API client: {client['name']} ({client['tier']} tier)")
        
        # Prioritize paid tier clients
        clients.sort(key=lambda x: x.get('tier') == 'paid', reverse=True)
        return clients

    async def get_available_client(self) -> Optional[ClientConfig]:
        """
        Finds the next available client that is not rate-limited.
        Implements a round-robin strategy with a cool-down period.
        """
        for _ in range(len(self.client_queue)):
            client = self.client_queue[0]
            client_name = client.get('name')
            
            if client_name and time.time() < self.cool_down_times.get(client_name, 0):
                self.client_queue.rotate(-1)
                continue

            rate_limiter = client.get('rate_limiter')
            tpm_limiter = client.get('tpm_limiter')
            if rate_limiter and tpm_limiter and rate_limiter.can_make_request() and tpm_limiter.can_make_request():
                self.logger.debug(f"Selected available client: {client_name}")
                self.client_queue.rotate(-1)
                return client
            
            self.client_queue.rotate(-1)
        
        self.logger.warning("All API clients are currently rate-limited or in cool-down. Waiting...")
        await asyncio.sleep(5)
        return await self.get_available_client()

    async def make_request(self, prompt: str) -> Optional[ResponseData]:
        """
        Makes a request to an available LLM API, handling intelligent client rotation and fallbacks.
        The primary retry logic is handled by the calling pipeline.
        """
        if not self.clients:
            self.logger.error("Cannot make request: No API clients are configured.")
            return None

        client = await self.get_available_client()
        if not client:
            self.logger.error("No available clients to make a request.")
            return None

        client_name = client.get('name', 'unknown-client')
        try:
            async with client['rate_limiter'], client['tpm_limiter']:
                self.logger.info(f"Attempting request with {client_name} ({client.get('provider')})...")
                provider = client.get('provider')

                if provider == 'vertex_ai':
                    response_data = await self._make_vertex_request(client, prompt)
                elif provider == 'google_ai_studio':
                    response_data = await self._make_studio_request(client, prompt)
                else:
                    self.logger.error(f"Unknown provider for client {client_name}: {provider}")
                    return None

                if response_data and response_data.get("success"):
                    self.logger.info(f"Successfully received response from {client_name}.")
                else:
                    self.logger.warning(f"Request with {client_name} failed. Response: {response_data}.")
                
                return response_data

        except aiohttp.ClientResponseError as e:
            wait_time = 60  # Default cool-down
            if e.status == 429: # Too Many Requests
                if e.headers and (retry_after := e.headers.get("Retry-After")):
                    try:
                        wait_time = int(retry_after)
                        self.logger.warning(f"Rate limit hit for {client_name}. Respecting 'Retry-After' header. Cooling down for {wait_time}s.")
                    except ValueError:
                        self.logger.warning(f"Could not parse 'Retry-After' header: {retry_after}. Using default cool-down.")
                else:
                    self.logger.warning(f"Rate limit hit for {client_name} with no 'Retry-After' header. Using default cool-down.")
            else:
                 self.logger.warning(f"HTTP error for {client_name}. Using default cool-down. Error: {e}")

            self.cool_down_times[client_name] = time.time() + wait_time
            raise e # Re-raise to be caught by the pipeline's retry logic

        except google_exceptions.ResourceExhausted as e:
            self.logger.warning(f"API error for {client_name}. Placing it in cool-down. Error: {e}")
            self.cool_down_times[client_name] = time.time() + 60 # 60-second cool-down
            raise e # Re-raise to be caught by the pipeline's retry logic
        
        except Exception as e:
            self.logger.error(f"An unexpected error occurred with {client_name}: {e}. Trying next client.", exc_info=True)
            raise e # Re-raise for the pipeline to handle

    async def _make_vertex_request(self, client: ClientConfig, prompt: str) -> Optional[ResponseData]:
        """Handles API requests to Google Cloud Vertex AI using ADC."""
        project_id = client.get('project_id')
        model_name = client.get('model')
        client_name = client.get('name')

        if not project_id or not model_name:
            self.logger.error(f"Vertex AI client '{client_name}' is missing 'project_id' or 'model' in config.")
            return None

        try:
            # Initialize Vertex AI for this project.
            # This relies on Application Default Credentials.
            vertexai.init(project=project_id)
            
            model = GenerativeModel(model_name)
            
            # The SDK's generate_content_async handles the async call
            response = await model.generate_content_async(prompt)
            
            content = response.text
            return ResponseData(success=True, content=content, model_used=model_name)

        except google_exceptions.ResourceExhausted as e:
            self.logger.warning(f"Vertex AI resource exhausted for {client_name}: {e}")
            raise  # Re-raise to be caught by the main request loop
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during Vertex AI request for {client_name}: {e}", exc_info=True)
            return ResponseData(success=False, content=str(e), model_used=model_name or "unknown")


    async def _make_studio_request(self, client: ClientConfig, prompt: str) -> Optional[ResponseData]:
        """Handles API requests to Google AI Studio."""
        model = client.get('model')
        api_key = client.get('api_key')
        client_name = client.get('name')

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 429:
                    self.logger.warning(f"Rate limit hit for {client_name}. Raising ClientResponseError.")
                    response.raise_for_status()

                if response.status >= 400:
                    error_text = await response.text()
                    self.logger.error(f"Google AI Studio request failed for {client_name} with status {response.status}: {error_text}")
                    return ResponseData(success=False, content=error_text, model_used=model or "unknown")

                json_response = await response.json()
                
                # Check for empty or malformed response
                if not json_response.get("candidates"):
                    self.logger.warning(f"Malformed response from {client_name}: No 'candidates' field. Response: {json_response}")
                    return ResponseData(success=False, content="Malformed response from API.", model_used=model or "unknown")

                content = json_response["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return ResponseData(success=True, content=content, model_used=model or "unknown")
        except aiohttp.ClientResponseError as e:
            # This will now catch the 429 and other client errors
            raise e
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during Google AI Studio request for {client_name}: {e}", exc_info=True)
            return ResponseData(success=False, content=str(e), model_used=model or "unknown")


    async def close_session(self):
        """Closes the aiohttp client session."""
        await self.session.close()
        self.logger.info("API Client Manager session closed.")
