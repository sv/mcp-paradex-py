"""
Sample test file to demonstrate testing in the project.
"""

import pytest


def test_sample():
    """Sample test function."""
    assert True


@pytest.mark.parametrize(
    "input_value,expected",
    [
        (1, 1),
        (2, 2),
        ("test", "test"),
    ],
)
def test_sample_parametrized(input_value, expected):
    """Sample parametrized test function."""
    assert input_value == expected
