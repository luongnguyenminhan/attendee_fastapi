#!/bin/bash

echo "🚀 Bắt đầu format và fix code với Ruff..."

# Chạy ruff format cho imports
echo "📦 Format imports..."
ruff format --select I .

# Chạy ruff format cho toàn bộ document  
echo "📝 Format documents..."
ruff format .

# Chạy ruff check và fix tất cả lỗi có thể tự động sửa
echo "🔧 Fix các lỗi tự động..."
ruff check --fix .

echo "✅ Hoàn thành! Code đã được format và fix." 