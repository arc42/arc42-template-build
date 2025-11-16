#!/bin/bash
# Quick test that outputs were created

echo "Testing build outputs..."

EXPECTED_FILES=(
    "workspace/build/EN/withHelp/html/arc42-template-EN-withHelp.html"
    "workspace/build/EN/withHelp/pdf/arc42-template-EN-withHelp.pdf"
    "workspace/build/EN/withHelp/docx/arc42-template-EN-withHelp.docx"
    "workspace/build/DE/withHelp/html/arc42-template-DE-withHelp.html"
    "workspace/build/DE/withHelp/pdf/arc42-template-DE-withHelp.pdf"
    "workspace/build/DE/withHelp/docx/arc42-template-DE-withHelp.docx"
)

for file in "${EXPECTED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        exit 1
    fi
done

echo "All expected files created!"