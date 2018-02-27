#!/bin/sh
# 1) Execute assembler to create .obj file with machine code
# 2) Mock the execution of the machine code using algorithm.py

python assembler.py

while true; do
    read -p "Do you wish to compute machine instructions? [y/n] " yn
    case $yn in
        [Yy]* ) python algorithm.py; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done
