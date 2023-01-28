#!/bin/bash
source ../fin/bin/activate
pip install -r requirements.txt 1> /dev/null

startup_path=$HOME"/.ipython/profile_default/startup"

mkdir -p $startup_path
rm -rf $startup_path/*
echo "Path cleaned:"
ls $startup_path
echo $startup_path
cp -r ./core/*.py $startup_path
cp -r ./extensions/ $startup_path
cp ./autoimport/autoimport.py $startup_path
echo "Path loaded:"
ls $startup_path