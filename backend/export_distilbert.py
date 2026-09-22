import os
import torch
from transformers import AutoModelForSequenceClassification
from onnxruntime.quantization import quantize_dynamic, QuantType

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
WEIGHTS_PATH = os.path.join(MODEL_DIR, "distilbert_best.pt")
ONNX_OUTPUT = os.path.join(MODEL_DIR, "distilbert_phishing.onnx")
ONNX_QUANTIZED = os.path.join(MODEL_DIR, "distilbert_phishing_int8.onnx")

print("Loading DistilBERT architecture...")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

if os.path.exists(WEIGHTS_PATH):
    print(f"Loading trained weights from {WEIGHTS_PATH}...")
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
else:
    print("No trained weights found, using base weights.")

model.eval()

dummy_input_ids = torch.ones(1, 128, dtype=torch.long)
dummy_attention_mask = torch.ones(1, 128, dtype=torch.long)

print("Exporting with TorchScript exporter (dynamo=False)...")
torch.onnx.export(
    model,
    (dummy_input_ids, dummy_attention_mask),
    ONNX_OUTPUT,
    export_params=True,
    opset_version=14,
    do_constant_folding=True,
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch_size"},
        "attention_mask": {0: "batch_size"},
        "logits": {0: "batch_size"}
    },
    dynamo=False
)

size_mb = os.path.getsize(ONNX_OUTPUT) / (1024 * 1024)
print(f"Exported {ONNX_OUTPUT} ({size_mb:.1f} MB)")

print("Applying INT8 quantization...")
quantize_dynamic(
    ONNX_OUTPUT,
    ONNX_QUANTIZED,
    weight_type=QuantType.QInt8
)
q_size_mb = os.path.getsize(ONNX_QUANTIZED) / (1024 * 1024)
print(f"Quantized {ONNX_QUANTIZED} ({q_size_mb:.1f} MB)")
print("ALL DONE!")
