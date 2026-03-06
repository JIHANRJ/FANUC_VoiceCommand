"""Reusable Ollama-based order extraction package."""

from .strict_json_extractor import (
    OrderExtractor,
    create_extractor,
    extract_order,
    extract_order_with_inventory,
    load_model,
)
from .generic_schema_extractor import (
    GenericSchemaExtractor,
    create_generic_extractor,
    extract_with_schema,
    extract_with_schema_files,
)

__all__ = [
    "OrderExtractor",
    "create_extractor",
    "extract_order",
    "extract_order_with_inventory",
    "load_model",
    "GenericSchemaExtractor",
    "create_generic_extractor",
    "extract_with_schema",
    "extract_with_schema_files",
]
