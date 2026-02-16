import sys
import os

print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"sys.path: {sys.path}")

try:
    from src.utils.llm import llm
    print("Successfully imported llm")
except Exception as e:
    print(f"Error: {e}")
