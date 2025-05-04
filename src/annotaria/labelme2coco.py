#!/usr/bin/env python3
"""
Copyright (c) Raul Tapia
Email: raultapia@us.es

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from labelme2coco import get_coco_from_labelme_folder
import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Convert LabelMe annotations to COCO format.")
    parser.add_argument('folders', metavar='FOLDERS', type=str, nargs='+', help='Folders to process')
    args = parser.parse_args()

    for arg in args.folders:
        if not os.path.isdir(arg):
            raise Exception(f"{arg} is not a valid folder.")

    for path in args.folders:
        for folder in [x for x in os.listdir(path) if os.path.isdir(f"{path}/{x}")]:
            with open(f"{path}/{folder}.json", 'w') as f:
                x = get_coco_from_labelme_folder(f"{path}/{folder}").json

                for image in x.get("images", []):
                    file_name = image.get("file_name", "")
                    image["file_name"] = os.path.basename(file_name)

                image_id_prev = -1
                cnt = 0
                for annotation in x.get("annotations", []):
                    image_id = annotation.get("image_id", "")
                    if image_id == image_id_prev:
                        cnt += 1
                    else:
                        cnt = 0
                    image_id_prev = image_id
                    for image in x.get("images", []):
                        if image.get("id") == annotation.get("image_id"):
                            filename = os.path.splitext(image.get("file_name", ""))[0]
                            with open(f"{path}/{folder}/{filename}.json", 'r') as f2:
                                data = json.load(f2)
                                track_id = data.get("shapes", [])[cnt]["group_id"]
                                annotation["track_id"] = track_id
                            break

                json.dump(x, f, indent=2)


if __name__ == '__main__':
    main()
