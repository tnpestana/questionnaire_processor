import re

# Normalize all whitespaces in the sequence (spaces, tabs, new lines) by replacing them with a single space " "
def sanitize_text(input: str) -> str: 
    return re.sub(r'\s+', ' ', input).strip()
