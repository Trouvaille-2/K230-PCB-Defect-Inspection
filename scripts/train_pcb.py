from ultralytics import YOLO
print(">>> [步骤1] 加载轻量级 YOLOv8n 预训练权重作为底座骨架...")
model = YOLO("../models/yolov8n.pt")
print(">>> [步骤2] 启动 PCB 缺陷数据集迁移学习训练...")
# 超参数针对边缘部署优化:
# - data: 数据集配置文件路径
# - epochs: 训练轮数 (先以 10 轮验证全流程闭环)
# - imgsz: 320x320 严格对齐 K230 KPU 最佳吞吐尺寸
# - batch: 8
# - workers: 2
# - project: 结果保存目录
results = model.train(
    data="../datasets/PCB_YOLO/data.yaml",
    epochs=10,
    imgsz=320,
    batch=8,
    workers=2,
    project="../runs",
    name="pcb_v8n_320",
    exist_ok=True
)
print(">>> [步骤3] 训练顺利完成！最优权重已生成在: ../runs/pcb_v8n_320/weights/best.pt")