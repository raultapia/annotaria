#!/usr/bin/env python3
"""
Copyright (c) Raul Tapia
Email: raultapia@us.es

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json
import labelme2coco
import os
import sys

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        if not os.path.isdir(arg):
            raise Exception(f"{arg} is not a valid folder.")

    for path in sys.argv[1:]:
        for folder in [x for x in os.listdir(path) if os.path.isdir(f"{path}/{x}")]:
            with open(f"{path}/{folder}.json", 'w') as f:
                x = labelme2coco.get_coco_from_labelme_folder(f"{path}/{folder}").json

                for image in x.get("images", []):
                    file_name = image.get("file_name", "")
                    image["file_name"] = os.path.basename(file_name)

                json.dump(x, f, indent=2)
