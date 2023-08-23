from typing import Any, Dict

DEFAULT_SCRUBBED_FIELDS = (
    'password',
    'secret',
    'passwd',
    'api_key',
    'apikey',
    'bk_token',
    'bk_ticket',
    'access_token',
    'auth',
    'credentials',
)


def scrub_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Scrub the data, mask all sensitive data fields.

    :return: A new dict, with sensitive data masked as "******".
    """
    if not isinstance(data, dict):
        return data

    def _key_is_sensitive(key: str) -> bool:
        """Check if given key is sensitive."""
        for field in DEFAULT_SCRUBBED_FIELDS:
            if field in key.lower():
                return True
        return False

    result: Dict[str, Any] = {}

    # Use a stack to avoid recursion
    stack = [(data, result)]
    while stack:
        current_data, current_result = stack.pop()

        for key, value in current_data.items():
            if _key_is_sensitive(key):
                current_result[key] = '******'
                continue

            # Process nested data by push it to the stack
            if isinstance(value, dict):
                new_dict: Dict[str, Any] = {}
                current_result[key] = new_dict
                stack.append((value, new_dict))
            else:
                current_result[key] = value
    return result
