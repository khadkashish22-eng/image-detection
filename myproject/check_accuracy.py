"""
Check the real accuracy of the ResNet-56 model on CIFAR-10's official test set.
==================================================================================
Run this from your terminal (same environment where torch is installed):

    python check_accuracy.py

This downloads CIFAR-10's test set (10,000 images, ~170MB, one-time download)
and runs every image through the model, then prints the final accuracy.
Takes a few minutes on CPU. No Django/server needed for this -- it's a
standalone check.
"""

import torch
from torchvision import datasets, transforms

print("Loading model (uses cached weights if already downloaded)...")
model = torch.hub.load(
    "chenyaofo/pytorch-cifar-models", "cifar10_resnet56", pretrained=True
)
model.eval()

# Must match naive.py's preprocessing exactly.
transform = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize(
            mean=(0.4914, 0.4822, 0.4465),
            std=(0.247, 0.243, 0.261),
        ),
    ]
)

print("Downloading/loading CIFAR-10 test set (10,000 images)...")
test_set = datasets.CIFAR10(
    root="./data", train=False, download=True, transform=transform
)
test_loader = torch.utils.data.DataLoader(test_set, batch_size=256, shuffle=False)

correct = 0
total = 0

print("Running predictions...")
with torch.no_grad():
    for batch_idx, (images, labels) in enumerate(test_loader):
        outputs = model(images)
        predicted = outputs.argmax(dim=1)
        correct += (predicted == labels).sum().item()
        total += labels.size(0)
        print(f"  Batch {batch_idx + 1}/{len(test_loader)} -- running accuracy: "
              f"{100 * correct / total:.2f}%")

final_accuracy = 100 * correct / total
print(f"\nFinal accuracy on CIFAR-10 test set: {final_accuracy:.2f}%")
print(f"Correct: {correct} / {total}")