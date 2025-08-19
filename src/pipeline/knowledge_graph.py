#!/usr/bin/env python3
"""
SetForge Knowledge Graph
========================

This module is responsible for assembling structured data into a unified,
deduplicated knowledge graph.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("SetForge")

class KnowledgeGraph:
    """
    Builds and maintains a knowledge graph of extracted information.
    """

    def __init__(self):
        """
        Initializes the KnowledgeGraph.
        """
        self.graph: Dict[str, Any] = {}

    def update_graph(self, university_name: str, data: Dict[str, Any], category: str):
        """
        Updates the knowledge graph with new data.

        Args:
            university_name: The name of the university.
            data: The data to be added to the graph.
            category: The category of the data.
        """
        if university_name not in self.graph:
            self.graph[university_name] = self._create_university_node()

        university_node = self.graph[university_name]

        # Use category to place data in the correct part of the graph
        if category == "Fee_Structure" and "fee_structure" in university_node:
            university_node["fee_structure"].append(data)
        elif category == "Course_Details" and "course_catalog" in university_node:
            university_node["course_catalog"].append(data)
        elif category == "Scholarship_Policy" and "scholarship_policy" in university_node:
            university_node["scholarship_policy"].append(data)
        else:
            # For other categories, merge data at the top level
            university_node.update(data)

        self._deduplicate_lists(university_node)

    def _create_university_node(self) -> Dict[str, Any]:
        """Creates a new, empty node for a university."""
        return {
            "fee_structure": [],
            "scholarship_policy": [],
            "course_catalog": [],
            "eligibility_criteria": [],
            "contact_information": {}
        }

    def _deduplicate_lists(self, node: Dict[str, Any]):
        """Deduplicates lists within a graph node."""
        for key, value in node.items():
            if isinstance(value, list) and value:
                # Simple deduplication based on converting dicts to tuples
                try:
                    unique_items = {tuple(sorted(d.items())) for d in value if isinstance(d, dict)}
                    node[key] = [dict(t) for t in unique_items]
                except TypeError:
                    # Fallback for non-hashable items
                    pass

    def get_university_data(self, university_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves all data for a specific university.

        Args:
            university_name: The name of the university.

        Returns:
            A dictionary containing the university's data, or None.
        """
        return self.graph.get(university_name)

    def get_all_data(self) -> Dict[str, Any]:
        """
        Returns the entire knowledge graph.
        """
        return self.graph
