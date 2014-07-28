#!/bin/bash

FILENAME="icfpc_tbd.tar.gz"

mkdir -p submission/solution
mkdir submission/code

# solutions
cp data/lms/ff.gcc		submission/solution/lambdaman.gcc
cp data/ghosts/redsplitt.ghc	submission/solution/ghost0.ghc

# code
cp -r *_scratch			submission/code/
cp -r production		submission/code/
cp -r data			submission/code/
cp README			submission/code/

# removing some crap from data
rm -f submission/code/data/id_rsa*
rm -f submission/code/some_results.json

find submission -exec touch -t 1401010000 {} \;
tar -czf $FILENAME -C submission solution code
rm -rf submission

echo "saved submission in $FILENAME"
sha1sum $FILENAME
echo "secret token for submission: 69ce5cb1-66e0-4a5b-b1dd-ac97269b74e3"

echo "will now upload file"
#curl --form "file=@$FILENAME" "http://f.nn.lv/?f=rest"
echo ""
