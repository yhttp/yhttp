def flatten_json(json_obj, parent_key='', sep='.'):
    """
    Recursively flattens a nested JSON object into a dot-separated dictionary.
    Preserves lists as-is to maintain compatibility with MultiDict.

    Example:
    {
        "foo": {"nested": "value"},
        "bar": [1, 2, 3]
    }
    becomes:
    {
        "foo.nested": "value",
        "bar": [1, 2, 3]
    }
    """
    items = {}
    for k, v in json_obj.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_json(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items
