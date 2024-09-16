#!/usr/bin/env python3
"""
Copyright (c) Raul Tapia
Email: raultapia@us.es

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import cv2
import dataclasses
import enum
import json
import numpy
import os
import sys


@dataclasses.dataclass
class Config:
    ADD_LABEL: bool = True
    DISPLAY_NON_ANNOTATED: bool = True
    ALWAYS_DRAW_BBOX: bool = True
    FPS: int = 20


class Key(enum.Enum):
    EXIT, NEXT, PREV, ROTATE, SLEEP = 27, 100, 97, 114, 32

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class Counter:
    def __init__(self, minval, maxval):
        self.minval = minval
        self.maxval = maxval
        self.cnt = minval

    def __index__(self):
        return self.cnt

    def __iadd__(self, n):
        for i in range(n):
            self.cnt += 1
            if self.cnt > self.maxval:
                self.cnt = self.minval
        return self.cnt

    def __isub__(self, n):
        for i in range(n):
            self.cnt -= 1
            if self.cnt < self.minval:
                self.cnt = self.maxval
        return self.cnt


def generate_colors(N, colormap_name):
    values = numpy.linspace(0, 255, N, dtype=numpy.uint8)
    img = numpy.reshape(values, (N, 1))
    colormap = eval(f"cv2.COLORMAP_{colormap_name}")
    img = cv2.applyColorMap(img, colormap)
    colors = [tuple(map(int, img[i, 0, :])) for i in range(N)]
    return colors


def reshape(img, threshold):
    scale = (threshold / (img.shape[0] * img.shape[1]))**0.5
    img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
    return (img, scale)


def rotate_point(p, shape):
    if not isinstance(p[0], float):
        p = p[0]
    return shape[0] - p[1], shape[1] - p[0]


def wait_key(cnt, sleep, rotate):
    c = 0
    while not Key.has_value(c):
        c = cv2.waitKey(int((1 / Config.FPS) * 1e3) * (not sleep))
        if c == -1:
            c = Key.NEXT.value

    if Key(c) == Key.EXIT:
        return (0, 0, True)
    elif Key(c) == Key.PREV:
        cnt -= 1
    elif Key(c) == Key.NEXT:
        cnt += 1
    elif Key(c) == Key.ROTATE:
        rotate = not rotate
    elif Key(c) == Key.SLEEP:
        sleep = not sleep
    return (sleep, rotate, False)


def callback(x):
    Config.FPS = x


def main(json_file):
    with open(json_file, 'r') as f:
        coco = json.load(f)

    img_data = coco['images']
    ann_data = coco['annotations']
    color_list = generate_colors(len(coco['categories']), "RAINBOW")

    if Config.DISPLAY_NON_ANNOTATED:
        x = img_data[0]['file_name']
        x = x[:len(x) - x[::-1].index("/")]
        filenames = [x + y for y in os.listdir(x) if y[-4:] == '.png']
        annotated_filenames = [x['file_name'] for x in img_data]
        filenames.sort()
        annotated_filenames.sort()
        has_annotations = [x in annotated_filenames for x in filenames]

    k = Counter(0, len(filenames) - 1 if Config.DISPLAY_NON_ANNOTATED else len(img_data) - 1)
    sleep = True
    rotate = False
    cv2.namedWindow("COCO VISUALIZER", cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("FPS", "COCO VISUALIZER", 20, 800, callback)
    cv2.setTrackbarMin("FPS", "COCO VISUALIZER", 1)

    while True:
        img = cv2.imread(filenames[k] if Config.DISPLAY_NON_ANNOTATED else img_data[k]['file_name'])
        if rotate:
            img = cv2.rotate(img, cv2.ROTATE_180)
        img, scale = reshape(img, 1e6)
        for ann in ann_data:
            if Config.DISPLAY_NON_ANNOTATED:
                check = has_annotations[k] and ann['image_id'] == img_data[annotated_filenames.index(filenames[k])]['id']
            else:
                check = ann['image_id'] == img_data[k]['id']
            if check:
                # Label
                x, y, w, h = [scale * x for x in ann['bbox']]
                label = coco['categories'][ann['category_id']]['name'].upper() + " (" + str(ann['category_id']) + ")"
                if rotate:
                    x, y = map(lambda a, b: a - b, rotate_point([x, y], img.shape), (w, h))
                if y < 20 and Config.ADD_LABEL:
                    cv2.putText(img, label, (int(x), int(y + h + 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color_list[ann['category_id']], 2)
                elif Config.ADD_LABEL:
                    cv2.putText(img, label, (int(x), int(y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color_list[ann['category_id']], 2)
                if Config.ALWAYS_DRAW_BBOX:
                    cv2.rectangle(img, (int(x), int(y)), (int(x + w), int(y + h)), color_list[ann['category_id']], 1)

                if ('segmentation' in ann) and ann['segmentation']:
                    # Segmentation
                    points = (scale * numpy.array(ann['segmentation'])).astype(numpy.int32).reshape(-1, 1, 2)
                    img = cv2.polylines(img, [numpy.array([rotate_point(x, img.shape) for x in points]) if rotate else points], True, color_list[ann['category_id']], 3)
                else:
                    # Bounding box
                    cv2.rectangle(img, (int(x), int(y)), (int(x + w), int(y + h)), color_list[ann['category_id']], 3)

        sub_img = img[img.shape[0] - 150:img.shape[0] - 20, 5:280]
        img[img.shape[0] - 150:img.shape[0] - 20, 5:280] = cv2.addWeighted(sub_img, 0.5, numpy.zeros(sub_img.shape, dtype=numpy.uint8), 0.5, 1.0)
        cv2.putText(img, "Press A for previous image", (10, img.shape[0] - 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, "Press D for next image", (10, img.shape[0] - 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, "Press R to rotate the image", (10, img.shape[0] - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, f"Press SPACE to {'play' if sleep else 'pause'} sequence", (10, img.shape[0] - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, "Press ESC to exit", (10, img.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("COCO VISUALIZER", img)
        sleep, rotate, exit = wait_key(k, sleep, rotate)
        if exit:
            return


if __name__ == "__main__":
    if not len(sys.argv) == 2:
        raise Exception("This scripts receives a json file.")

    if not os.path.isfile(sys.argv[1]):
        raise Exception(f"{sys.argv[1]} is not a valid json file.")

    main(sys.argv[1])

    cv2.destroyAllWindows()
