#!/bin/bash

# Option 1: PNG zu JPEG konvertieren (meist dramatische Größenreduktion)
# for i in `find . -type f ! -name "thumb-*.png" -name "*.png" | grep -v thumbs`;
# do
#   filefull="${i##*/}"
#   file="${filefull%.[^.]*}"
#   ext="${filefull:${#file} + 1}"
#   dir=$(echo ${i} | sed -e "s/${file}\.${ext}//")
#   source="${dir}${file}.${ext}"
  
#   if [ ! -d ${dir}thumbs/ ];
#   then
#     mkdir ${dir}thumbs/
#   fi
  
#   # Als JPEG speichern für dramatische Größenreduktion
#   dest="${dir}thumbs/${file}.jpg"
  
#   if [ -f ${dest} ];
#   then
#     continue;
#   fi;
  
#   # PNG zu JPEG mit weißem Hintergrund (für Transparenz)
#   convert ${source} -background white -flatten -quality 85 -strip ${dest};
#   echo "convert ${source} -background white -flatten -quality 85 -strip ${dest};"
# done

echo -e "\n=== webp Konvertierung ==="
# for i in posts/**/*.{jpg,jpeg,png,JPG,JPEG,PNG}; do
for i in `find . -type f ! -name "*.svg" ! -name "*.webp" ! -name "*.gif" | grep -v thumbs`; do 
  # echo "i: $i"
  [ ! -f "$i" ] && continue
  
  filename=$(basename "$i")
  name="${filename%.*}"
  dir=$(dirname "$i")
  output="${dir}/${name}.webp"
  
  [ -f "$output" ] && continue
  
  # Dateigröße prüfen
  size=$(stat -f%z "$i" 2>/dev/null || stat -c%s "$i" 2>/dev/null)
  
  # Qualität basierend auf Dateigröße anpassen
  if [ "$size" -gt 1000000 ]; then  # > 1MB
    quality=75
  elif [ "$size" -gt 500000 ]; then # > 500KB
    quality=80
  else
    quality=85
  fi
  
  echo "Konvertiere: $i (${size} bytes) -> $output (quality: $quality)"
  cwebp -q $quality "$i" -o "$output"
done

