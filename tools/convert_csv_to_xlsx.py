#!/usr/bin/env python3
"""Convert TEST_CASES.csv to TEST_CASES.xlsx (Excel-friendly).

Usage: python tools/convert_csv_to_xlsx.py
"""
import pandas as pd
from pathlib import Path

SRC = Path('TEST_CASES.csv')
OUT = Path('TEST_CASES.xlsx')

if not SRC.exists():
    raise SystemExit(f"Source file not found: {SRC}")

df = pd.read_csv(SRC, dtype=str).fillna("")

# Convert literal backslash-n sequences to real newlines for Excel display
def fix_newlines(val):
    if not isinstance(val, str):
        return val
    return val.replace('\\n', '\n')

df = df.map(fix_newlines)

df.to_excel(OUT, index=False, engine='openpyxl')
print(f"Wrote {OUT.resolve()}")
