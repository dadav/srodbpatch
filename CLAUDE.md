# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**srodbpatch** is a PyQt6 GUI tool for managing database patches. It connects to an MSSQL database and applies SQL patch scripts with automatic backup and restore capabilities.

## Architecture

- **Patch System**: Patches are defined in the `PATCHES` dictionary in `main.py`
- **Each patch includes**:
  - `description`: Human-readable description
  - `backup_tables`: List of tables to backup before applying
  - `sql_statements`: List of SQL statements to execute

## Adding New Patches

To add a new patch, add an entry to the `PATCHES` dictionary:

```python
PATCHES = {
    "Patch Name": {
        "description": "What this patch does",
        "backup_tables": ["TableName1", "TableName2"],
        "sql_statements": [
            "UPDATE ...",
            "INSERT ...",
        ],
    }
}
```
