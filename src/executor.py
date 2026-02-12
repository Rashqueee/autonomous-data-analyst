import io
import contextlib
import re
import pandas as pd
import matplotlib.pyplot as plt

def execute_code(code, df):
    local_env = {
        "df": df, 
        "pd": pd,
        "plt": plt,
        "result_table": None}

    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
                exec(code, {"__builtins__": __builtins__}, local_env)
    except Exception as e:
        return f"Error during code execution: {str(e)}", local_env

    return stdout.getvalue(), local_env

def clean_code(code: str) -> str:
    code = code.strip()

    # hapus ````
    if "```" in code:
        # Find all code blocks
        code_blocks = re.findall(r'```(?:python)?\n(.*?)```', code, re.DOTALL)
        if code_blocks:
            # Join all code blocks
            code = '\n\n'.join(code_blocks)

    # hapus penjelasan tambahan
    explanatory_patterns = [
        r'\n\s*This code.*$',
        r'\n\s*The above code.*$',
        r'\n\s*Note:.*$',
        r'\n\s*Explanation:.*$',
        r'\n\s*Here\'s what.*$',
        r'\n\s*This will.*$',
        r'\n\s*This script.*$',
        r'\n\s*The result.*$',
        r'\n\s*I\'ve.*$',
        r'\n\s*You can.*$',
    ]
    for pattern in explanatory_patterns:
        code = re.sub(pattern, '', code, flags=re.IGNORECASE | re.DOTALL)

    
    return code.strip()