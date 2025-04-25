"""
Utilities for working with JMESPath expressions.

This module provides utility functions for working with JMESPath expressions,
including validation, filtering, and error handling.
"""

import logging
from typing import Any, Callable, List, Optional, TypeVar, Union

import jmespath
from jmespath.exceptions import ParseError
from pydantic import TypeAdapter

logger = logging.getLogger(__name__)

T = TypeVar("T")


def apply_jmespath_filter(
    data: List[T],
    jmespath_filter: Optional[str],
    type_adapter: TypeAdapter,
    error_logger: Optional[Callable[[str], Any]] = None,
    strict: bool = False,
    experimental_allow_partial: bool = True,
) -> List[T]:
    """
    Apply a JMESPath filter to a list of data objects.

    Validates the JMESPath filter, applies it to the data after converting to dicts,
    and converts the filtered data back to the original type.

    Args:
        data: List of data objects to filter
        jmespath_filter: JMESPath expression to apply
        type_adapter: Pydantic TypeAdapter to convert filtered data back to original type
        error_logger: Optional function to log errors
        strict: Whether to use strict validation when converting back to original type (default: False)
        experimental_allow_partial: Whether to allow partial validation when converting back (default: True)

    Returns:
        Filtered list of data objects

    Raises:
        ValueError: If the JMESPath filter is invalid
    """
    if not jmespath_filter or jmespath_filter == "null":
        return data

    try:
        # Validate the filter expression
        jmespath.compile(jmespath_filter)

        # Convert to dict for JMESPath to work properly
        data_dicts = [item.model_dump() for item in data]
        filtered_data = jmespath.search(jmespath_filter, data_dicts)

        # Convert back to original type
        if filtered_data:
            return type_adapter.validate_python(
                filtered_data,
                strict=strict,
                experimental_allow_partial="on",
            )
        else:
            return []
    except ParseError as e:
        error_message = f"Invalid JMESPath filter: {e}"
        if error_logger:
            error_logger(error_message)
        logger.error(error_message)
        raise ValueError(error_message)
    except Exception as e:
        error_message = f"Error applying JMESPath filter: {e}"
        if error_logger:
            error_logger(error_message)
        logger.error(error_message)
        raise
