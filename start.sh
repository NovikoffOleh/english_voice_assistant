#!/bin/bash

# Завантаження та розпакування ffmpeg
echo "🔽 Downloading ffmpeg..."
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz

# Знаходимо папку з ffmpeg
FFMPEG_DIR=$(find . -type d -name "ffmpeg*" | head -n 1)

# Додаємо до PATH
export PATH="$PATH:$(pwd)/$FFMPEG_DIR"

echo "✅ ffmpeg installed. PATH=$PATH"

# Запуск бота
echo "🚀 Starting bot..."
python3 bot.py
