#!/usr/bin/env python3
"""
Copyright (c) Raul Tapia
Email: raultapia@us.es

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import argparse
import json
import os


def is_image(filename):
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))


def run_yolo(image_folder, weight_file, conf_thresh):
    import warnings
    warnings.filterwarnings("ignore")
    from ultralytics import YOLO
    warnings.filterwarnings("default")

    model = YOLO(weight_file)
    cnt = 0
    for filename in sorted(os.listdir(image_folder)):
        cnt += 1
        if is_image(filename):
            image_path = os.path.join(image_folder, filename)
            result = model.track(image_path, persist=True, save=False)[0]
            ret = {"shapes": [], "imagePath": filename, "imageData": None, "imageWidth": result.orig_shape[1], "imageHeight": result.orig_shape[0]}
            for x in result:
                if x.boxes.conf > conf_thresh:
                    ret["shapes"].append({
                        "label": x.names[int(x.boxes.cls)],
                        "points": [[int(x.boxes.xyxy[0][0]), int(x.boxes.xyxy[0][1])], [int(x.boxes.xyxy[0][2]), int(x.boxes.xyxy[0][3])]],
                        "group_id": int(x.boxes.id),
                        "shape_type": "rectangle",
                    })
            with open(os.path.join(image_folder, os.path.splitext(filename)[0] + ".json"), "w") as f:
                f.write(json.dumps(ret, indent=4))


def main():
    parser = argparse.ArgumentParser(description="xxx")
    parser.add_argument('folders', metavar='FOLDERS', type=str, nargs='+', help='Folders to process')
    parser.add_argument('--confidence', '-c', type=float, default=0.5, help='Confidence threshold for YOLO (default: 0.5)')
    parser.add_argument('--weights', '-w', type=str, default='yolo11n.pt', help='Path to YOLO weights file (default: "yolo11n.pt" (pretrained))')
    parser.add_argument('--force', '-f', action='store_true', help='Skip warning and proceed without confirmation')
    args = parser.parse_args()

    for arg in args.folders:
        if not os.path.isdir(arg):
            raise Exception(f"{arg} is not a valid folder.")

    if not args.force:
        print("\033[91;1mWARNING: The following folders will have their annotations overwritten:\033[0m")
        for folder in args.folders:
            print(f"\033[91;1m - {os.path.abspath(folder)}\033[0m")
            confirm = input("\033[91;1mDo you want to proceed? (y/n) [n]: \033[0m").strip().lower() or "n"
            if confirm != "y":
                print("\033[91;1mOperation cancelled.\033[0m")
                exit(1)

    for path in args.folders:
        path = os.path.abspath(path)
        for folder in [os.path.join(path, x) for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]:
            run_yolo(folder, args.weights, args.confidence)


if __name__ == "__main__":
    main()
