"""Final AI Builder (Smart mapping).

Enabled workflow.

Current behavior: runs the standard builder.
Next enhancement: migrate AI-assisted mapping from your SMART_AI notebook.
"""

from __future__ import annotations

from pathlib import Path
from .final_ai_standard import run_final_ai_standard


def run_final_ai_smart(af_input_xlsx: Path, country_code_xlsx: Path, template_xlsx: Path, out_xlsx: Path):
    return run_final_ai_standard(af_input_xlsx, country_code_xlsx, template_xlsx, out_xlsx)
