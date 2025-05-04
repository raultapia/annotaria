#!/usr/bin/env python3
"""
Copyright (c) Raul Tapia
Email: raultapia@us.es

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from copy import deepcopy
from PIL import Image
from scipy.interpolate import CubicSpline
import argparse
import io
import json
import numpy as np
import os
import tqdm
import zipfile


def generate_indices(vector, n):
    ret = [float(vector[0])]
    for i in range(len(vector) - 1):
        start = vector[i]
        end = vector[i + 1]
        step = (end - start) / (n[i] + 1)
        ret.extend(start + step * j for j in range(1, n[i] + 2))
    return ret


def mode_interpolation(vector, n):
    from statistics import mode
    return [mode(vector)] * (sum(n) + len(vector)), mode(vector)


def spline_interpolation(x, y, xs):
    cs = CubicSpline(x, y)
    return cs(xs)


def run_interp(data, n, debug=None):
    orig_id = [item['image_id'] for item in data]
    image_id = generate_indices(orig_id, n)
    category_id, mode = mode_interpolation([item['category_id'] for item in data], n)
    bbox_x = spline_interpolation([item['image_id'] for item in data], [item['bbox'][0] for item in data], image_id)
    bbox_y = spline_interpolation([item['image_id'] for item in data], [item['bbox'][1] for item in data], image_id)
    bbox_w = spline_interpolation([item['image_id'] for item in data], [item['bbox'][2] for item in data], image_id)
    bbox_h = spline_interpolation([item['image_id'] for item in data], [item['bbox'][3] for item in data], image_id)

    output = []
    for i in range(len(image_id)):
        d = deepcopy(data[0])
        d["image_id"] = image_id[i]
        d["bbox"] = [bbox_x[i], bbox_y[i], bbox_w[i], bbox_h[i]]
        d["segmentation"] = []
        d["category_id"] = category_id[i]
        d["area"] = int(bbox_w[i] * bbox_h[i])
        d["is_interpolated"] = image_id[i] not in orig_id
        output.append(d)

    if debug is not None:
        import warnings
        warnings.filterwarnings("ignore")
        import matplotlib.pyplot as plt
        warnings.filterwarnings("default")
        plt.figure(figsize=(10, 6))
        fi = [item['image_id'] for item in data]
        bbx = [item['bbox'][0] for item in data]
        bby = [item['bbox'][1] for item in data]
        bbw = [item['bbox'][2] for item in data]
        bbh = [item['bbox'][3] for item in data]
        plt.plot(fi, bbx, 'o', label='Bounding Box X', color='blue', markersize=2.5)
        plt.plot(fi, bby, 'o', label='Bounding Box Y', color='green', markersize=2.5)
        plt.plot(fi, bbw, 'o', label='Bounding Box W', color='red', markersize=2.5)
        plt.plot(fi, bbh, 'o', label='Bounding Box H', color='purple', markersize=2.5)
        plt.plot(image_id, bbox_x, label='Interpolated Bounding Box X0', color='blue')
        plt.plot(image_id, bbox_y, label='Interpolated Bounding Box Y0', color='green')
        plt.plot(image_id, bbox_w, label='Interpolated Bounding Box X1', color='red')
        plt.plot(image_id, bbox_h, label='Interpolated Bounding Box Y1', color='purple')
        plt.title(f"Interpolated Bounding Box Coordinates for track ID {data[0]['track_id']}")
        plt.xlabel("Frame Index")
        plt.ylabel("Bounding Box Coordinates")
        plt.legend()
        plt.grid(True)

        # Save plot to in-memory buffer and write to zip
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        with zipfile.ZipFile(debug, 'a') as zf:
            zf.writestr(f"track{data[0]['track_id']}_plot.png", buffer.read())
        buffer.close()
        plt.close()

    return output


def main():
    parser = argparse.ArgumentParser(description="COCO interpolator.")
    parser.add_argument("json_file", help="Path to the JSON file.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--number", type=int, help="Interpolation factor")
    group.add_argument("-a", "--auto", action="store_true", help="Automatically select interpolation factor to fit non-annotated images.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")
    args = parser.parse_args()
    debug_zip = os.path.abspath(args.json_file).replace(".json", "-interp_debug.zip") if args.debug else None

    if debug_zip:
        with zipfile.ZipFile(debug_zip, 'w') as zf:
            pass  # Create an empty zip file to append debug images later

    with open(os.path.abspath(args.json_file), 'r') as f:
        json_file = json.load(f)
        annotations = json_file.get("annotations", [])
        track_annotations = {}
        for annotation in annotations:
            track_id = annotation.get("track_id")
            if track_id not in track_annotations:
                track_annotations[track_id] = []
            track_annotations[track_id].append(annotation)

        interp_annotations = []
        used_image_files = {}
        for track_id, track in tqdm.tqdm(track_annotations.items(), desc="Interpolating annotations", unit="instance", colour="yellow"):
            seq = [item['image_id'] for item in track]
            if args.auto:
                seq = [img["file_name"] for img in json_file.get("images", []) if img["id"] in seq]
                seq_files = sorted([f for f in os.listdir(os.path.abspath(args.json_file).replace(".json", "/")) if f.endswith(".png")])
                n = [sum(1 for f in seq_files if seq[i] < f < seq[i + 1]) for i in range(len(seq) - 1)]
                interp_annotations.extend(run_interp(track, n, debug_zip))

                image_id = generate_indices([item['image_id'] for item in track], n)
                image_filename = [f for f in seq_files if any(seq[i] <= f <= seq[i + 1] for i in range(len(seq) - 1))]
                for img_id, img_file in zip(image_id, image_filename):
                    img_path = os.path.join(os.path.abspath(args.json_file).replace(".json", "/"), img_file)
                    with Image.open(img_path) as img:
                        width, height = img.size
                    used_image_files[img_id] = {"file_name": img_file, "width": width, "height": height}
            else:
                n = [(args.number + 1) * (seq[i + 1] - seq[i]) - 1 for i in range(len(seq) - 1)]
                interp_annotations.extend(run_interp(track, n, debug_zip))

    with open(os.path.abspath(args.json_file).replace('.json', '-interp.json'), 'w', encoding='utf-8') as f:
        interp_annotations = sorted(interp_annotations, key=lambda x: x["image_id"])
        for idx, annotation in enumerate(interp_annotations):
            annotation["id"] = idx + 1
        json_file["annotations"] = interp_annotations
        if args.auto:
            json_file["images"] = [{"height": img_file["height"], "width": img_file["width"], "id": img_id, "file_name": img_file["file_name"]} for img_id, img_file in used_image_files.items()]
        json.dump(json_file, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
