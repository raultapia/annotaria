#!/usr/bin/env python3
"""
Copyright (c) Raul Tapia
Email: raultapia@us.es

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import tqdm
import argparse
import json
import labelme
import numpy
import os


def check_if_circle(points):
    if len(points) < 3:
        return False
    arr = numpy.array(points, dtype=float)
    cx, cy = arr.mean(axis=0)
    dists = numpy.sqrt((arr[:, 0] - cx)**2 + (arr[:, 1] - cy)**2)
    return dists.std() < 1


def check_if_line(points, tolerance=0.01):
    if len(points) < 2:
        return False
    arr = numpy.array(points, dtype=float)
    centroid = arr.mean(axis=0)
    centered_points = arr - centroid

    U, S, Vt = numpy.linalg.svd(centered_points, full_matrices=False)
    if S[0] == 0:
        return True

    ratio = S[1] / S[0]
    return ratio < tolerance


def get_line_extremes(points):
    arr = numpy.array(points, dtype=float)
    centroid = arr.mean(axis=0)
    centered = arr - centroid
    U, S, Vt = numpy.linalg.svd(centered, full_matrices=False)
    direction = Vt[0]
    t = numpy.dot(centered, direction)
    t_min = t.min()
    t_max = t.max()
    point_min = centroid + t_min * direction
    point_max = centroid + t_max * direction
    return [[point_min[0], point_min[1]], [point_max[0], point_max[1]]]


def coco2labelme(coco_json_path, images_folder):
    with open(coco_json_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)

    images = coco_data["images"]
    annotations = coco_data["annotations"]
    categories = coco_data["categories"]
    cat_id_to_name = {cat["id"]: cat["name"] for cat in categories}
    image_id_to_info = {}
    image_id_to_shapes = {}

    for img in images:
        image_id_to_info[img["id"]] = img
        image_id_to_shapes[img["id"]] = []

    for ann in annotations:
        image_id = ann["image_id"]
        cat_id = ann["category_id"]
        category_name = cat_id_to_name[cat_id]

        if ann["area"] < 3:
            points = ann["segmentation"][0] if len(ann["segmentation"]) > 0 else []
            points = [points[i:i + 2] for i in range(0, len(points), 2)]
            if check_if_line(points):
                points = get_line_extremes(points)
                shape_type = "line"
            else:
                x, y, w, h = ann["bbox"]
                cx = x + w / 2
                cy = y + h / 2
                points = [[float(cx), float(cy)]]
                shape_type = "point"
        elif len(ann["segmentation"]):
            points = ann["segmentation"][0]
            points = [points[i:i + 2] for i in range(0, len(points), 2)]
            shape_type = "polygon"
            if check_if_circle(points):
                x, y, w, h = ann["bbox"]
                cx = x + w / 2
                cy = y + h / 2
                r = min(w, h) / 2
                points = [[float(cx), float(cy)], [float(cx + r), float(cy)]]
                shape_type = "circle"
        else:
            x, y, w, h = ann["bbox"]
            points = [[x, y], [x + w, y + h]]
            shape_type = "rectangle"

        shape = {
            "label": category_name,
            "points": points,
            "group_id": None,
            "description": "",
            "shape_type": shape_type,
            "flags": {},
            "mask": None
        }

        image_id_to_shapes[image_id].append(shape)

    for image_id, img_info in tqdm.tqdm(image_id_to_info.items(), desc="Generating LabelMe annotations", unit="file", colour="yellow"):
        shapes = image_id_to_shapes[image_id]

        labelme_annotation = {
            "version": labelme.__version__,
            "flags": {},
            "shapes": shapes,
            "imagePath": img_info["file_name"],
            "imageData": None,
            "imageHeight": img_info["height"],
            "imageWidth": img_info["width"]
        }

        base_filename, _ = os.path.splitext(img_info["file_name"])
        out_fn = base_filename + ".json"
        out_fp = os.path.join(images_folder, out_fn)

        os.makedirs(images_folder, exist_ok=True)

        with open(out_fp, 'w', encoding='utf-8') as f:
            json.dump(labelme_annotation, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="COCO visualizer.")
    parser.add_argument("json_file", help="Path to the JSON file.")
    parser.add_argument("images_folder", nargs="?", default=None, help="Optional path to the folder containing the images. If not provided, images path is obtained from the json path")
    args = parser.parse_args()

    if not os.path.isfile(args.json_file):
        raise Exception(f"{args.json_file} is not a valid JSON file.")

    if args.images_folder is None:
        args.images_folder = os.path.dirname(os.path.abspath(args.json_file)) + "/" + os.path.basename(args.json_file).replace(".json", "/")

    if args.images_folder and not os.path.isdir(args.images_folder):
        raise Exception(f"{args.images_folder} is not a valid directory.")

    print(f"JSON file: {args.json_file}")
    print(f"Images folder: {args.images_folder}")
    coco2labelme(args.json_file, args.images_folder)


if __name__ == "__main__":
    main()
