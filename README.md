# OptiThick-AI
Adaptive optical thin-film thickness measurement system using RGB space vector fitting and exposure compensation. Features multi-image learning, precision crosshair query, and substrate-aware auto-analysis.
# OptiThick-AI: Adaptive Optical Thin-Film Thickness Analysis System
# OptiThick-AI: 自适应光学薄膜厚度分析系统

OptiThick-AI is a high-precision tool for measuring the thickness of thin films using RGB color space vector fitting and adaptive exposure compensation. Unlike traditional Hue-based methods, this system overcomes the discontinuity of color cycles and is robust against varying lighting conditions.

OptiThick-AI 是一款利用 RGB 空间向量拟合和自适应曝光补偿技术，实现高精度薄膜厚度测量的工具。与传统的基于 Hue（色调）的方法不同，本系统克服了颜色周期不连续的问题，并能有效抵抗不同光照条件带来的干扰。

---

## ✨ Key Features / 主要功能

* **Adaptive Exposure Compensation**: Learners the substrate baseline from training images and automatically scales target images to match the same exposure level.
    * **自适应曝光补偿**：从学习图像中提取衬底基准，自动缩放待测图像，确保曝光一致性。
* **RGB Space k-NN Fitting**: Uses 3D Euclidean distance instead of 1D Hue to avoid color jump discontinuities.
    * **RGB 空间 k-NN 拟合**：采用三维欧氏距离代替一维色调，完美解决颜色循环跳变问题。
* **Dual-Logic Workflow**: Separate modes for "Database Learning" and "Active Measurement".
    * **双逻辑工作流**：将“数据库学习”与“实际测量分析”逻辑分离，专业高效。
* **Substrate-Aware Averaging**: Smartly excludes substrate regions to calculate the precise average thickness of the sample.
    * **衬底自动剔除**：在计算平均高度时智能识别并剔除衬底区域，仅分析样品。
* **Crosshair Precision**: Real-time crosshair cursor for pinpointing micro-scale features.
    * **十字准心测量**：实时红色准心随动，实现微观区域的精准取点。

---

## 🚀 Installation / 安装说明

1. **Clone the repository / 克隆仓库**:
   ```bash
   git clone [https://github.com/yourusername/OptiThick-AI.git](https://github.com/yourusername/OptiThick-AI.git)
   cd OptiThick-AI
2. **Install dependencies / 安装依赖**:
   Ensure you have Python 3.10+ installed. Then run:
   ```bash
   pip install opencv-python pandas numpy scikit-learn matplotlib
