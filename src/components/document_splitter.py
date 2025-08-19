import logging
from typing import Dict, Any, List

from src.utils.api_client_manager import APIClientManager
from src.utils.json_parser import extract_json_from_response

logger = logging.getLogger("SetForge")

class DocumentSplitter:
    """
    Splits a document into logical chunks based on topics.
    """

    def __init__(self, api_manager: APIClientManager):
        """
        Initializes the DocumentSplitter.

        Args:
            api_manager: The API client manager.
        """
        self.api_manager = api_manager
        self.triage_prompt = self._load_triage_prompt()

    def _load_triage_prompt(self) -> str:
        """Loads the triage prompt from a file."""
        try:
            with open("src/prompts/triage_prompt.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            logger.error("Triage prompt not found at src/prompts/triage_prompt.txt")
            return "" # Return empty string if not found

    async def split_by_topic(self, content: str) -> List[Dict[str, Any]]:
        """
        Splits the document content into chunks based on topics using an LLM call.

        Args:
            content: The text content of the document.

        Returns:
            A list of dictionaries, where each dictionary represents a chunk
            with 'topic' and 'content' keys.
        """
        if not self.triage_prompt:
            logger.error("Cannot split document by topic: Triage prompt is missing.")
            return [{"topic": "general_info", "content": content}]

        prompt = self.triage_prompt.format(document_content=content)
        
        response_data = await self.api_manager.make_request(prompt)

        if not response_data or not response_data.get("success"):
            logger.warning("Failed to get a valid response from the triage model.")
            return [{"topic": "general_info", "content": content}]

        response_text = response_data.get("content", "")
        chunks = extract_json_from_response(response_text)
        
        if not chunks or not isinstance(chunks, list):
            logger.warning(f"Failed to decode chunks from triage model. Response: {response_text}")
            return [{"topic": "general_info", "content": content}]
            
        return chunks
