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
sed -i '1i import os; os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")' annotation-env/lib/python*/site-packages/labelme/__main__.py
