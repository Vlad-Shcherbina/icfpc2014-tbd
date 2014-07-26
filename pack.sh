#!/bin/bash

FILENAME="lightning_tbd.tar.gz"

mkdir -p submission/solution

cp data/lms/lightning.gcc submission/solution/lambdaman.gcc

cp -r production            submission/code
cp vlad_scratch/gen_gcc.py  submission/code/
cp yole_scratch/gcc_ast.py  submission/code/
cp README                   submission/code/
# cp -r *_scratch submission/code

tar -czf $FILENAME submission/*
rm -rf submission

echo "saved submission in $FILENAME"
sha1sum $FILENAME
echo "secret token for submission: 69ce5cb1-66e0-4a5b-b1dd-ac97269b74e3"

echo "will now upload file"
curl --form "file=@$FILENAME" "http://f.nn.lv/?f=rest"
echo ""
