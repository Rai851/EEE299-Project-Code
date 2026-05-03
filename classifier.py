import torch
import torchvision.transforms as transforms
from torchvision import models
from torchvision.models import MobileNet_V2_Weights
from PIL import Image

CATEGORIES = ['metal', 'paper', 'plastic']

class WasteClassifier:
    def __init__(self, model_path="waste_model.pth"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.model = models.mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
        self.model.classifier[1] = torch.nn.Linear(1280, len(CATEGORIES))
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        print(" Model loaded!")

        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])

    def predict(self, frame_rgb):
        img = Image.fromarray(frame_rgb)
        tensor = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            out = self.model(tensor)
            probs = torch.softmax(out, dim=1)[0]
            idx = probs.argmax().item()
            confidence = probs[idx].item()
        return CATEGORIES[idx], confidence
