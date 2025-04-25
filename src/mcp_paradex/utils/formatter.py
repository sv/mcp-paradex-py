from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel


def serialize_model_with_descriptions(instance: BaseModel) -> dict:
    """
    Serializes a Pydantic model instance including its values,
    field descriptions, and the model's description.

    Args:
        instance: An instance of a Pydantic BaseModel.

    Returns:
        A dictionary containing model description, and field data
        (value and description).
    """
    model_class = type(instance)
    model_schema = model_class.model_json_schema()  # Get the JSON schema
    instance_data = instance.model_dump()  # Get the instance's values

    serialized_output = {
        "model_description": model_class.__doc__.strip() if model_class.__doc__ else None,
        "fields": {},
    }

    # Iterate through the fields defined in the schema's properties
    # This ensures we process fields in a structured way based on the model definition
    if "properties" in model_schema:
        for field_name, field_schema in model_schema["properties"].items():
            if field_name in instance_data:  # Check if the field exists in the instance data
                serialized_output["fields"][field_name] = {
                    "value": instance_data[field_name],
                    "description": field_schema.get(
                        "description"
                    ),  # Use .get() in case description is missing
                }
            # Handle cases where a field might be defined but not present in the dump (e.g. excluded)
            # Or if you want to show all defined fields regardless of instance data:
            # else:
            #     serialized_output["fields"][field_name] = {
            #         "value": None, # Or some placeholder
            #         "description": field_schema.get("description")
            #     }

    # Alternative: Iterate through instance data keys (less robust if fields are excluded)
    # for field_name, value in instance_data.items():
    #     field_info = model_schema.get("properties", {}).get(field_name, {})
    #     serialized_output["fields"][field_name] = {
    #         "value": value,
    #         "description": field_info.get("description")
    #     }

    return serialized_output


# --- Compression Logic ---

T = TypeVar("T", bound=BaseModel)  # Generic type for the model


def compress_model_list(model_list: List[T]) -> Optional[Dict[str, Any]]:
    """
    Compresses a list of Pydantic models by extracting common field values.

    Args:
        model_list: A list of instances of the same Pydantic model type.

    Returns:
        A dictionary with 'common' data (shared across all models)
        and 'items' (list of dictionaries with varying data),
        or None if the input list is empty.
        Returns the original list as 'items' with empty 'common' if only one item exists.
    """
    if not model_list:
        return None
    if len(model_list) == 1:
        # No compression possible/needed for a single item
        return {"common": {}, "items": [model_list[0].model_dump()]}  # Return standard dump

    # Use the first item to get field names and initial potential common values
    first_item_data = model_list[0].model_dump()
    potential_common = first_item_data.copy()

    # Iterate through the rest of the models to find differences
    for item in model_list[1:]:
        item_data = item.model_dump()
        fields_to_remove_from_common = []
        for field_name, common_value in potential_common.items():
            # Important: Check if field exists in current item AND if values differ
            if field_name not in item_data or item_data[field_name] != common_value:
                fields_to_remove_from_common.append(field_name)

        # Remove fields that were not common
        for field_name in fields_to_remove_from_common:
            if field_name in potential_common:  # Avoid KeyError if removed already
                del potential_common[field_name]

        # Optimization: if no common fields left, stop checking
        if not potential_common:
            break

    # Now potential_common holds fields with values identical across ALL items
    common_data = potential_common
    common_field_names = set(common_data.keys())

    # Create the list of items containing only varying data
    varying_items = []
    for item in model_list:
        item_data = item.model_dump()
        varying_data = {
            field_name: value
            for field_name, value in item_data.items()
            if field_name not in common_field_names
        }
        varying_items.append(varying_data)

    return {"common": common_data, "items": varying_items}


# --- Decompression Logic ---


def decompress_to_models(compressed_data: Dict[str, Any], model_class: Type[T]) -> List[T]:
    """
    Reconstructs a list of Pydantic model instances from the compressed format.

    Args:
        compressed_data: The dictionary produced by compress_model_list.
        model_class: The Pydantic model class to instantiate.

    Returns:
        A list of reconstructed Pydantic model instances.
    """
    if not compressed_data:
        return []

    common_data = compressed_data.get("common", {})
    varying_items = compressed_data.get("items", [])
    model_list = []

    for item_data in varying_items:
        # Merge common data with the item-specific varying data
        full_data = {**common_data, **item_data}
        # Validate and create the model instance
        model_instance = model_class.model_validate(full_data)
        model_list.append(model_instance)

    return model_list
