# Dependencies and Requirements

## Do You Need the Mem0 Folder?

**No, you do NOT need the `mem0` folder** from the parent directory to run this improved version.

## How It Works

The improved version uses the **`mem0ai` Python package** installed via pip, not the local mem0 folder. 

### Package Dependency

The code imports from the installed `mem0ai` package:
```python
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.memory.utils import extract_json
```

This package is installed when you run:
```bash
pip install -r requirements.txt
```

Which includes:
```
mem0ai>=1.0.0
```

### Verification

You can verify the package is installed correctly:
```bash
python3 -c "from mem0 import Memory; print('✅ mem0ai package installed')"
```

The package will be installed in your Python site-packages (e.g., `/usr/local/lib/python3.x/site-packages/mem0/`), not from the local folder.

## What About the Mem0 Folder?

The `mem0` folder in the parent directory is **only referenced** in one optional use case:

### Optional: Comparison with Original Results

If you want to compare your results with the original Mem0 evaluation results, the `compare_results.py` script can optionally reference the original results file. This is completely optional and not required to run the improved version.

```bash
# This is OPTIONAL - only if you have original Mem0 results
python compare_results.py \
    --original_file path/to/original/evaluation_metrics.json \
    --improved_file evaluation_improved_metrics.json
```

## Standalone Operation

The improved version is **fully standalone** and can run independently:

1. ✅ Clone the repository
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Set up environment variables (`.env` file)
4. ✅ Download the LOCOMO dataset
5. ✅ Run experiments

**No mem0 folder needed!**

## Summary

| Component | Required? | Purpose |
|-----------|-----------|---------|
| `mem0ai` package (via pip) | ✅ **YES** | Core functionality |
| Local `mem0` folder | ❌ **NO** | Not needed |
| Original Mem0 results (for comparison) | ⚠️ **Optional** | Only for comparing results |

## Installation

Simply install the required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `mem0ai>=1.0.0` - The Mem0 package
- `openai>=1.0.0` - OpenAI API client
- `python-dotenv>=1.0.0` - Environment variables
- `tqdm>=4.65.0` - Progress bars
- `jinja2>=3.1.0` - Template engine
- `numpy>=1.24.0` - Numerical operations

No need to clone or reference the original mem0 repository!

