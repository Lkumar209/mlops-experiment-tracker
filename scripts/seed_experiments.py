#!/usr/bin/env python3
"""Seed 50 experiments with realistic names and tags."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.app.extensions import db
from backend.app.models.experiment import Experiment

EXPERIMENT_NAMES = [
    "ResNet-50 Ablation Study",
    "BERT Fine-tune v3",
    "GPT-2 Domain Adaptation",
    "Vision Transformer ViT-B/16",
    "EfficientNet-B4 Transfer",
    "LSTM Sequence Labeling",
    "Attention U-Net Segmentation",
    "XGBoost Hyperparameter Grid",
    "Transformer NER Fine-tune",
    "MobileNetV3 Quantization",
    "CLIP Zero-Shot Evaluation",
    "Stable Diffusion LoRA",
    "Whisper ASR Fine-tune",
    "DenseNet-121 CXR",
    "YOLOv8 Object Detection",
    "DeepLabV3+ Semantic Seg",
    "FastText Embedding Training",
    "BERT Sentence Similarity",
    "Random Forest Ensemble",
    "GAN Image Synthesis",
    "Autoencoder Anomaly Detection",
    "T5 Summarization Fine-tune",
    "Contrastive Learning SimCLR",
    "DistilBERT Distillation",
    "ResNet-101 Food Classification",
    "Wav2Vec2 Speech Fine-tune",
    "LLaMA-7B LoRA Fine-tune",
    "TabNet Tabular Classification",
    "DETR Object Detection",
    "ConvNeXt-Tiny ImageNet",
    "Swin Transformer Classification",
    "SAM Segmentation Prompt",
    "BEiT Pre-training",
    "MAE Masked Autoencoding",
    "DINO Self-Supervised",
    "RoBERTa Sentiment Analysis",
    "AlexNet Baseline Comparison",
    "VGG-16 Feature Extraction",
    "Inception-v4 Multi-label",
    "MLP Mixer Patch Embedding",
    "Perceiver IO Multimodal",
    "Mamba State Space Model",
    "Flamingo VLM Eval",
    "LLaVA Multimodal Chat",
    "Codex Code Generation",
    "PaLM-E Embodied Agent",
    "OpenCLIP Retrieval",
    "Segment Anything SAM2",
    "Grounding DINO Zero-Shot",
    "DALL-E 3 Prompt Study",
]

TAG_SETS = [
    {"domain": "cv", "task": "classification"},
    {"domain": "nlp", "task": "fine-tuning"},
    {"domain": "cv", "task": "segmentation"},
    {"domain": "nlp", "task": "generation"},
    {"domain": "multimodal", "task": "retrieval"},
    {"domain": "cv", "task": "detection"},
    {"domain": "nlp", "task": "embedding"},
    {"domain": "tabular", "task": "classification"},
    {"domain": "audio", "task": "asr"},
    {"domain": "rl", "task": "policy"},
]


def seed():
    app = create_app()
    with app.app_context():
        for i, name in enumerate(EXPERIMENT_NAMES):
            existing = db.session.query(Experiment).filter_by(name=name).first()
            if existing:
                print(f"  Skipping existing: {name}")
                continue

            tags = TAG_SETS[i % len(TAG_SETS)]
            exp = Experiment(name=name, description=f"Experiment: {name}", tags=tags)
            db.session.add(exp)

        db.session.commit()
        total = db.session.query(Experiment).count()
        print(f"Seeded experiments. Total: {total}")


if __name__ == "__main__":
    seed()
