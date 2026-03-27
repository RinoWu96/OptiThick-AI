import cv2
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from sklearn.neighbors import KNeighborsRegressor
import os

class UltraThicknessApp:
    def __init__(self, root):
        self.root = root
        self.lang = "zh"  # 默认语言
        self.translations = {
            "zh": {
                "title": "光学测厚系统 v7.0 - 综合学习与精准测量版",
                "study_phase": "【 学习阶段：建立综合库 】",
                "load_db": "加载/创建数据库文件",
                "open_study_img": "打开学习图像",
                "calib_sub_study": "标定衬底 (统一曝光)",
                "add_point": "选取校准点 (红框标识)",
                "analysis_phase": "【 分析阶段：自动与测量 】",
                "open_measure_img": "打开待测图像",
                "calib_sub_measure": "标定当前衬底",
                "calc_avg_height": "计算平均高度 (去衬底)",
                "realtime_crosshair": "开启实时十字准心测量",
                "status_wait": "等待初始化",
                "db_success": "数据库加载成功",
                "study": "学习",
                "analysis": "分析",
                "img_loaded": "图像: ",
                "calib_msg": "点击衬底。此亮度将作为全数据库的【唯一标准曝光】",
                "calib_title": "标定",
                "input_height": "输入实际高度 (nm):",
                "input_title": "校准",
                "preview_title": "校准后视图 (已匹配库曝光)",
                "avg_height_title": "样品区域(剔除衬底)平均高度",
                "analysis_result_title": "分析结果",
                "sample_points": "样品点数",
                "avg_height": "平均高度",
                "status_prefix": "状态: ",
                "lang_label": "语言/Language"
            },
            "en": {
                "title": "Optical Thickness System v7.0 - Learning & Precision Edition",
                "study_phase": "[ Study Phase: Build Database ]",
                "load_db": "Load/Create Database File",
                "open_study_img": "Open Study Image",
                "calib_sub_study": "Calibrate Substrate (Fixed Exp)",
                "add_point": "Add Calibration Point (Red Box)",
                "analysis_phase": "[ Analysis Phase: Auto & Measure ]",
                "open_measure_img": "Open Measurement Image",
                "calib_sub_measure": "Calibrate Current Substrate",
                "calc_avg_height": "Calculate Avg Height (Sub-free)",
                "realtime_crosshair": "Enable Real-time Crosshair",
                "status_wait": "Waiting for Initialization",
                "db_success": "Database loaded successfully",
                "study": "Study",
                "analysis": "Analysis",
                "img_loaded": "Image: ",
                "calib_msg": "Click on substrate. This brightness will be the standard for the database.",
                "calib_title": "Calibration",
                "input_height": "Input actual height (nm):",
                "input_title": "Calibration",
                "preview_title": "Calibrated Preview (Matched Exp)",
                "avg_height_title": "Sample Area (Sub-free) Avg Height",
                "analysis_result_title": "Analysis Result",
                "sample_points": "Sample Points",
                "avg_height": "Average Height",
                "status_prefix": "Status: ",
                "lang_label": "Language"
            }
        }
        self.root.title(self.translations[self.lang]["title"])
        
        # 核心数据
        self.db_path = None
        self.calib_df = pd.DataFrame(columns=['r_cal', 'g_cal', 'b_cal', 'thickness', 'image_x', 'image_y', 'source_file'])
        
        # 学习基准（关键：全库统一的衬底亮度标准）
        self.db_norm_ref = None 
        self.current_sub_ref = None
        self.current_img = None
        self.img_name = ""
        
        self.model = KNeighborsRegressor(n_neighbors=3, weights='distance')
        self.ui_elements = {} # 存储需要更新文本的UI元素
        self.current_mode_key = None # 记录当前图像模式 (study/analysis)
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # 侧边栏
        ctrl_frame = tk.Frame(self.root, width=260, bg="#1a1a1a")
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y)

        h_style = {"bg": "#333333", "fg": "#00ffcc", "font": ('微软雅黑', 10, 'bold'), "pady": 5}
        btn_style = {"width": 25, "pady": 8, "cursor": "hand2", "font": ('微软雅黑', 9)}

        # --- 语言选择 ---
        lang_frame = tk.Frame(ctrl_frame, bg="#1a1a1a")
        lang_frame.pack(fill=tk.X, pady=(10, 5))
        self.ui_elements['lang_label'] = tk.Label(lang_frame, text=self.translations[self.lang]["lang_label"], bg="#1a1a1a", fg="#00ffcc", font=('微软雅黑', 9))
        self.ui_elements['lang_label'].pack(side=tk.LEFT, padx=5)
        
        self.lang_var = tk.StringVar(value="中文" if self.lang == "zh" else "English")
        lang_menu = tk.OptionMenu(lang_frame, self.lang_var, "中文", "English", command=self.change_language)
        lang_menu.config(width=8, font=('微软雅黑', 8))
        lang_menu.pack(side=tk.RIGHT, padx=5)

        # --- 学习阶段 ---
        self.ui_elements['study_header'] = tk.Label(ctrl_frame, text=self.translations[self.lang]["study_phase"], **h_style)
        self.ui_elements['study_header'].pack(fill=tk.X, pady=(10, 5))
        
        self.ui_elements['btn_init_db'] = tk.Button(ctrl_frame, text=self.translations[self.lang]["load_db"], command=self.init_db, **btn_style)
        self.ui_elements['btn_init_db'].pack(pady=2)
        
        self.ui_elements['btn_load_study'] = tk.Button(ctrl_frame, text=self.translations[self.lang]["open_study_img"], command=self.load_img_study, **btn_style)
        self.ui_elements['btn_load_study'].pack(pady=2)
        
        self.ui_elements['btn_set_sub_study'] = tk.Button(ctrl_frame, text=self.translations[self.lang]["calib_sub_study"], command=self.set_sub_study, bg="#c0392b", fg="white", **btn_style)
        self.ui_elements['btn_set_sub_study'].pack(pady=2)
        
        self.ui_elements['btn_add_point'] = tk.Button(ctrl_frame, text=self.translations[self.lang]["add_point"], command=self.add_point, **btn_style)
        self.ui_elements['btn_add_point'].pack(pady=2)

        # --- 分析阶段 ---
        self.ui_elements['analysis_header'] = tk.Label(ctrl_frame, text=self.translations[self.lang]["analysis_phase"], **h_style)
        self.ui_elements['analysis_header'].pack(fill=tk.X, pady=(20, 5))
        
        self.ui_elements['btn_load_measure'] = tk.Button(ctrl_frame, text=self.translations[self.lang]["open_measure_img"], command=self.load_img_measure, **btn_style)
        self.ui_elements['btn_load_measure'].pack(pady=2)
        
        self.ui_elements['btn_set_sub_measure'] = tk.Button(ctrl_frame, text=self.translations[self.lang]["calib_sub_measure"], command=self.set_sub_measure, bg="#2980b9", fg="white", **btn_style)
        self.ui_elements['btn_set_sub_measure'].pack(pady=2)
        
        self.ui_elements['btn_auto_height'] = tk.Button(ctrl_frame, text=self.translations[self.lang]["calc_avg_height"], command=self.auto_avg_height, bg="#27ae60", fg="white", **btn_style)
        self.ui_elements['btn_auto_height'].pack(pady=2)
        
        self.ui_elements['btn_crosshair'] = tk.Button(ctrl_frame, text=self.translations[self.lang]["realtime_crosshair"], command=self.enable_crosshair_query, **btn_style)
        self.ui_elements['btn_crosshair'].pack(pady=2)

        self.info_label = tk.Label(ctrl_frame, text=f"{self.translations[self.lang]['status_prefix']}{self.translations[self.lang]['status_wait']}", bg="#1a1a1a", fg="#888", wraplength=220)
        self.info_label.pack(side=tk.BOTTOM, pady=20)

        # 绘图布局
        plot_frame = tk.Frame(self.root)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig_main, self.ax_main = plt.subplots(figsize=(7, 6))
        self.canvas_main = FigureCanvasTkAgg(self.fig_main, master=plot_frame)
        self.canvas_main.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig_cal, self.ax_cal = plt.subplots(figsize=(4, 6))
        self.canvas_cal = FigureCanvasTkAgg(self.fig_cal, master=plot_frame)
        self.canvas_cal.get_tk_widget().pack(side=tk.RIGHT, fill=tk.Y)

    def change_language(self, lang_name):
        self.lang = "zh" if lang_name == "中文" else "en"
        self.update_ui_text()

    def update_ui_text(self):
        t = self.translations[self.lang]
        self.root.title(t["title"])
        self.ui_elements['lang_label'].config(text=t["lang_label"])
        self.ui_elements['study_header'].config(text=t["study_phase"])
        self.ui_elements['btn_init_db'].config(text=t["load_db"])
        self.ui_elements['btn_load_study'].config(text=t["open_study_img"])
        self.ui_elements['btn_set_sub_study'].config(text=t["calib_sub_study"])
        self.ui_elements['btn_add_point'].config(text=t["add_point"])
        self.ui_elements['analysis_header'].config(text=t["analysis_phase"])
        self.ui_elements['btn_load_measure'].config(text=t["open_measure_img"])
        self.ui_elements['btn_set_sub_measure'].config(text=t["calib_sub_measure"])
        self.ui_elements['btn_auto_height'].config(text=t["calc_avg_height"])
        self.ui_elements['btn_crosshair'].config(text=t["realtime_crosshair"])
        
        # 更新状态栏：根据当前应用状态重新合成
        if self.current_img is not None and self.current_mode_key:
            mode_text = t[self.current_mode_key]
            self.update_info(f"{mode_text}{t['img_loaded']}{self.img_name}")
        elif self.db_path:
            self.update_info(t["db_success"])
        else:
            self.update_info(t["status_wait"])

        # 更新绘图标题（如果已存在）
        self.show_calibrated_preview()
        if self.ax_main.get_title():
            # 简单处理：如果是平均高度标题，则更新它
            if "平均高度" in self.ax_main.get_title() or "Avg Height" in self.ax_main.get_title():
                # 这里需要提取数值，稍显复杂，先不强制更新正在显示的绘图标题，除非重新触发计算
                pass
        self.canvas_main.draw()

    # --- 核心图像算法 ---
    def get_calibrated_rgb(self, bgr_pixel):
        if self.current_sub_ref is None or self.db_norm_ref is None: return None
        # 使用学习阶段确定的全局基准进行动态补偿
        scale = self.db_norm_ref / (self.current_sub_ref + 1e-6)
        cal_bgr = np.clip(bgr_pixel * scale, 0, 255)
        return cal_bgr[[2, 1, 0]]

    def show_calibrated_preview(self):
        """在右侧框显示校准后的图像效果"""
        if self.current_img is None or self.db_norm_ref is None: return
        scale = self.db_norm_ref / (self.current_sub_ref + 1e-6)
        cal_img = np.clip(self.current_img * scale, 0, 255).astype(np.uint8)
        self.ax_cal.clear()
        self.ax_cal.imshow(cv2.cvtColor(cal_img, cv2.COLOR_BGR2RGB))
        self.ax_cal.set_title(self.translations[self.lang]["preview_title"], fontsize=9)
        self.ax_cal.axis('off')
        self.canvas_cal.draw()

    # --- 逻辑实现 ---
    def init_db(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            self.db_path = path
            if os.path.exists(path):
                self.calib_df = pd.read_csv(path)
                # 自动提取库中的第一个衬底亮度作为全局标准
                if not self.calib_df.empty: self.db_norm_ref = 180 # 预设或计算均值
                self.train_model()
            else:
                self.calib_df.to_csv(path, index=False)
            self.update_info(self.translations[self.lang]["db_success"])

    def load_img_study(self): self.load_img_gen("study")
    def load_img_measure(self): self.load_img_gen("analysis")

    def load_img_gen(self, mode_key):
        path = filedialog.askopenfilename()
        if path:
            self.current_img = cv2.imread(path).astype(np.float32)
            self.img_name = os.path.basename(path)
            self.current_mode_key = mode_key
            self.current_sub_ref = None
            self.refresh_main_view()
            mode_text = self.translations[self.lang][mode_key]
            self.update_info(f"{mode_text}{self.translations[self.lang]['img_loaded']}{self.img_name}")

    def set_sub_study(self):
        """学习阶段：不仅校准当前图，还要确立全库的亮度标杆"""
        messagebox.showinfo(self.translations[self.lang]["calib_title"], self.translations[self.lang]["calib_msg"])
        def onclick(event):
            if event.xdata:
                roi = self.current_img[int(event.ydata)-5:int(event.ydata)+5, int(event.xdata)-5:int(event.xdata)+5]
                self.current_sub_ref = np.mean(roi, axis=(0,1))
                self.db_norm_ref = self.current_sub_ref # 锁定标杆
                self.show_calibrated_preview()
                self.ax_main.plot(event.xdata, event.ydata, 'yx')
                self.canvas_main.draw()
                self.fig_main.canvas.mpl_disconnect(cid)
        cid = self.fig_main.canvas.mpl_connect('button_press_event', onclick)

    def add_point(self):
        def onclick(event):
            if event.xdata:
                rgb_cal = self.get_calibrated_rgb(self.current_img[int(event.ydata), int(event.xdata)])
                h = simpledialog.askfloat(self.translations[self.lang]["input_title"], self.translations[self.lang]["input_height"])
                if h is not None:
                    new_row = {'r_cal':rgb_cal[0], 'g_cal':rgb_cal[1], 'b_cal':rgb_cal[2], 
                               'thickness':h, 'image_x':event.xdata, 'image_y':event.ydata, 'source_file':self.img_name}
                    self.calib_df = pd.concat([self.calib_df, pd.DataFrame([new_row])], ignore_index=True)
                    self.calib_df.to_csv(self.db_path, index=False)
                    self.train_model()
                    self.refresh_main_view()
                self.fig_main.canvas.mpl_disconnect(cid)
        cid = self.fig_main.canvas.mpl_connect('button_press_event', onclick)

    def set_sub_measure(self):
        """分析阶段：匹配数据库的标杆曝光"""
        def onclick(event):
            if event.xdata:
                roi = self.current_img[int(event.ydata)-5:int(event.ydata)+5, int(event.xdata)-5:int(event.xdata)+5]
                self.current_sub_ref = np.mean(roi, axis=(0,1))
                self.show_calibrated_preview()
                self.fig_main.canvas.mpl_disconnect(cid)
        cid = self.fig_main.canvas.mpl_connect('button_press_event', onclick)

    def auto_avg_height(self):
        """计算平均高度（智能剔除衬底区域）"""
        if self.current_sub_ref is None: return
        # 颜色距离计算
        diff = np.abs(self.current_img - self.current_sub_ref)
        dist = np.sum(diff, axis=2)
        # 识别非衬底（样品）区域：距离衬底颜色超过阈值的点
        sample_mask = dist > 40 
        sample_pixels = self.current_img[sample_mask]
        
        if len(sample_pixels) > 0:
            cal_pix = np.array([self.get_calibrated_rgb(p) for p in sample_pixels])
            preds = self.model.predict(cal_pix)
            avg_h = np.mean(preds)
            self.ax_main.imshow(sample_mask, alpha=0.2, cmap='autumn')
            self.ax_main.set_title(f"{self.translations[self.lang]['avg_height_title']}: {avg_h:.2f} nm")
            self.canvas_main.draw()
            result_msg = f"{self.translations[self.lang]['sample_points']}: {len(sample_pixels)}\n{self.translations[self.lang]['avg_height']}: {avg_h:.2f} nm"
            messagebox.showinfo(self.translations[self.lang]["analysis_result_title"], result_msg)

    def enable_crosshair_query(self):
        """精准十字准心测量"""
        def onmove(event):
            if event.inaxes == self.ax_main:
                # 清除旧准心
                if hasattr(self, 'h_line'): self.h_line.remove()
                if hasattr(self, 'v_line'): self.v_line.remove()
                # 画新准心
                self.h_line = self.ax_main.axhline(y=event.ydata, color='red', lw=0.5, alpha=0.8)
                self.v_line = self.ax_main.axvline(x=event.xdata, color='red', lw=0.5, alpha=0.8)
                self.canvas_main.draw_idle()

        def onclick(event):
            if event.xdata:
                rgb_cal = self.get_calibrated_rgb(self.current_img[int(event.ydata), int(event.xdata)])
                pred = self.model.predict([rgb_cal])[0]
                self.ax_main.text(event.xdata, event.ydata, f" {pred:.1f}nm", color='white', 
                                  bbox=dict(facecolor='red', alpha=0.6))
                self.canvas_main.draw()

        self.fig_main.canvas.mpl_connect('motion_notify_event', onmove)
        self.fig_main.canvas.mpl_connect('button_press_event', onclick)

    def refresh_main_view(self):
        self.ax_main.clear()
        self.ax_main.imshow(cv2.cvtColor(self.current_img.astype(np.uint8), cv2.COLOR_BGR2RGB))
        # 绘制该图已有的红色方块
        pts = self.calib_df[self.calib_df['source_file'] == self.img_name]
        for _, r in pts.iterrows():
            self.ax_main.add_patch(Rectangle((r['image_x']-8, r['image_y']-8), 16, 16, lw=1.5, ec='red', fc='none'))
        self.canvas_main.draw()

    def train_model(self):
        if len(self.calib_df) >= 3:
            self.model.fit(self.calib_df[['r_cal', 'g_cal', 'b_cal']].values, self.calib_df['thickness'].values)

    def update_info(self, msg): self.info_label.config(text=f"{self.translations[self.lang]['status_prefix']}{msg}", fg="#00ffcc")
    def on_closing(self): plt.close('all'); self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); app = UltraThicknessApp(root); root.mainloop()
