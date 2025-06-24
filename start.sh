#!/bin/bash

# Завантаження та розпакування ffmpeg
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ

# Додати ffmpeg в PATH
export PATH="$PATH:$(pwd)/ffmpeg-*/"

# Запуск бота
python3 bot.py


