#!/usr/bin/env python3
"""
SetForge Kaggle Inference Client
Client for interacting with the remote Kaggle inference server.
"""

import httpx
import json
from logging import Logger
from typing import Optional, Dict, Any

class KaggleInferenceClient:
    """
    A client to communicate with the FastAPI server running on a Kaggle kernel.
    Handles sending prompts and receiving generated responses.
    """

    def __init__(self, server_url: str, logger: Logger, timeout: int = 120):
        """
        Initializes the client with the server URL.

        Args:
            server_url (str): The public ngrok URL of the Kaggle inference server.
            logger (Logger): The logger instance for logging messages.
            timeout (int): The timeout in seconds for HTTP requests.
        """
        if not server_url or not server_url.startswith("https://"):
            raise ValueError("A valid HTTPS ngrok server URL must be provided.")
        
        self.base_url = server_url.rstrip('/')
        self.generate_url = f"{self.base_url}/generate"
        self.logger = logger
        self.timeout = timeout

    async def generate(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Sends a prompt to the /generate endpoint and gets the model's response.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            Optional[Dict[str, Any]]: The JSON response from the server, or None if an error occurs.
        """
        self.logger.debug(f"Sending prompt to Kaggle server at {self.generate_url}")
        
        payload = {"prompt": prompt}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.generate_url, json=payload)
                
                response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
                
                response_data = response.json()
                self.logger.debug(f"Received response: {response_data}")
                
                return response_data

        except httpx.HTTPStatusError as e:
            self.logger.error(f"❌ HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            self.logger.error(f"❌ An error occurred while requesting {e.request.url!r}: {e}")
            return None
        except json.JSONDecodeError:
            self.logger.error("❌ Failed to decode JSON response from server.")
            return None
        except Exception as e:
            self.logger.error(f"❌ An unexpected error occurred in the Kaggle client: {e}", exc_info=True)
            return None

    async def is_server_alive(self) -> bool:
        """
        Checks if the inference server is running and accessible.
        FastAPI typically has a /docs endpoint available.
        """
        health_check_url = f"{self.base_url}/docs"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(health_check_url)
                if response.status_code == 200:
                    self.logger.info("✅ Kaggle inference server is alive and reachable.")
                    return True
                else:
                    self.logger.warning(f"⚠️ Server responded with status {response.status_code} on health check.")
                    return False
        except httpx.RequestError as e:
            self.logger.error(f"❌ Could not connect to Kaggle server for health check: {e}")
            return False
