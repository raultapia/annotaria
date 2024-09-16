#!/usr/bin/env bash

rm -rf annotation_framework
mkdir annotation_framework
sudo apt -y install python3-pip
pip install --upgrade --target annotation_framework labelme
pip install --upgrade --target annotation_framework labelme2coco
pip install --upgrade --target annotation_framework tqdm
sed -i '1s/^/#/' annotation_framework/sahi/models/__init__.py
