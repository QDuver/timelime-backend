
import json
def fix_json_comma_error(json_str, error_char_position):
    """Attempts to fix a JSON string by inserting a comma at the specified character position."""
    return json_str[:error_char_position] + ',' + json_str[error_char_position:]

def decode_json_with_auto_fix(json_str, max_attempts=10):
    attempts = 0
    while attempts < max_attempts:
        try:
            return json.loads(json_str)  # Try to decode the JSON
        except json.JSONDecodeError as e:
            error_message = str(e)
            if "Expecting ',' delimiter" in error_message:
                # Extract the character position from the error message
                char_pos = int(error_message.split('char ')[-1].rstrip(')'))
                json_str = fix_json_comma_error(json_str, char_pos)
            else:
                # If the error is not about a missing comma, raise the original error
                raise
        attempts += 1
    raise ValueError("Failed to fix JSON after multiple attempts.")


def parse_json(json_str):
    try:
        return json.loads(json_str)
    except:
        try:
            fixed_json = decode_json_with_auto_fix(json_str)
            return fixed_json
        except Exception as e:
            print(f"Failed to fix JSON: {e}")
