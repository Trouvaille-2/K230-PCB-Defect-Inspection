import os
os.environ['DOTNET_ROOT'] = os.path.expanduser('~/.dotnet')
import numpy as np
import nncase

print(">>>[步骤1]初始化nncase编译器...")
compile_options = nncase.CompileOptions()
# 目标硬件平台：K230
compile_options.target = "k230"
#编译优化等级：0~2
compile_options.dump_ir = False
compile_options.dump_asm = False
compile_options.dump_dir = "tmp"

compiler = nncase.Compiler(compile_options)
print(">>> [步骤2] 导入 ONNX 模型计算图...")
import_options = nncase.ImportOptions()
with open("../models/yolov8n.onnx", "rb") as f:
    compiler.import_onnx(f.read(), import_options)
print(">>> [步骤3] 配置 PTQ 训练后量化参数...")
calib_data = [np.random.rand(1, 3, 320, 320).astype(np.float32) for _ in range(5)]
ptq_options = nncase.PTQTensorOptions()
ptq_options.set_tensor_data([calib_data])
compiler.use_ptq(ptq_options)
compiler.compile()
print(">>> [步骤5] 导出 K230 专属 kmodel 二进制文件...")
kmodel_bytes = compiler.gencode_tobytes()
output_kmodel_path = "../models/yolov8n_k230.kmodel"
with open(output_kmodel_path, "wb") as f:
    f.write(kmodel_bytes)
kmodel_size_mb = os.path.getsize(output_kmodel_path) / (1024 * 1024)
print(f">>> [编译完成！] 目标文件已生成: {output_kmodel_path}")
print(f">>> 最终 kmodel 大小: {kmodel_size_mb:.2f} MB")