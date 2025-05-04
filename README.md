<div align="center" style="margin-bottom: 10px;">
<a href="https://github.com/raultapia/annotaria">
<img width="500" src="https://github.com/raultapia/annotaria/blob/main/.github/assets/annotaria.png?raw=true" alt="annotaria">
</a>
</div>
<p align="center" class="brief">
Welcome to my personal image annotation framework!
</p>

## 🧩 Installation

To get started, install the framework:

```bash
git clone https://github.com/raultapia/annotaria
pip install .
```

## 💬 Commands

| **Command**    | **Description**                                                                               |
| -------------- | --------------------------------------------------------------------------------------------- |
| `bag2images`   | Extract individual image frames from a ROS bag file, enabling easy access to raw image data   |
| `labelme`      | Annotate images with polygons, bounding boxes, or other shapes using `labelme` tool           |
| `labelme2coco` | Convert `labelme` annotation files into the widely-used COCO dataset format for compatibility |
| `coco2labelme` | Recreate `labelme` JSON files from a COCO JSON file, retrieving original data                 |
| `cocoviz`      | Visualize COCO dataset annotations with an interactive GUI                                    |
| `interpolator` | Interpolate annotations using cubic splines                                                   |

---

### `bag2images`

#### Arguments:

- `BAG_FILE` (required): One or more paths to ROS bag files (`.bag`) to process.

#### Example:

```bash
bag2images my_rosbag.bag
```

---

### `labelme`

#### Arguments:

No additional arguments are required. The tool will launch the GUI for annotation.

#### Example:

```bash
labelme
```

---

### `labelme2coco`

#### Arguments:

- `FOLDERS` (required): One or more folders containing `labelme` JSON files to process.

#### Example:

```bash
labelme2coco annotations_folder
```

---

### `coco2labelme`

#### Arguments:

- `json_file` (required): Path to the COCO JSON file.
- `images_folder` (optional): Path to the folder containing the images. If not provided, the images path is derived from the JSON file.

#### Example:

```bash
coco2labelme coco_annotations.json images_folder
```

---

### `cocoviz`

#### Arguments:

- `json_file` (required): Path to the COCO JSON file.
- `images_folder` (optional): Path to the folder containing the images. If not provided, the images path is derived from the JSON file.
- `--skip-non-annotated` or `-s` (optional): Skip displaying non-annotated images.

#### Example:

```bash
cocoviz coco_annotations.json images_folder --skip-non-annotated
```

---

### `interpolator`

#### Arguments:

- `json_file` (required): Path to the COCO JSON file.
- `-n` or `--number` (optional): Interpolation factor. Specifies the number of interpolated frames between consecutive annotations.
- `-a` or `--auto` (optional): Automatically select the interpolation factor to fit non-annotated images.
- `-d` or `--debug` (optional): Enable debug mode. Generates debug plots for each track and saves them in a ZIP file.

#### Example:

1. Interpolate with a fixed factor of 5:

```bash
interpolator coco_annotations.json -n 5
```

2. Automatically determine the interpolation factor:

```bash
interpolator coco_annotations.json -a
```

3. Enable debug mode to generate plots:

```bash
interpolator coco_annotations.json -n 5 -d
```

---

## 📜 Acknowledgments

This framework leverages the powerful capabilities of the [`labelme`](https://github.com/wkentaro/labelme) tool for image annotation and the [`labelme2coco`](https://github.com/fcakyon/labelme2coco) utility for converting annotations into the COCO dataset format. Full credit goes to their respective developers.
