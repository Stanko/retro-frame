#!/bin/bash

FILES=*.webp
for f in $FILES
do
  replace="gif"
  gif=${f/webp/$replace}
  echo "$f -> $gif"
  
  convert -background black -alpha remove -delay 10 -dispose previous -coalesce -loop 0 -layers optimize $f $gif
done  