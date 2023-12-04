import os
import json
from pathlib import Path
from flask import Flask, render_template, Response
from random import choice
import shutil
from loguru import logger as log
from icecream import ic


app = Flask(__name__)
app.config["UNCLASSIFIED_DATASET"] = os.path.join("static", "unclassified_dataset")

valid_extension = 'jpg'


@app.route("/")
def home():
    config_file_path = os.path.join(os.getcwd(), "datasets.json")
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    
    dataset_names = config.keys()
    dataset_names = [str(dataset_name) for dataset_name in dataset_names]
    dataset_count = len(dataset_names)

    return render_template(
        "home.html",
        dataset_count=dataset_count,
        dataset_names=dataset_names,
    )


@app.route("/<dataset_name>")
def classifier(dataset_name):
    config_file_path = os.path.join(os.getcwd(), "datasets.json")
    with open(config_file_path, 'r') as f:
        config = json.load(f)

    all_images_done = False
    current_image_path = False
    image_name = False

    unclassified_dataset_dir = Path(Path.cwd(), "static", "unclassified_dataset")
    valid_images = [file_path.name for file_path in unclassified_dataset_dir.iterdir() if file_path.suffix != valid_extension]
    # valid_images = unclassified_dataset_dir.glob(f'*.{valid_extension}')
    ic(len(valid_images))
    
    dataset_dir = Path(os.getcwd(), "Dataset", dataset_name,)
    existing_images_gen = dataset_dir.glob(f'**/*.{valid_extension}')
    existing_images = [image_path.name for image_path in existing_images_gen]
    ic(len(existing_images))
    
    image_names = [image_name for image_name in valid_images if image_name not in existing_images]
    ic(len(image_names))
    try:
        image_name = choice(image_names)
        current_image_path = os.path.join(app.config["UNCLASSIFIED_DATASET"], f"{image_name}")
    except IndexError:
        all_images_done = True

    categories = config[dataset_name]
    categories_count = len(categories)

    return render_template(
        "classification.html", 
        all_images_done=all_images_done,
        current_image=current_image_path,
        image_name=image_name,
        categories=categories,
        categories_count=categories_count,
        dataset_name=dataset_name,
    )


@app.route("/<dataset_name>/<cat_id>/<image_name>")
def set_category(dataset_name, cat_id, image_name):

    unclassified_dataset_dir = os.path.join(os.getcwd(), "static", "unclassified_dataset")
    dataset_dir = os.path.join(os.getcwd(), "Dataset", dataset_name,)
    os.makedirs(dataset_dir, exist_ok=True)

    cat_id_dir = os.path.join(dataset_dir, cat_id)
    os.makedirs(cat_id_dir, exist_ok=True)

    src_image_path = os.path.join(unclassified_dataset_dir, image_name)
    dst_image_path = os.path.join(cat_id_dir, image_name)

    shutil.copyfile(src_image_path, dst_image_path)    
    
    return "Done!"
