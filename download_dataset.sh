#!/bin/bash
# Helper script to download LOCOMO dataset

set -e

echo "=========================================="
echo "LOCOMO Dataset Download Helper"
echo "=========================================="

DATASET_DIR="dataset"
GDRIVE_URL="https://drive.google.com/drive/folders/1L-cTjTm0ohMsitsHg4dijSPJtqNflwX-?usp=drive_link"

# Create dataset directory
mkdir -p "$DATASET_DIR"

echo "📥 LOCOMO Dataset Files:"
echo ""
echo "Files available on Google Drive:"
echo "  1. locomo10.json (2.7 MB) - Main dataset"
echo "  2. locomo10_rag.json (2.3 MB) - RAG-formatted dataset"
echo ""
echo "Google Drive Link:"
echo "  $GDRIVE_URL"
echo ""

# Check if files already exist
if [ -f "$DATASET_DIR/locomo10.json" ]; then
    echo "✅ Found: $DATASET_DIR/locomo10.json"
    echo "   Size: $(du -h "$DATASET_DIR/locomo10.json" | cut -f1)"
else
    echo "❌ Missing: $DATASET_DIR/locomo10.json"
fi

if [ -f "$DATASET_DIR/locomo10_rag.json" ]; then
    echo "✅ Found: $DATASET_DIR/locomo10_rag.json"
    echo "   Size: $(du -h "$DATASET_DIR/locomo10_rag.json" | cut -f1)"
else
    echo "❌ Missing: $DATASET_DIR/locomo10_rag.json"
    echo "   (Optional - only needed for RAG experiments)"
fi

echo ""
echo "=========================================="
echo "Download Instructions:"
echo "=========================================="
echo ""
echo "Option 1: Manual Download"
echo "  1. Open the Google Drive link:"
echo "     $GDRIVE_URL"
echo "  2. Download both files:"
echo "     - locomo10.json"
echo "     - locomo10_rag.json (optional)"
echo "  3. Place them in: $(pwd)/$DATASET_DIR/"
echo ""
echo "Option 2: Using gdown (if installed)"
if command -v gdown &> /dev/null; then
    echo "  ✅ gdown is installed"
    echo ""
    echo "  To download:"
    echo "    cd $DATASET_DIR"
    echo "    # Extract file IDs from Google Drive URL"
    echo "    # Then use: gdown --id FILE_ID"
else
    echo "  ❌ gdown is not installed"
    echo ""
    echo "  Install with: pip install gdown"
    echo "  Then you can download files using their Google Drive file IDs"
fi
echo ""
echo "Option 3: Using wget/curl (if files are publicly accessible)"
echo "  Note: Google Drive requires authentication for direct downloads"
echo ""

# Check if all required files exist
if [ -f "$DATASET_DIR/locomo10.json" ]; then
    echo "✅ Ready to run experiments!"
    echo ""
    echo "Next steps:"
    echo "  1. Ensure .env file has OPENAI_API_KEY"
    echo "  2. Run: python3 run_experiments_improved.py --method add --data_path dataset/locomo10.json"
else
    echo "⚠️  Please download locomo10.json before running experiments"
fi

