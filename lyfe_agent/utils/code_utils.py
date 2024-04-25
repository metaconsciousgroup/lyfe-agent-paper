

def decorate_code(code: str, language="javascript") -> str:
    """
    Decorate the code with the necessary imports and variables.
    """
    if language == "javascript":
        return f"await {code}"
    else:
        raise ValueError(f"Language {language} not supported.")