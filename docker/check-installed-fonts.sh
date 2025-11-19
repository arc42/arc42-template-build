#!/bin/bash
# Script to verify actual font filenames in Ubuntu container

echo "=== Checking Liberation Fonts ==="
find /usr/share/fonts -name "*Liberation*" -type f 2>/dev/null | sort

echo ""
echo "=== Checking DejaVu Fonts ==="
find /usr/share/fonts -name "*DejaVu*" -type f 2>/dev/null | sort

echo ""
echo "=== Checking Noto Sans Fonts ==="
find /usr/share/fonts -name "NotoSans-*.ttf" -o -name "NotoSans.ttf" -type f 2>/dev/null | sort

echo ""
echo "=== Checking Noto Mono Fonts ==="
find /usr/share/fonts -name "NotoSansMono*.ttf" -o -name "NotoMono*.ttf" -type f 2>/dev/null | sort

echo ""
echo "=== Checking WenQuanYi (Chinese) Fonts ==="
find /usr/share/fonts -name "*wqy*" -type f 2>/dev/null | sort
