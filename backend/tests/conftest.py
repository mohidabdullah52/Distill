"""Shared pytest fixtures."""

import pytest


@pytest.fixture
def sample_pages():
    """Sample parser output for chunker tests."""
    return [
        ("report.pdf", 1, "Introduction to machine learning and neural networks."),
        ("report.pdf", 2, "Deep learning uses multiple layers."),
    ]
