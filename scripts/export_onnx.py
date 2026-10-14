from ultralytics import YOLO
import onnx

model = YOLO("yolov8n.pt")

model.export(
	format="onnx",
	imgsz=320,
	dynamic=False,
	opset=12,
	simplify=True
)

onnx_model = onnx.load("yolov8n.onnx")

for node in onnx_model.graph.input:
    shape = [d.dim_value for d in node.type.tensor_type.shape.dim]
    print("模型输入节点维度:", shape)
    
for node in onnx_model.graph.output:
    shape = [d.dim_value for d in node.type.tensor_type.shape.dim]
    print("模型输出节点维度:", shape)