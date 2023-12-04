import os
import json
from pathlib import Path
from flask import Flask, render_template, Response
from random import choice
import shutil
from loguru import logger as log
from icecream import ic
import urllib.parse


app = Flask(__name__)
app.config["UNCLASSIFIED_DATASET"] = os.path.join("static", "unclassified_dataset")

valid_extensions = ['.jpg', '.png']


@app.route("/")
def home():
    config_file_path = os.path.join(os.getcwd(), "datasets.json")
    with open(config_file_path, 'r') as f:
        config = json.load(f)

    dataset_names = config.keys()
    dataset_names = [str(dataset_name) for dataset_name in dataset_names]
    encoded_dataset_names = [urllib.parse.quote(dataset_name) for dataset_name in dataset_names]
    dataset_count = len(dataset_names)

    return render_template(
        "home.html",
        dataset_count=dataset_count,
        dataset_names=dataset_names,
        encoded_dataset_names=encoded_dataset_names,
    )


@app.route("/<encoded_dataset_name>")
def classifier(encoded_dataset_name):
    decoded_dataset_name = urllib.parse.unquote(encoded_dataset_name)
    config_file_path = os.path.join(os.getcwd(), "datasets.json")
    with open(config_file_path, 'r') as f:
        config = json.load(f)

    image_name = False
    current_image_path = False
    encoded_image_name = False
    all_images_done = False

    unclassified_dataset_dir = Path(Path.cwd(), "static", "unclassified_dataset")
    valid_images = [file_path.name for file_path in unclassified_dataset_dir.iterdir() if file_path.suffix in valid_extensions]
    ic(len(valid_images))

    dataset_dir = Path(os.getcwd(), "Dataset", decoded_dataset_name,)

    existing_images = list()
    for ext in valid_extensions:
        existing_image_gen = dataset_dir.glob(f"**/*{ext}")
        existing_images.extend([file_path.name for file_path in existing_image_gen])
    ic(len(existing_images))

    unclassified_image_names = [image_name for image_name in valid_images if image_name not in existing_images]
    ic(len(unclassified_image_names))

    try:
        image_name = choice(unclassified_image_names)
        encoded_image_name = urllib.parse.quote(image_name)
        current_image_path = os.path.join(app.config["UNCLASSIFIED_DATASET"], f"{image_name}")
    except IndexError:
        all_images_done = True

    categories = config[decoded_dataset_name]
    encoded_categories=[urllib.parse.quote(category) for category in categories]
    categories_count = len(categories)

    return render_template(
        "classification.html", 
        all_images_done=all_images_done,
        current_image=current_image_path,
        categories_count=categories_count,
        categories=categories,
        # script vars
        image_name=image_name,
        encoded_categories=encoded_categories,
        dataset_name=encoded_dataset_name,
        encoded_image_name=encoded_image_name,
    )


@app.route("/classify/<dataset_name>/<cat_id>/<image_name>")
def set_category(dataset_name, cat_id, image_name):
    dataset_name = urllib.parse.unquote(dataset_name)
    cat_id = urllib.parse.unquote(cat_id)
    image_name = urllib.parse.unquote(image_name)

    unclassified_dataset_dir = os.path.join(os.getcwd(), "static", "unclassified_dataset")
    dataset_dir = os.path.join(os.getcwd(), "Dataset", dataset_name,)
    os.makedirs(dataset_dir, exist_ok=True)

    cat_id_dir = os.path.join(dataset_dir, cat_id)
    os.makedirs(cat_id_dir, exist_ok=True)

    src_image_path = os.path.join(unclassified_dataset_dir, image_name)
    dst_image_path = os.path.join(cat_id_dir, image_name)

    shutil.copyfile(src_image_path, dst_image_path)
    
    return "Done!"
