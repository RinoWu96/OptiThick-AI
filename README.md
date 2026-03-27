# OptiThick-AI: AFM-Calibrated Optical Thin-Film Analysis System
# OptiThick-AI: 基于 AFM 标定的光学薄膜厚度分析系统

**OptiThick-AI** is a high-precision metrology tool designed for 2D materials and semiconductor device research. It maps **Atomic Force Microscopy (AFM)** absolute height data to **Optical Microscopy RGB vector space**, enabling rapid, non-destructive, and wide-field thickness inversion.

**OptiThick-AI** 是一款专为二维材料及半导体器件研究设计的高精度测量工具。它通过建立 **AFM（原子力显微镜）** 绝对高度与 **光学显微镜 RGB 空间向量** 之间的非线性映射，实现全视野范围内的快速、无损、自动化厚度反演。

---

## ✨ Key Features / 核心特性

* **AFM-Optical Correlation / AFM-光学原位标定**: Uses AFM "ground truth" to calibrate optical colors, converting sensory RGB data into physical thickness (nm).
    * **AFM-光学原位标定**：利用 AFM 的“真理高度”为光学图像对色，将感官 RGB 数据转化为物理厚度 (nm)。
* **Adaptive Exposure Compensation / 自适应曝光补偿**: Automatically scales target images to match the database's exposure baseline by calibrating the substrate.
    * **自适应曝光补偿**：通过标定衬底自动缩放待测图像，消除因光源亮度或曝光时间不同导致的色差。
* **Smart Artifact Filtering / 智能干扰剔除**:
    * **Substrate & Electrode Masking**: Automatically excludes substrate and metal electrodes (e.g., Au, Ti) from average height calculations.
    * **智能干扰剔除**：在计算均值时自动识别并剔除衬底及金属电极（如金、钛）的反光干扰。
* **Quantitative Heatmaps / 定量高度热力图**: Generates independent pseudo-color maps to visualize full-field thickness distribution and growth uniformity.
    * **定量高度热力图**：一键生成独立伪彩色分布图，直观展现薄膜的生长均匀性或剥离梯度。
* **Crosshair Precision / 精准十字准心**: Real-time crosshair cursor for instantaneous thickness queries of micro-scale features.
    * **精准十字准心**：实时红细十字准心随动，支持微米级特征点的即时厚度点查。

---

## 🚀 Installation / 安装说明

1.  **Clone the repository / 克隆仓库**:
    ```bash
    git clone [https://github.com/yourusername/OptiThick-AI.git](https://github.com/yourusername/OptiThick-AI.git)
    cd OptiThick-AI
    ```
2.  **Install dependencies / 安装依赖**:
    ```bash
    pip install opencv-python pandas numpy scikit-learn matplotlib
    ```
3.  **Run the App / 启动程序**:
    ```bash
    python OptiThick-AI.py
    ```

---

## 🛠 Workflow / 使用工作流

### Phase 1: Database Learning (阶段 1：建立标定库)
1.  **Init DB**: Load or create a `.csv` database file.
2.  **Set Substrate**: Click on the substrate to lock the global exposure baseline.
3.  **Add Points**: Click on locations with known AFM data and input the actual thickness (nm).
1.  **初始化数据库**：加载或新建 `.csv` 库文件。
2.  **标定衬底**：点击衬底区域，锁定全库统一的“标准曝光”基准。
3.  **采集特征点**：点击已有 AFM 数据的点，输入实测厚度数值 (nm)。

### Phase 2: Automated Analysis (阶段 2：自动化分析)
1.  **Load Image**: Open a new device image for analysis.
2.  **Calibrate Substrate**: Match the current image's exposure to the database.
3.  **Calibrate Electrode**: Click on metal electrodes to exclude them from calculations.
4.  **Analyze**: Use **"Avg Height"** for statistics or **"Heatmap"** for full-field visualization.
1.  **加载图像**：打开待测器件照片。
2.  **标定当前衬底**：使当前图像亮度与数据库对齐。
3.  **标定电极**：点击金属电极区域，防止其干扰厚度统计。
4.  **生成结果**：通过 **“计算平均高度”** 获取统计值，或点击 **“生成热力图”** 查看全图分布。

---

## 🔬 Methodology / 技术原理

The system utilizes **k-Nearest Neighbors (k-NN) Regression** in a 3D RGB vector space. This approach overcomes the color jump discontinuities found in traditional 1D Hue mapping.

本系统采用 **k-NN（k-最近邻）回归算法** 在三维 RGB 向量空间中进行拟合。相比传统的单维度色调映射，该方法能更好地处理颜色循环的不连续性。

1.  **Vector Normalization / 向量标准化**:
    $$Vector_{calibrated} = Vector_{raw} \times \frac{Brightness_{baseline}}{Brightness_{current\_substrate}}$$
2.  **Euclidean Mapping / 欧氏距离映射**: Thickness is predicted by finding the closest color manifold features in the calibrated database.
    **空间寻优**：通过计算待测像素与数据库样本点的三维欧氏距离，反演物理厚度。

---
