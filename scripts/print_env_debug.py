#!/usr/bin/env python3
import os
keys = [k for k in os.environ.keys() if any(x in k.lower() for x in ("github","pypi","slack","acosp","helm"))]
if not keys:
    print("<no matching env vars found>")
else:
    for k in keys:
        print(f"{k}={os.environ[k]}")
