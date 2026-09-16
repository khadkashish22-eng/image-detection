"""
PicScan - CNN vs ResNet-56 Live Comparison
==============================================
Runs an uploaded image through BOTH models and returns the prediction
from whichever one is more confident. Displays both results so the
UI can show the comparison, with the winner highlighted.

Models used:
  1. Your own custom CNN (picscan_best_model.keras) - trained from scratch
  2. Pretrained ResNet-56 (via torch.hub, chenyaofo/pytorch-cifar-models) -
     94.37% verified accuracy on CIFAR-10, not trained by you

Requirements: pip install torch torchvision joblib
"""

import os
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

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "jfif", "webp", "bmp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Load both models once, when this module is first imported
# ---------------------------------------------------------------------------
CNN_MODEL_PATH = os.path.join(BASE_DIR, "picscan_best_model.keras")
cnn_model = load_model(CNN_MODEL_PATH)

# torch.hub caches the downloaded weights locally after the first run,
# so this is fast on every run after the very first one.
resnet_model = torch.hub.load(
    "chenyaofo/pytorch-cifar-models",
    "cifar10_resnet56",
    pretrained=True,
)
resnet_model.eval()  # inference mode - disables dropout/batchnorm updates

# Exact normalization values this specific pretrained model was trained with
resnet_transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=(0.4914, 0.4822, 0.4465),
        std=(0.247, 0.243, 0.261),
    ),
])


# ---------------------------------------------------------------------------
# Predict with the custom CNN
# ---------------------------------------------------------------------------
def predict_cnn(filename):
    img = load_img(filename, target_size=(32, 32))
    img = img_to_array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    predictions = cnn_model.predict(img, verbose=0)[0]
    top_index = int(np.argmax(predictions))

    return {
        "model_name": "Custom CNN",
        "predicted_class": CLASSES[top_index],
        "confidence": round(float(predictions[top_index]) * 100, 2),
    }


# ---------------------------------------------------------------------------
# Predict with the pretrained ResNet-56
# ---------------------------------------------------------------------------
def predict_resnet(filename):
    img = Image.open(filename).convert("RGB")
    img_tensor = resnet_transform(img).unsqueeze(0)  # add batch dimension

    with torch.no_grad():
        outputs = resnet_model(img_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]

    top_index = int(torch.argmax(probabilities))

    return {
        "model_name": "ResNet-56 (pretrained)",
        "predicted_class": CLASSES[top_index],
        "confidence": round(float(probabilities[top_index]) * 100, 2),
    }


# ---------------------------------------------------------------------------
# Compare both, return whichever is more confident
# ---------------------------------------------------------------------------
def predict(filename):
    """
    Runs both models and returns a dict with both results, plus the
    winner (highest confidence) clearly marked - matching the shape
    your template can loop over and highlight.
    """
    cnn_result = predict_cnn(filename)
    resnet_result = predict_resnet(filename)

    results = [cnn_result, resnet_result]
    results.sort(key=lambda r: r["confidence"], reverse=True)

    winner = results[0]

    return {
        "results": results,               # both, sorted best-first
        "winner_model": winner["model_name"],
        "winner_class": winner["predicted_class"],
        "winner_confidence": winner["confidence"],
    }