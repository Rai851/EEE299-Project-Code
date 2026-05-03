import torch
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from torchvision.models import MobileNet_V2_Weights

CATEGORIES = ['metal', 'paper', 'plastic']

# Data Augmentation বাড়ানো হয়েছে
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(30),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

dataset = datasets.ImageFolder(r"D:\pppppp\smart_dustbin\dataset-resized", transform=train_transform)

# Train/Validation split
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_data, val_data = torch.utils.data.random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
val_loader   = DataLoader(val_data, batch_size=32, shuffle=False)

# Model
model = models.mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
model.classifier[1] = torch.nn.Linear(1280, len(CATEGORIES))

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
criterion = torch.nn.CrossEntropyLoss()

best_acc = 0
print("🚀 Training শুরু হচ্ছে...")

for epoch in range(30):  # 30 epoch
    # Training
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)

    train_acc = 100. * correct / total

    # Validation
    model.eval()
    val_correct = 0
    val_total = 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            _, predicted = outputs.max(1)
            val_correct += predicted.eq(labels).sum().item()
            val_total += labels.size(0)

    val_acc = 100. * val_correct / val_total
    scheduler.step()

    print(f"Epoch {epoch+1}/30 — Loss: {total_loss:.2f} — Train: {train_acc:.1f}% — Val: {val_acc:.1f}%")

    # সবচেয়ে ভালো model save করো
    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), "waste_model.pth")
        print(f"💾 Best model saved! Val Accuracy: {val_acc:.1f}%")

print(f"✅ Training শেষ! Best Accuracy: {best_acc:.1f}%")