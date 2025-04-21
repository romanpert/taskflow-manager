import os
import re

pattern = re.compile(r"^\s*(\w+)\s*:\s*\1\b")

for root, _, files in os.walk("taskflow_manager"):
    for fname in files:
        if fname.endswith(".py"):
            path = os.path.join(root, fname)
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if pattern.search(line):
                        print(
                            f"⚠️  Posible conflicto en {path} línea {i}: "
                            f"{line.strip()}"
                        )
