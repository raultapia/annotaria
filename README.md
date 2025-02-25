# Annotation Framework
This is my annotation framework.

## 🧩 Installation
Install the framework using `setup.sh`

## 📤 Step 1
Extract images from rosbag

```
./runv python3 scripts/bag2images.py shapes_translation.bag
```

## ✍🏽 Step 2
Annotate images using `labelme`

```
./runv labelme
```

1. Open Dir
2. Check that "File > Save automatically" is on
3. Annotate!
4. Close app when finished

## 🔁 Step 3
Convert annotations using `labelme2coco`

```
./runv python3 scripts/labelme2coco-launcher.py shapes_translation/
```

## 👀 Optional
Visualize result

```
./runv python3 scripts/coco-viz.py shapes_translation/dvs_image_raw.json
```
