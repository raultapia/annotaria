#!/usr/bin/env bash

sudo chmod +x runv
sudo apt -y install python3-pip
sudo apt -y install python3-venv
python3 -m venv annotation-env

./runv pip install --upgrade pip
./runv pip install pyqt5 --verbose
./runv pip install bagpy --verbose
./runv pip install cv-bridge --verbose
./runv pip install labelme --verbose
./runv pip install labelme2coco --verbose

sed -i '1s/^/#/' annotation-env/lib/python*/site-packages/sahi/models/__init__.py
sed -i '/import os; os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")/d' annotation-env/lib/python*/site-packages/labelme/__main__.py
sed -i '1i import os; os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")' annotation-env/lib/python*/site-packages/labelme/__main__.py

python_version=$(grep -oP '^version\s*=\s*\K.*' annotation-env/pyvenv.cfg)
major=$(echo "$python_version" | cut -d'.' -f1)
minor=$(echo "$python_version" | cut -d'.' -f2)
if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 9 ]; }; then
  sed -i '/from __future__ import annotations/d' annotation-env/lib/python*/site-packages/labelme/ai/text_to_annotation.py
  sed -i '1 i\from __future__ import annotations' annotation-env/lib/python*/site-packages/labelme/ai/text_to_annotation.py
fi
