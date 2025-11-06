# LOCOMO Dataset Setup

## Dataset Information

The LOCOMO dataset is used for evaluating memory systems. It contains conversational data with various question types to test memory recall and understanding.

**Files:**
- `locomo10.json` (2.7 MB) - Main dataset (required)
- `locomo10_rag.json` (2.3 MB) - RAG-formatted dataset (optional, for RAG experiments)

## Download Instructions

### Google Drive Link
https://drive.google.com/drive/folders/1L-cTjTm0ohMsitsHg4dijSPJtqNflwX-?usp=drive_link

### Method 1: Manual Download (Recommended)

1. Open the Google Drive link above
2. Click on each file to download:
   - `locomo10.json`
   - `locomo10_rag.json` (optional)
3. Place the downloaded files in:
   ```
   evaluation_improved/dataset/
   ```

### Method 2: Using gdown

If you have `gdown` installed:

```bash
pip install gdown

# Navigate to dataset directory
cd evaluation_improved/dataset

# Download files (you'll need the file IDs from Google Drive)
# Right-click on file in Google Drive > Get link > Extract file ID
gdown --id FILE_ID_FOR_LOCOMO10
gdown --id FILE_ID_FOR_LOCOMO10_RAG
```

### Method 3: Using Helper Script

Run the helper script to check status and get instructions:

```bash
cd evaluation_improved
bash download_dataset.sh
```

## Verify Dataset

After downloading, verify the files:

```bash
cd evaluation_improved
ls -lh dataset/
```

You should see:
- `locomo10.json` (~2.7 MB)
- `locomo10_rag.json` (~2.3 MB) [optional]

## Dataset Structure

The `locomo10.json` file contains:
- Multiple conversations with speakers A and B
- Questions and answers (QA pairs) for each conversation
- Categories of questions (1-4)
- Evidence and adversarial answers

Example structure:
```json
[
  {
    "conversation": {
      "speaker_a": "Alice",
      "speaker_b": "Bob",
      "session_1": [...],
      "session_1_date_time": "2022-01-01T00:00:00"
    },
    "qa": [
      {
        "question": "...",
        "answer": "...",
        "category": "1",
        "evidence": [...]
      }
    ]
  }
]
```

## Next Steps

Once the dataset is downloaded:

1. **Verify .env file** has `OPENAI_API_KEY`:
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

2. **Run experiments**:
   ```bash
   # Step 1: Add memories
   python3 run_experiments_improved.py --method add --data_path dataset/locomo10.json
   
   # Step 2: Search and generate answers
   python3 run_experiments_improved.py --method search --data_path dataset/locomo10.json --top_k 30 --filter_memories
   ```

## Troubleshooting

**Issue: "File not found"**
- Ensure files are in `evaluation_improved/dataset/` directory
- Check file names match exactly: `locomo10.json`

**Issue: "Permission denied"**
- Check file permissions: `chmod 644 dataset/locomo10.json`

**Issue: "Invalid JSON"**
- Verify file was downloaded completely (check file size)
- Re-download if file appears corrupted

