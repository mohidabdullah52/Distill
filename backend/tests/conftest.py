"""
Shared pytest fixtures used across the backend test suite.
"""

import pytest


@pytest.fixture
def sample_pages():
    """
    Supplies representative parser output for chunker tests.

    Returns:
        list: Tuples of filename, page number, and sample text.
    """
    return [
        ("report.pdf", 1, "Introduction to machine learning and neural networks."),
        ("report.pdf", 2, "Deep learning uses multiple layers."),
    ]
