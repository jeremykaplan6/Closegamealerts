# Requirements to Turn day03_text_analyzer.py into a Reusable Internal Tool

## Current State
✅ Core functionality works
✅ Clean function boundaries
✅ Simple, readable code
✅ No external dependencies

## What's Needed for Production-Ready Internal Tool

### 1. **Better CLI Interface** (High Priority)
- **Replace manual argv handling with `argparse`**
  - `--file` / `-f` for input file
  - `--mode` / `-m` for read mode (30s/2min) - no interactive prompt
  - `--output` / `-o` for output file (default: stdout)
  - `--format` for output format (text/json/markdown)
  - `--quiet` / `-q` flag for non-interactive use

**Example:**
```bash
text_analyzer --file notes.txt --mode 30s --output report.md
text_analyzer -f notes.txt -m 2min --format json
```

### 2. **Programmatic API** (High Priority)
- **Separate CLI from core logic**
- **Return structured data** (dict/dataclass) instead of only printing
- **Make functions importable** for use in other scripts

**Example:**
```python
from text_analyzer import analyze_text

result = analyze_text(text, mode="30s")
# Returns: {"summary": [...], "risks": [...], "questions": [...]}
```

### 3. **Output Format Options** (Medium Priority)
- **JSON output** for integration with other tools
- **Markdown output** for documentation
- **HTML output** for web integration
- **CSV export** for spreadsheet analysis

### 4. **Error Handling & Validation** (High Priority)
- **Better error messages** with actionable guidance
- **Input validation** (file exists, readable, non-empty)
- **Graceful handling** of edge cases (empty files, malformed text)
- **Exit codes** for scripting (0=success, 1=error, 2=file not found)

### 5. **Configuration Management** (Medium Priority)
- **Config file support** (YAML/JSON/TOML) for:
  - Risk keywords (customizable per organization)
  - Question templates (customizable per team)
  - Default read mode
  - Output formatting preferences
- **Environment variable support** for defaults

### 6. **Batch Processing** (Medium Priority)
- **Process multiple files** at once
- **Directory scanning** with glob patterns
- **Progress indicators** for long operations

**Example:**
```bash
text_analyzer --dir ./notes/ --pattern "*.txt" --mode 30s
```

### 7. **Logging** (Medium Priority)
- **Replace print() with logging module**
- **Log levels** (DEBUG, INFO, WARNING, ERROR)
- **Optional log file** output
- **Structured logging** for monitoring

### 8. **Package Structure** (Low-Medium Priority)
```
text_analyzer/
├── __init__.py
├── analyzer.py          # Core analysis functions
├── cli.py               # CLI interface
├── formatters.py        # Output formatters
├── config.py            # Configuration management
└── utils.py             # Utilities
```

### 9. **Documentation** (Medium Priority)
- **README.md** with:
  - Installation instructions
  - Usage examples
  - Configuration guide
  - API documentation
- **Better docstrings** (Google/NumPy style)
- **Type hints** (already partially done ✅)

### 10. **Testing** (High Priority)
- **Unit tests** for core functions
- **Integration tests** for CLI
- **Test fixtures** (sample input files)
- **CI/CD** setup (optional)

### 11. **Dependencies** (Low Priority)
- **requirements.txt** or **pyproject.toml**
- **Version pinning** if adding external deps
- **Optional dependencies** for advanced features

### 12. **Installation** (Low-Medium Priority)
- **setup.py** or **pyproject.toml** for pip install
- **Entry point** for CLI command
- **Make installable** as `text-analyzer` command

**Example:**
```bash
pip install -e .
text-analyzer --file notes.txt
```

## Priority Ranking

### Must-Have (MVP):
1. ✅ Better CLI with argparse (remove interactive prompts)
2. ✅ Programmatic API (return data structures)
3. ✅ Error handling & validation
4. ✅ JSON output option

### Should-Have (V1.0):
5. Multiple output formats (markdown, HTML)
6. Configuration file support
7. Logging instead of print()
8. Basic tests

### Nice-to-Have (V2.0):
9. Batch processing
10. Package structure
11. Full documentation
12. Installation package

## Quick Win: Minimal Changes for Reusability

**Fastest path to "reusable":**
1. Add `argparse` for CLI (30 min)
2. Create `analyze_text()` function that returns dict (15 min)
3. Add JSON output option (15 min)
4. Better error handling (15 min)

**Total: ~1-2 hours** for basic reusability

## Example: Minimal Reusable Version

```python
def analyze_text(text: str, mode: str = "30s") -> dict:
    """Core analysis function - returns structured data."""
    if mode == "30s":
        bullet_count, max_risks, max_questions = 3, 3, 3
    else:
        bullet_count, max_risks, max_questions = 7, 8, 8
    
    return {
        "summary": summarize_bullets(text, bullet_count),
        "risks": key_risks_uncertainties(text, max_risks),
        "questions": questions_to_ask_next(text)[:max_questions],
        "mode": mode
    }

# CLI becomes thin wrapper around analyze_text()

