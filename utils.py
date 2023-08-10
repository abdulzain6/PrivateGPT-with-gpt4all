import os
import re

def sanitize_filename(filename: str) -> str:
    return os.path.basename(filename)

def replace_specials_with_underscores(string: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", string)