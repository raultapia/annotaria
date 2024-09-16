# Annotation Framework
This is my annotation framework.

## 🧩 Installation
Install the framework using `setup.sh`

## 📤 Step 1
Extract images from rosbag

```
python3 bag2images.py shapes_translation.bag
```

## ✍🏽 Step 2
Annotate images using `labelme`

```
export PYTHONPATH=$PYTHONPATH:$(pwd)/annotation_framework/
python3 annotation_framework/labelme/__main__.py
```

1. Open Dir
2. Check that "File > Save automatically" is on
3. Annotate!
4. Close app when finished

## 🔁 Step 3
Convert annotations using `labelme2coco`

```
export PYTHONPATH=$PYTHONPATH:$(pwd)/annotation_framework/
python3 labelme2coco-launcher.py shapes_translation/
```

## 👀 Optional
Visualize result

```
python3 coco-viz.py shapes_translation/dvs_image_raw.json
```
