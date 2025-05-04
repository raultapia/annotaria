from annotaria.coco2labelme import main as coco2labelme_main
from annotaria.interpolator import main as interpolator_main
from annotaria.labelme2coco import main as labelme2coco_main
from unittest.mock import patch
import os
import pytest
import re
import shutil


@pytest.fixture
def clear_json_files(request):
    rootdir = request.config.rootdir
    tests_dir = os.path.join(rootdir, "tests")

    def clear():
        for root, dirs, files in os.walk(os.path.join(tests_dir, "eval")):
            for file in files:
                if file.endswith(".json"):
                    os.remove(os.path.join(root, file))

    clear()
    yield tests_dir
    clear()


@pytest.fixture
def setup_coco2labelme(clear_json_files):
    shutil.copy(os.path.join(clear_json_files, "gt", f"images.json"), os.path.join(clear_json_files, "eval"))
    return clear_json_files


@pytest.fixture
def setup_labelme2coco(clear_json_files):
    for file in ["000000002592", "000000011122", "000000013348"]:
        shutil.copy(os.path.join(clear_json_files, "gt", f"{file}.json"), os.path.join(clear_json_files, "eval", "images"))
    return clear_json_files


@pytest.fixture
def setup_interpolator(clear_json_files):
    shutil.copy(os.path.join(clear_json_files, "gt", f"images.json"), os.path.join(clear_json_files, "eval"))
    return clear_json_files


def test_coco2labelme(setup_coco2labelme):
    with patch("sys.argv", ["coco2labelme.py", os.path.join(setup_coco2labelme, "eval/images.json")]):
        coco2labelme_main()

    for file in ["000000002592", "000000011122", "000000013348"]:
        with open(os.path.join(setup_coco2labelme, f"eval/images/{file}.json"), "r") as f1, open(os.path.join(setup_coco2labelme, "gt", f"{file}.json"), "r") as f2:
            content1 = f1.read()
            content2 = f2.read()
            content1 = re.sub(r'"version": "\d+\.\d+\.\d+",', '', content1)
            content2 = re.sub(r'"version": "\d+\.\d+\.\d+",', '', content2)
            assert content1 == content2, "The files are not exactly equal"


def test_labelme2coco(setup_labelme2coco):
    with patch("sys.argv", ["labelme2coco.py", os.path.join(setup_labelme2coco, "eval")]):
        labelme2coco_main()

    with open(os.path.join(setup_labelme2coco, "eval/images.json"), "r") as f1, open(os.path.join(setup_labelme2coco, "gt", "images.json"), "r") as f2:
        assert f1.read() == f2.read(), "The files are not exactly equal"


def test_interpolator(setup_interpolator):
    with patch("sys.argv", ["coco2labelme.py", os.path.join(setup_interpolator, "eval/images.json"), "-n", "3"]):
        interpolator_main()

    with open(os.path.join(setup_interpolator, "eval/images-interp.json"), "r") as f1, open(os.path.join(setup_interpolator, "gt", "images-interp.json"), "r") as f2:
        assert f1.read() == f2.read(), "The files are not exactly equal"
