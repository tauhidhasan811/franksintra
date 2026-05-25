import json
from uuid import uuid4
from typing import List, Dict

import re
import ast



class DataProcessor:
    @staticmethod
    def _get_value(item, key):
        if isinstance(item, dict):
            return item.get(key, "")
        return getattr(item, key, "")



class ProcessData:
    
    @staticmethod
    def CleanData(text):
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        # print(f"Cleaned text: {cleaned}")  # For debugging, see how it's being cleaned.

        # Try parsing it as JSON first
        try:
            # Attempt to load it as JSON
            cleaned = json.loads(cleaned)
        except json.JSONDecodeError:
            # If JSON parsing fails, try using literal_eval (assuming it's a Python literal expression)
            try:
                cleaned = ast.literal_eval(cleaned)
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing content with ast.literal_eval: {e}")
                cleaned = {None}  # Or handle the error as needed (e.g., return a default value or an empty dict/list)

        return cleaned
            
            



