import os
import sys

# temporarily patch main.py
with open("main.py", "r") as f:
    original = f.read()

patched = original.replace(
    'raise ValueError("Selected recommendation is not available")',
    'raise ValueError(f"Selected recommendation is not available. selected_ids: {selected_ids}, recs: {[{r.flight.id, r.hotel.id} for r in (recommendations or [])]}")'
)

with open("main.py", "w") as f:
    f.write(patched)
