"""
PicScan - ResNet-56 Quick Training Script (CIFAR-10, PyTorch)
=================================================================
Simplified, short version — real ResNet-56 architecture, fewer epochs
(15 instead of 100), so you get an honest, complete training run with
real logs and real accuracy in ~15-25 minutes on a free Colab GPU.

Runtime -> Change runtime type -> GPU, before running this.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

class_names = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck",
]

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
CIFAR_MEAN = (0.4914, 0.4822, 0.4465)
CIFAR_STD = (0.2470, 0.2435, 0.2616)

train_transform = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(CIFAR_MEAN, CIFAR_STD),
])
test_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(CIFAR_MEAN, CIFAR_STD),
])

train_dataset = torchvision.datasets.CIFAR10(root="./data", train=True, download=True, transform=train_transform)
test_dataset = torchvision.datasets.CIFAR10(root="./data", train=False, download=True, transform=test_transform)

train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=2)
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False, num_workers=2)

# ---------------------------------------------------------------------------
# ResNet-56 architecture (same real CIFAR-ResNet design as before)
# ---------------------------------------------------------------------------
class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride, bias=False),
                nn.BatchNorm2d(out_channels),
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        return F.relu(out)


class ResNetCIFAR(nn.Module):
    def __init__(self, num_blocks_per_stage, num_classes=10):
        super().__init__()
        self.in_channels = 16
        self.conv1 = nn.Conv2d(3, 16, 3, 1, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(16)
        self.stage1 = self._make_stage(16, num_blocks_per_stage, stride=1)
        self.stage2 = self._make_stage(32, num_blocks_per_stage, stride=2)
        self.stage3 = self._make_stage(64, num_blocks_per_stage, stride=2)
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(64, num_classes)

    def _make_stage(self, out_channels, num_blocks, stride):
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for s in strides:
            layers.append(BasicBlock(self.in_channels, out_channels, s))
            self.in_channels = out_channels
        return nn.Sequential(*layers)

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.stage1(out)
        out = self.stage2(out)
        out = self.stage3(out)
        out = self.avgpool(out)
        out = torch.flatten(out, 1)
        return self.fc(out)


def resnet56(num_classes=10):
    return ResNetCIFAR(num_blocks_per_stage=9, num_classes=num_classes)  # depth = 6*9+2 = 56


model = resnet56().to(device)
print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")

# ---------------------------------------------------------------------------
# Training setup — simplified: Adam (converges faster in few epochs than
# SGD, which needs more epochs to shine), no LR scheduler needed for a
# short run like this.
# ---------------------------------------------------------------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

EPOCHS = 15  # short run — honest, complete, quick

# ---------------------------------------------------------------------------
# Training loop
# ---------------------------------------------------------------------------
for epoch in range(1, EPOCHS + 1):
    # ---- train ----
    model.train()
    train_loss, correct, total = 0.0, 0, 0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        train_loss += loss.item() * images.size(0)
        correct += outputs.argmax(1).eq(labels).sum().item()
        total += labels.size(0)
    train_acc = 100.0 * correct / total

    # ---- evaluate ----
    model.eval()
    test_correct, test_total = 0, 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            test_correct += outputs.argmax(1).eq(labels).sum().item()
            test_total += labels.size(0)
    test_acc = 100.0 * test_correct / test_total

    print(f"Epoch {epoch:2d}/{EPOCHS} | Train acc: {train_acc:.2f}% | Test acc: {test_acc:.2f}%")

    # Save after EVERY epoch — so if you stop early (Ctrl+C, laptop needs
    # to shut down, etc.), you still have a real, usable model file and
    # real logs from whatever epochs actually completed. Nothing is lost.
    torch.save(model.state_dict(), "resnet56_quick.pth")
    print(f"  -> Checkpoint saved (epoch {epoch} complete)")

# ---------------------------------------------------------------------------
# Training complete
# ---------------------------------------------------------------------------
print(f"\nFinal test accuracy: {test_acc:.2f}%")
print("Model saved to resnet56_quick.pth")