"""
PicScan - CNN vs ResNet-56 Comparison
=========================================
Runs both models on every upload. Saves the winning model's top-4
predictions to the database (same shape as before, so views.py and
the Prediction model don't need to change), and also returns a
comparison dict for display on the result page.

Accepts a wide range of common image formats.
"""

import os
from functools import lru_cache

import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CLASSES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
]

# Broad set of common image formats. Note: HEIC (default iPhone photo
# format) is NOT included here - Pillow can't open it without an extra
# library (pillow-heif). If you need HEIC support, install that
# separately and add "heic"/"heif" to this set.
ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "jfif", "png", "webp", "bmp",
    "gif", "tiff", "tif", "ico", "pgm", "ppm",
}

# Shown on the form page as before
MODEL_ACCURACY = 87.32  # your CNN's verified test accuracy


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Load both models once, when this module is first imported
# ---------------------------------------------------------------------------
CNN_MODEL_PATH = os.path.join(BASE_DIR, "picscan_best_model.keras")
@lru_cache(maxsize=1)
def get_cnn_model():
    return load_model(CNN_MODEL_PATH)


@lru_cache(maxsize=1)
def get_resnet_model():
    model = torch.hub.load(
        "chenyaofo/pytorch-cifar-models", "cifar10_resnet56", pretrained=True
    )
    model.eval()
    return model

resnet_transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),
        std=(0.247, 0.243, 0.261),
    ),
])


def _load_as_rgb(filename):
    """
    Opens ANY Pillow-supported image format (jpg, png, webp, bmp, gif,
    tiff, etc.) and converts it to RGB. This handles images that are
    grayscale, have a transparency channel (RGBA), or are palette-based
    (like some PNGs/GIFs) - all normalized to plain RGB before the
    models ever see them.
    """
    with Image.open(filename) as img:
        return img.convert("RGB")


# ---------------------------------------------------------------------------
# Individual model predictions - each returns top-4 classes + probabilities
# ---------------------------------------------------------------------------
def _predict_cnn_top4(filename):
    img = _load_as_rgb(filename).resize((32, 32))
    img = img_to_array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    predictions = get_cnn_model().predict(img, verbose=0)[0]
    top_indices = np.argsort(predictions)[::-1][:4]

    top_classes = [CLASSES[i] for i in top_indices]
    top_probs = [round(float(predictions[i]) * 100, 2) for i in top_indices]
    return top_classes, top_probs


def _predict_resnet_top4(filename):
    img = _load_as_rgb(filename)
    img_tensor = resnet_transform(img).unsqueeze(0)

    with torch.no_grad():
        outputs = get_resnet_model()(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]

    top_indices = torch.argsort(probabilities, descending=True)[:4]

    top_classes = [CLASSES[i] for i in top_indices]
    top_probs = [round(float(probabilities[i]) * 100, 2) for i in top_indices]
    return top_classes, top_probs


# ---------------------------------------------------------------------------
# Main entry point - matches the original predict(filename) signature
# ---------------------------------------------------------------------------
def predict(filename):
    """
    Returns (class_result, prob_result, comparison):
      - class_result, prob_result: top-4 from the WINNING model
        (same shape as before, so process_and_save_prediction and the
        Prediction model don't need to change)
      - comparison: dict with both models' top prediction + confidence,
        for display only (not saved to the database)
    """
    cnn_classes, cnn_probs = _predict_cnn_top4(filename)
    resnet_classes, resnet_probs = _predict_resnet_top4(filename)

    cnn_top1 = {"model_name": "Custom CNN", "predicted_class": cnn_classes[0], "confidence": cnn_probs[0]}
    resnet_top1 = {"model_name": "ResNet-56 (pretrained)", "predicted_class": resnet_classes[0], "confidence": resnet_probs[0]}

    comparison = {
        "results": sorted([cnn_top1, resnet_top1], key=lambda r: r["confidence"], reverse=True),
    }
    comparison["winner_model"] = comparison["results"][0]["model_name"]
    comparison["winner_class"] = comparison["results"][0]["predicted_class"]
    comparison["winner_confidence"] = comparison["results"][0]["confidence"]

    if comparison["winner_model"] == "Custom CNN":
        class_result, prob_result = cnn_classes, cnn_probs
    else:
        class_result, prob_result = resnet_classes, resnet_probs

    return class_result, prob_result, comparison
