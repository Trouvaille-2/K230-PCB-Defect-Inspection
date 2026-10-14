# 🔍 K230-PCB-Defect-Inspection
> **基于 K230 边缘 AI (RISC-V) 与 Ubuntu Qt C++ 工业质检上位机的 PCB 表面缺陷智能检测系统**  
> *An Industrial PCB Surface Defect Inspection System Based on CanMV-K230 Edge AI (RISC-V) and Ubuntu Qt C++ Station.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: K230 RISC-V](https://img.shields.io/badge/Hardware-CanMV--K230-orange.svg)](https://www.canaan-creative.com/)
[![Framework: nncase](https://img.shields.io/badge/Compiler-nncase_v2.11-green.svg)](https://github.com/kendryte/nncase)
[![UI: Qt 6 C++](https://img.shields.io/badge/UI-Qt_6_C%2B%2B-blueviolet.svg)](https://www.qt.io/)

---

## 📌 项目概述 (Overview)

针对传统工业 PCB 表面微小缺陷人工目视检测效率低、漏检率高，以及传统工控机方案成本昂贵、体积笨重的问题，本项目设计并实现了一套**面向工业现场的“低功耗边缘端实时推理 + 中央工控监控大屏”的端到端软硬件闭环质检系统**。

### 🌟 核心亮点 (Highlights)
1. **工业级 6 类缺陷精准覆盖**：基于北京大学开源 **DeepPCB** 数据集，针对短路（short）、开路（open）、毛刺（spur）等 6 类常见微米级缺陷优化。
2. **边缘极致能效比 (Edge Acceleration)**：搭载平头哥玄铁双核 RISC-V 架构芯片 **CanMV-K230**，调用硬件专属 **6.0 TOPS KPU 加速器**，实现满帧实时前向推理（延迟 $\le 20\text{ms}$，帧率可达 35~50 FPS）。
3. **模型深度量化压缩 (INT8 PTQ)**：基于嘉楠官方 **`nncase 2.11`** 编译工具链，采用真实生产样本进行激活值动态分布校准，将 13MB 的 FP32 ONNX 压缩为 **3.32MB 的专属硬件 `.kmodel` 二进制文件**，内存带宽压力缩减 **75%**，精度损失 $< 2\%$。
4. **全链路工业通信与 Qt 上位机**：基于 Linux POSIX Socket / 串口设计工业帧报文（包头+长度+数据体+CRC16校验），在 Ubuntu 环境下采用 **现代 C++ / Qt 6** 架构工业质检看板，多线程异步渲染缺陷打框、实时良品率统计与数据追溯。

---

## 🏗️ 系统全景架构 (Architecture Pipeline)第一阶段：PC 端模型迁移学习 │ │ DeepPCB 工业数据集 (1500+张样本) ➔ YOLOv8n (320x320) ➔ 产出 best.pt │ └───────────────────────────────────┬────────────────────────────────────┘ │ ▼ ┌────────────────────────────────────────────────────────────────────────┐ │ 第二阶段：计算图规范化与 INT8 量化编译 │ │ best.pt ➔ 静态计算图 (pcb_best.onnx [1, 10, 2100]) │ │ │ │ │ ▼ (nncase 2.11 工具链 + 真实 PCB 样本激活值分布校准) │ │ pcb_defect.kmodel (专属硬件二进制, 体积仅 3.32 MB) │ └───────────────────────────────────┬────────────────────────────────────┘ │ ▼ ┌────────────────────────────────────────────────────────────────────────┐ │ 第三阶段：K230 边缘端推理与通信 (Edge Linux C++) │ │ GC2093 工业摄像头采集 ➔ KPU 硬件推理 (15~20ms) ➔ NMS 坐标解算 ➔ TCP/串口推流 │ └───────────────────────────────────┬────────────────────────────────────┘ │ 工业私有协议帧 (含 CRC16 防粘包) ▼ ┌────────────────────────────────────────────────────────────────────────┐ │ 第四阶段：Ubuntu C++ Qt 工业质检上位机 │ │ QThread 异步网络通信 ➔ QPainter 毫秒级缺陷打框 ➔ QCustomPlot 动态大屏看板 │

---

## 📊 模型与性能指标 (Performance & Benchmarks)

| 指标维度 | PC 原始模型 (PyTorch) | 通用计算图 (ONNX) | K230 专属硬件模型 (kmodel) |
| :--- | :---: | :---: | :---: |
| **精度格式** | FP32 | FP32 | **INT8 (PTQ)** |
| **文件大小** | 6.2 MB | 12.1 MB | **3.32 MB (压缩 75%)** |
| **输入尺寸** | 320 × 320 | 320 × 320 (静态) | 320 × 320 (静态) |
| **输出张量** | [1, 10, 2100] | [1, 10, 2100] | 专属算子流 |
| **推理延迟** | - | - | **$\sim 18\text{ms}$ (35~50 FPS)** |
| **功耗** | 几百瓦 (GPU) | - | **$< 2\text{W}$ (极低功耗)** |

### 检测缺陷类别定义：
- `0: missing_hole` (缺孔)
- `1: mouse_bite` (鼠咬)
- `2: open_circuit` (开路)
- `3: short` (短路)
- `4: spur` (毛刺)
- `5: spurious_copper` (多余铜/铜渣)

---

## 📂 项目工程目录 (Repository Structure)

```text
├── models/
│   ├── pcb_best.onnx             # 静态规整计算图 (12.1 MB)
│   └── pcb_defect.kmodel         # K230 KPU 专属 INT8 硬件量化模型 (3.32 MB)
├── scripts/
│   ├── train_pcb.py              # DeepPCB 工业数据集轻量迁移学习训练脚本
│   ├── export_pcb_onnx.py        # 针对 KPU 优化的静态 ONNX 计算图导出脚本
│   └── compile_pcb_kmodel.py     # Canaan nncase INT8 真实样本 PTQ 量化编译脚本
├── edge_app/                     # K230 板端 Linux C++ 推理与驱动工程 (开发中)
├── pc_qt_station/                # Ubuntu C++ Qt 6 工业监控上位机大屏工程 (开发中)
├── .gitignore                    # Git 规则文件 (已隔离庞大图像数据集与缓存)
└── README.md                     # 项目技术全景说明文档
快速上手 (Quick Start)
1. 宿主机环境依赖
操作系统：Ubuntu 22.04 / 24.04 / 26.04 LTS
运行时依赖：Microsoft .NET Runtime 7.0 (nncase 编译器底层引擎)
Python 环境：Python 3.10
依赖包：ultralytics, nncase==2.11.0, nncase-kpu==2.11.0, onnx, opencv-python
# 激活 Conda 独立环境
conda activate k230

# 1. 运行轻量迁移学习训练
python scripts/train_pcb.py

# 2. 导出适配硬件的规整静态 ONNX
python scripts/export_pcb_onnx.py

# 3. 执行 INT8 PTQ 硬件算子编译
python scripts/compile_pcb_kmodel.py
作者 (Author)
开发者：Meng Fanhua (孟凡华)
专业背景：山东农业大学 · 人工智能 / 嵌入式控制
研究兴趣：端侧 AI 部署 (Edge AI)、嵌入式 Linux C++、工业通信与运动控制 (Motion Control)
GitHub：@Trouvaille-2
本项目遵守 MIT License 开源协议。欢迎交流与 Star ⭐️！ EOF
