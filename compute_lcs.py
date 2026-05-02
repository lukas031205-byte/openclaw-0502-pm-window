#!/usr/bin/env python3
"""
TrACE-Video LCS (Latent Semantic Consistency) metric via DINOv2 L2 distance.
Uses torch.hub FacebookResearch dinov2 — confirmed working on this VM.

Usage:
    python3 compute_lcs.py image1.jpg image2.jpg
    python3 compute_lcs.py --batch images/ [--csv results.csv]

Output: L2 distance between DINOv2 L2-normalized features (lower = more semantically similar)
"""

import torch
from PIL import Image
import numpy as np
from torchvision import transforms
import argparse
import os
import sys

# Load DINOv2 once
print("Loading DINOv2 (ViT-B/14) from torch.hub...", file=sys.stderr)
model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitb14')
model.eval()
print("DINOv2 loaded ok", file=sys.stderr)

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

def load_and_transform(path):
    img = Image.open(path).convert('RGB')
    return transform(img).unsqueeze(0)

def compute_lcs(img1_path, img2_path):
    x1 = load_and_transform(img1_path)
    x2 = load_and_transform(img2_path)
    with torch.no_grad():
        f1 = model(x1)
        f2 = model(x2)
        f1 = f1 / f1.norm(dim=-1, keepdim=True)
        f2 = f2 / f2.norm(dim=-1, keepdim=True)
        l2_dist = (f1 - f2).norm(dim=-1).item()
    return l2_dist

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute TrACE-Video LCS metric via DINOv2 L2')
    parser.add_argument('img1', help='First image path')
    parser.add_argument('img2', help='Second image path')
    args = parser.parse_args()
    
    l2 = compute_lcs(args.img1, args.img2)
    print(f"{l2:.6f}")
