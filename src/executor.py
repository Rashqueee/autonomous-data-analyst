import io
import contextlib
import pandas as pd

def execute_code(code, df):
    local_env = {"df": df, "pd": pd}
    stdout = io.StringIO()

    with contextlib.redirect_stdout(stdout):
        exec(code, {}, local_env)

    return stdout.getvalue(), local_env

def clean_code(code: str) -> str:
    code = code.strip()

    if code.startswith("```"):
        code = code.replace("```python", "")
        code = code.replace("```", "")

    return code.strip()