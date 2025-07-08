#!/bin/bash

echo "🚀 Bắt đầu format và fix code với Ruff..."

# Chạy ruff format cho imports
echo "📦 Format imports..."
ruff format --select I .

echo "Prunning pycache..."
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "Prunning .ruff_cache..."
rm -rf .ruff_cache

echo "Prunning .mypy_cache..."
rm -rf .mypy_cache

echo "Prunning .DS_Store..."
rm -rf .DS_Store

echo "Prunning .vscode..."
rm -rf .vscode
# Chạy ruff format cho toàn bộ document  
echo "📝 Format documents..."
ruff format .

# Chạy ruff check và fix tất cả lỗi có thể tự động sửa
echo "🔧 Fix các lỗi tự động..."
ruff check --fix .

echo "✅ Hoàn thành! Code đã được format và fix." 