def dict_as_snake(dict_val: dict) -> dict:
    """TastyWorks uses kebab case, nuff said"""
    return {k.replace('-', '_'): v for k, v in dict_val.items()}
