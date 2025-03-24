from os import path
from authentication.auth_key import auth_data

def authenticate(item: object) -> bool:
    """
    Authenticates a user by validating their API key against a list of valid keys
    stored in a secret YAML file.
    Args:
        item (object): An object containing the attribute `api_key`,
                       which represents the user's API key.
    Returns:
        bool: Returns `True` if the provided API key is valid, otherwise `False`.
    """

    api_key = item.api_key
    valid_api_keys = auth_data["auth_key"]
    if api_key in valid_api_keys:
        return True
    return False