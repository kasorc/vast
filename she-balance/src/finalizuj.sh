#!/bin/bash
# Pełna produkcja jednej animacji: render MP4 → muzyka zsynchronizowana ze scenami → MP4 z dźwiękiem.
# ./finalizuj.sh <nazwa>   (PREMIUM=1 ./finalizuj.sh <nazwa> – motion blur, korekcja, ziarno)
set -e
cd "$(dirname "$0")"
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
n=$1
node renderuj.mjs $n ${PREMIUM:+--premium}
read total cuts <<< "$(node sceny.mjs $n)"
python3 muzyka2.py $n $total  # stara, nastrojowa wersja: python3 muzyka.py $n $total "$cuts" "${2:-}"
$FF -y -loglevel error -i ../animacje/$n.mp4 -i ../animacje/$n.wav -c:v copy -c:a aac -b:a 192k -shortest ../animacje/$n-muzyka.mp4
mv ../animacje/$n-muzyka.mp4 ../animacje/$n.mp4
echo "gotowe: $n ($total s)"
