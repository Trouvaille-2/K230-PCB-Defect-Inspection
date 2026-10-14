import os
import glob
import cv2
import numpy as np
# 1. 注入 .NET 7.0 运行时环境
os.environ['DOTNET_ROOT'] = os.path.expanduser('~/.dotnet')
import nncase
print(">>> [1/5] 初始化 nncase 编译器 (目标平台: K230)...")
compile_options = nncase.CompileOptions()
compile_options.target = "k230"
compile_options.dump_ir = False
compile_options.dump_asm = False
compile_options.dump_dir = "tmp"
compiler = nncase.Compiler(compile_options)
print(">>> [2/5] 导入真实 PCB 计算图 (pcb_best.onnx)...")
import_options = nncase.ImportOptions()
with open("../models/pcb_best.onnx", "rb") as f:
    compiler.import_onnx(f.read(), import_options)
print(">>> [3/5] 加载验证集真实 PCB 图像构建校准集...")
val_images = glob.glob("../datasets/PCB_YOLO/images/val/*.jpg")[:5]
calib_data = []
for img_path in val_images:
    img = cv2.imread(img_path)
    img = cv2.resize(img, (320, 320))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0  # 归一化到 [0, 1]
    img = np.transpose(img, (2, 0, 1))    # HWC -> CHW (3, 320, 320)
    img = np.expand_dims(img, axis=0)     # (1, 3, 320, 320)
    calib_data.append(img)
print(f"    成功加载 {len(calib_data)} 张真实 PCB 样本进行激活值分布校准！")
ptq_options = nncase.PTQTensorOptions()
ptq_options.set_tensor_data([calib_data])
print(">>> [4/5] 启动 PTQ 硬件算子融合与 INT8 量化编译 (请稍候)...")
compiler.use_ptq(ptq_options)
compiler.compile()
print(">>> [5/5] 导出最终目标硬件二进制文件...")
kmodel_bytes = compiler.gencode_tobytes()
output_path = "../models/pcb_defect.kmodel"
with open(output_path, "wb") as f:
    f.write(kmodel_bytes)
size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"==================================================")
print(f"🎉 恭喜！PCB 缺陷检测专属模型编译完成: {output_path}")
print(f"🎉 最终模型体积: {size_mb:.2f} MB")
print(f"==================================================")