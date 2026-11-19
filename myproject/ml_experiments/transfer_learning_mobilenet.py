"""
PicScan - Transfer Learning: Fine-tuning MobileNetV2 on CIFAR-10
===================================================================
Uses a model pretrained on ImageNet (1.4 million images, 1000 categories)
and fine-tunes it for our 10 CIFAR-10 categories.

Two-stage approach:
  Stage 1: Freeze the pretrained base, train only our new classifier head.
  Stage 2: Unfreeze the top portion of the base and fine-tune everything
           together at a lower learning rate for extra accuracy.

Requirements: tensorflow >= 2.15
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np

SEED = 42
tf.random.set_seed(SEED)
np.random.seed(SEED)

(x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()

y_train = y_train.squeeze()
y_test = y_test.squeeze()

class_names = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
]

print(f"Train: {x_train.shape}, Test: {x_test.shape}")

IMG_SIZE = 96

resize_and_rescale = keras.Sequential([
    layers.Resizing(IMG_SIZE, IMG_SIZE),
], name="resize")

data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.05),
    layers.RandomZoom(0.1),
], name="data_augmentation")

base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights="imagenet",
)

base_model.trainable = False

inputs = keras.Input(shape=(32, 32, 3))
x = resize_and_rescale(inputs)
x = data_augmentation(x)
x = preprocess_input(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(10, activation="softmax")(x)

model = keras.Model(inputs, outputs, name="picscan_transfer_mobilenetv2")
model.summary()

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss=keras.losses.SparseCategoricalCrossentropy(),
    metrics=["accuracy"],
)

callbacks = [
    keras.callbacks.ModelCheckpoint(
        filepath="picscan_transfer_best.keras",
        monitor="val_loss",
        save_best_only=True,
        verbose=1,
    ),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1,
    ),
    keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=8,
        restore_best_weights=True,
        verbose=1,
    ),
]

print("\n--- Stage 1: training classifier head (base model frozen) ---\n")

history_stage1 = model.fit(
    x_train,
    y_train,
    batch_size=64,
    epochs=15,
    validation_split=0.1,
    callbacks=callbacks,
    verbose=1,
)

print("\n--- Stage 2: fine-tuning top layers of MobileNetV2 ---\n")

base_model.trainable = True

fine_tune_at = len(base_model.layers) - 30
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-5),
    loss=keras.losses.SparseCategoricalCrossentropy(),
    metrics=["accuracy"],
)

history_stage2 = model.fit(
    x_train,
    y_train,
    batch_size=64,
    epochs=15,
    validation_split=0.1,
    callbacks=callbacks,
    verbose=1,
)

test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print("\n====================================")
print("TRANSFER LEARNING FINAL RESULTS")
print("====================================")
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {test_acc * 100:.2f}%")

model.save("picscan_transfer_final.keras")
print("\nModel saved as picscan_transfer_final.keras")