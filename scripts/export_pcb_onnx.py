from ultralytics import YOLO
import onnx
print(">>> [1/3] 加载 PCB 专属权重 best.pt...")
# 注意训练输出的实际路径
model = YOLO("runs/runs/pcb_v8n_320/weights/best.pt")
print(">>> [2/3] 导出为 K230 静态计算图 (320x320, opset=12)...")
success = model.export(
    format="onnx",
    imgsz=320,
    dynamic=False,
    opset=12,
    simplify=True
)
print(f">>> [3/3] 导出成功！移动到 models/ 目录...")
import os
os.system("mv runs/runs/pcb_v8n_320/weights/best.onnx ../models/pcb_best.onnx")
onnx_model = onnx.load("../models/pcb_best.onnx")
for node in onnx_model.graph.output:
    shape = [d.dim_value for d in node.type.tensor_type.shape.dim]
    print(f"    [PCB 模型输出节点] 形状: {shape}")