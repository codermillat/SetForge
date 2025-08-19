import logging
from typing import Dict, Any, List

logger = logging.getLogger("SetForge")

class KnowledgeAggregator:
    """
    Aggregates structured data chunks into a single, coherent knowledge unit.
    """

    def aggregate(self, structured_chunks: List[Dict[str, Any]], original_filename: str) -> Dict[str, Any]:
        """
        Merges structured data from different topic chunks.

        Args:
            structured_chunks: A list of structured data dictionaries, one for each topic.
            original_filename: The name of the original source file.

        Returns:
            A single dictionary representing the aggregated knowledge.
        """
        final_data: Dict[str, Any] = {
            "source_file": original_filename,
            "structured_data": {}
        }

        for chunk in structured_chunks:
            # The topic is the first key in the chunk dict
            topic = next(iter(chunk))
            final_data["structured_data"][topic] = chunk[topic]
            
        logger.info(f"Aggregated {len(structured_chunks)} chunks for {original_filename}")
        return final_data
