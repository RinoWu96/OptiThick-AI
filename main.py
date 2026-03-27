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
                "title": "光学测厚系统 v8.0 - AFM标定与热力图增强版",
                "study_phase": "【 学习阶段：建立综合库 】",
                "load_db": "加载/创建数据库文件",
                "open_study_img": "打开学习图像",
                "calib_sub_study": "标定衬底 (统一曝光)",
                "add_point": "选取校准点 (红框标识)",
                "analysis_phase": "【 分析阶段：自动与测量 】",
                "open_measure_img": "打开待测图像",
                "calib_sub_measure": "标定当前衬底",
                "calib_electrode": "标定电极 (剔除干扰)",
                "calc_avg_height": "计算平均高度 (去衬底/电极)",
                "show_heatmap": "生成独立高度热力图",
                "realtime_crosshair": "开启实时十字准心测量",
                "status_wait": "等待初始化",
                "db_success": "数据库加载成功",
                "study": "学习",
                "analysis": "分析",
                "img_loaded": "图像: ",
                "calib_msg": "点击衬底。此亮度将作为全数据库的【唯一标准曝光】",
                "calib_elec_msg": "点击电极区域，系统将自动识别并剔除此类高反射区域",
                "calib_title": "标定",
                "input_height": "输入实际高度 (nm):",
                "input_title": "校准",
                "preview_title": "校准后视图 (已匹配库曝光)",
                "avg_height_title": "样品区域(剔除衬底及电极)平均高度",
                "analysis_result_title": "分析结果",
                "sample_points": "样品点数",
                "avg_height": "平均高度",
                "status_prefix": "状态: ",
                "lang_label": "语言/Language",
                "heatmap_title": "厚度分布热力图 (nm)"
            },
            "en": {
                "title": "Optical Thickness System v8.0 - Heatmap & Electrode Filtering",
                "study_phase": "[ Study Phase: Build Database ]",
                "load_db": "Load/Create Database File",
                "open_study_img": "Open Study Image",
                "calib_sub_study": "Calibrate Substrate (Fixed Exp)",
                "add_point": "Add Calibration Point (Red Box)",
                "analysis_phase": "[ Analysis Phase: Auto & Measure ]",
                "open_measure_img": "Open Measurement Image",
                "calib_sub_measure": "Calibrate Current Substrate",
                "calib_electrode": "Calibrate Electrode (Masking)",
                "calc_avg_height": "Calculate Avg Height (Sub/Elec-free)",
                "show_heatmap": "Generate Independent Heatmap",
                "realtime_crosshair": "Enable Real-time Crosshair",
                "status_wait": "Waiting for Initialization",
                "db_success": "Database loaded successfully",
                "study": "Study",
                "analysis": "Analysis",
                "img_loaded": "Image: ",
                "calib_msg": "Click on substrate. This brightness will be the standard for the database.",
                "calib_elec_msg": "Click on electrode. System will mask these high-reflective areas.",
                "calib_title": "Calibration",
                "input_height": "Input actual height (nm):",
                "input_title": "Calibration",
                "preview_title": "Calibrated Preview (Matched Exp)",
                "avg_height_title": "Sample Area (Excl. Sub & Elec) Avg Height",
                "analysis_result_title": "Analysis Result",
                "sample_points": "Sample Points",
                "avg_height": "Average Height",
                "status_prefix": "Status: ",
                "lang_label": "Language",
                "heatmap_title": "Thickness Distribution Heatmap (nm)"
            }
        }
        self.root.title(self.translations[self.lang]["title"])
        
        # 核心数据
        self.db_path = None
        self.calib_df = pd.DataFrame(columns=['r_cal', 'g_cal', 'b_cal', 'thickness', 'image_x', 'image_y', 'source_file', 'ref_b', 'ref_g', 'ref_r'])
        
        # 标定基准
        self.db_norm_ref = None 
        self.current_sub_ref = None
        self.current_elec_ref = None # 电极参考
        self.current_img = None
        self.img_name = ""
        
        self.model = KNeighborsRegressor(n_neighbors=3, weights='distance')
        self.ui_elements = {}
        self.current_mode_key = None 
        self.crosshair_move_cid = None
        self.crosshair_click_cid = None
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # 增加侧边栏宽度以适配长英文文本
        self.ctrl_frame = tk.Frame(self.root, width=280, bg="#1a1a1a")
        self.ctrl_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.ctrl_frame.pack_propagate(False) # 锁定宽度

        self.h_style = {"bg": "#333333", "fg": "#00ffcc", "font": ('微软雅黑', 10, 'bold'), "pady": 5}
        # 初始按钮样式，字体大小设为 9
        self.btn_font_size = 9 if self.lang == "zh" else 8
        self.btn_style = {"width": 28, "pady": 6, "cursor": "hand2", "font": ('微软雅黑', self.btn_font_size)}

        # --- 语言选择 ---
        lang_frame = tk.Frame(self.ctrl_frame, bg="#1a1a1a")
        lang_frame.pack(fill=tk.X, pady=(10, 5))
        self.ui_elements['lang_label'] = tk.Label(lang_frame, text=self.translations[self.lang]["lang_label"], bg="#1a1a1a", fg="#00ffcc")
        self.ui_elements['lang_label'].pack(side=tk.LEFT, padx=5)
        self.lang_var = tk.StringVar(value="中文" if self.lang == "zh" else "English")
        lang_menu = tk.OptionMenu(lang_frame, self.lang_var, "中文", "English", command=self.change_language)
        lang_menu.config(width=10)
        lang_menu.pack(side=tk.RIGHT, padx=5)

        # --- 学习阶段 ---
        self.ui_elements['study_header'] = tk.Label(self.ctrl_frame, text=self.translations[self.lang]["study_phase"], **self.h_style)
        self.ui_elements['study_header'].pack(fill=tk.X, pady=(5, 2))
        self.ui_elements['btn_init_db'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["load_db"], command=self.init_db, **self.btn_style)
        self.ui_elements['btn_init_db'].pack(pady=1)
        self.ui_elements['btn_load_study'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["open_study_img"], command=self.load_img_study, **self.btn_style)
        self.ui_elements['btn_load_study'].pack(pady=1)
        self.ui_elements['btn_set_sub_study'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["calib_sub_study"], command=self.set_sub_study, bg="#c0392b", fg="white", **self.btn_style)
        self.ui_elements['btn_set_sub_study'].pack(pady=1)
        self.ui_elements['btn_add_point'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["add_point"], command=self.add_point, **self.btn_style)
        self.ui_elements['btn_add_point'].pack(pady=1)

        # --- 分析阶段 ---
        self.ui_elements['analysis_header'] = tk.Label(self.ctrl_frame, text=self.translations[self.lang]["analysis_phase"], **self.h_style)
        self.ui_elements['analysis_header'].pack(fill=tk.X, pady=(15, 2))
        self.ui_elements['btn_load_measure'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["open_measure_img"], command=self.load_img_measure, **self.btn_style)
        self.ui_elements['btn_load_measure'].pack(pady=1)
        self.ui_elements['btn_set_sub_measure'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["calib_sub_measure"], command=self.set_sub_measure, bg="#2980b9", fg="white", **self.btn_style)
        self.ui_elements['btn_set_sub_measure'].pack(pady=1)
        self.ui_elements['btn_set_elec'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["calib_electrode"], command=self.set_electrode_measure, bg="#8e44ad", fg="white", **self.btn_style)
        self.ui_elements['btn_set_elec'].pack(pady=1)
        self.ui_elements['btn_auto_height'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["calc_avg_height"], command=self.auto_avg_height, bg="#27ae60", fg="white", **self.btn_style)
        self.ui_elements['btn_auto_height'].pack(pady=1)
        self.ui_elements['btn_heatmap'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["show_heatmap"], command=self.generate_heatmap, bg="#f39c12", fg="white", **self.btn_style)
        self.ui_elements['btn_heatmap'].pack(pady=1)
        self.ui_elements['btn_crosshair'] = tk.Button(self.ctrl_frame, text=self.translations[self.lang]["realtime_crosshair"], command=self.enable_crosshair_query, **self.btn_style)
        self.ui_elements['btn_crosshair'].pack(pady=1)

        self.info_label = tk.Label(self.ctrl_frame, text=f"{self.translations[self.lang]['status_prefix']}{self.translations[self.lang]['status_wait']}", bg="#1a1a1a", fg="#888", wraplength=280, font=('微软雅黑', 9))
        self.info_label.pack(side=tk.BOTTOM, pady=10)

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
        
        # 根据语言调整按钮字体大小
        font_size = 9 if self.lang == "zh" else 8
        new_font = ('微软雅黑', font_size)
        
        self.ui_elements['lang_label'].config(text=t["lang_label"])
        self.ui_elements['study_header'].config(text=t["study_phase"])
        self.ui_elements['analysis_header'].config(text=t["analysis_phase"])
        
        # 批量更新按钮文本和字体
        btn_keys = [
            'btn_init_db', 'btn_load_study', 'btn_set_sub_study', 'btn_add_point',
            'btn_load_measure', 'btn_set_sub_measure', 'btn_set_elec', 
            'btn_auto_height', 'btn_heatmap', 'btn_crosshair'
        ]
        
        # 对应翻译键名（有些键名和UI元素名略有不同，这里需要一一对应）
        translation_map = {
            'btn_init_db': 'load_db',
            'btn_load_study': 'open_study_img',
            'btn_set_sub_study': 'calib_sub_study',
            'btn_add_point': 'add_point',
            'btn_load_measure': 'open_measure_img',
            'btn_set_sub_measure': 'calib_sub_measure',
            'btn_set_elec': 'calib_electrode',
            'btn_auto_height': 'calc_avg_height',
            'btn_heatmap': 'show_heatmap',
            'btn_crosshair': 'realtime_crosshair'
        }
        
        for key in btn_keys:
            self.ui_elements[key].config(text=t[translation_map[key]], font=new_font)
            
        self.info_label.config(text=f"{t['status_prefix']}{t['status_wait']}")
        if self.current_img is not None and self.current_mode_key:
            self.update_info(f"{t[self.current_mode_key]}{t['img_loaded']}{self.img_name}")
        
        self.show_calibrated_preview()
        self.canvas_main.draw()

    def get_calibrated_rgb(self, bgr_pixel):
        if self.current_sub_ref is None or self.db_norm_ref is None: return None
        scale = self.db_norm_ref / (self.current_sub_ref + 1e-6)
        cal_bgr = np.clip(bgr_pixel * scale, 0, 255)
        return cal_bgr[[2, 1, 0]]

    def show_calibrated_preview(self):
        if self.current_img is None or self.db_norm_ref is None: return
        scale = self.db_norm_ref / (self.current_sub_ref + 1e-6)
        cal_img = np.clip(self.current_img * scale, 0, 255).astype(np.uint8)
        self.ax_cal.clear()
        self.ax_cal.imshow(cv2.cvtColor(cal_img, cv2.COLOR_BGR2RGB))
        self.ax_cal.set_title(self.translations[self.lang]["preview_title"], fontsize=9)
        self.ax_cal.axis('off')
        self.canvas_cal.draw()

    def init_db(self):
        self.disable_crosshair_query()
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            self.db_path = path
            if os.path.exists(path):
                self.calib_df = pd.read_csv(path)
                # 1. 自动提取库中的标杆亮度（尝试恢复 db_norm_ref）
                if not self.calib_df.empty: 
                    if all(c in self.calib_df.columns for c in ['ref_b', 'ref_g', 'ref_r']):
                        row0 = self.calib_df.iloc[0]
                        self.db_norm_ref = np.array([row0['ref_b'], row0['ref_g'], row0['ref_r']])
                    else:
                        # 兼容老版本数据库
                        self.db_norm_ref = np.array([180.0, 180.0, 180.0])
                self.train_model()
                
                # --- 新增修复代码 ---
                # 如果加载数据库时已经打开了图片，立即更新校准状态
                if self.current_img is not None:
                    # 如果当前还没点过衬底，先默认一个（防止缩放崩溃），或者等待用户点
                    if self.current_sub_ref is None:
                        self.current_sub_ref = np.mean(self.current_img, axis=(0,1))
                    self.show_calibrated_preview()
                # ------------------
                
            else:
                self.calib_df.to_csv(path, index=False)
            self.update_info(self.translations[self.lang]["db_success"])

    def load_img_study(self): self.load_img_gen("study")
    def load_img_measure(self): self.load_img_gen("analysis")

    def load_img_gen(self, mode_key):
        self.disable_crosshair_query()
        path = filedialog.askopenfilename()
        if path:
            self.current_img = cv2.imread(path).astype(np.float32)
            self.img_name = os.path.basename(path)
            self.current_mode_key = mode_key
            self.current_sub_ref = None
            self.current_elec_ref = None  # 确保切换图片时重置电极标定
            self.refresh_main_view()
            self.update_info(f"{self.translations[self.lang][mode_key]}{self.translations[self.lang]['img_loaded']}{self.img_name}")

    def set_sub_study(self):
        self.disable_crosshair_query()
        messagebox.showinfo(self.translations[self.lang]["calib_title"], self.translations[self.lang]["calib_msg"])
        def onclick(event):
            if event.xdata:
                roi = self.current_img[int(event.ydata)-5:int(event.ydata)+5, int(event.xdata)-5:int(event.xdata)+5]
                self.current_sub_ref = np.mean(roi, axis=(0,1))
                self.db_norm_ref = self.current_sub_ref 
                self.show_calibrated_preview()
                self.ax_main.plot(event.xdata, event.ydata, 'yx')
                self.canvas_main.draw()
                self.fig_main.canvas.mpl_disconnect(cid)
        cid = self.fig_main.canvas.mpl_connect('button_press_event', onclick)

    def add_point(self):
        self.disable_crosshair_query()
        def onclick(event):
            if event.xdata:
                rgb_cal = self.get_calibrated_rgb(self.current_img[int(event.ydata), int(event.xdata)])
                h = simpledialog.askfloat(self.translations[self.lang]["input_title"], self.translations[self.lang]["input_height"])
                if h is not None:
                    new_row = {
                        'r_cal':rgb_cal[0], 'g_cal':rgb_cal[1], 'b_cal':rgb_cal[2], 
                        'thickness':h, 'image_x':event.xdata, 'image_y':event.ydata, 'source_file':self.img_name,
                        'ref_b': self.db_norm_ref[0], 'ref_g': self.db_norm_ref[1], 'ref_r': self.db_norm_ref[2]
                    }
                    self.calib_df = pd.concat([self.calib_df, pd.DataFrame([new_row])], ignore_index=True)
                    self.calib_df.to_csv(self.db_path, index=False)
                    self.train_model()
                    self.refresh_main_view()
                self.fig_main.canvas.mpl_disconnect(cid)
        cid = self.fig_main.canvas.mpl_connect('button_press_event', onclick)

    def set_sub_measure(self):
        self.disable_crosshair_query()
        def onclick(event):
            if event.xdata:
                roi = self.current_img[int(event.ydata)-5:int(event.ydata)+5, int(event.xdata)-5:int(event.xdata)+5]
                self.current_sub_ref = np.mean(roi, axis=(0,1))
                self.show_calibrated_preview()
                self.fig_main.canvas.mpl_disconnect(cid)
        cid = self.fig_main.canvas.mpl_connect('button_press_event', onclick)

    def set_electrode_measure(self):
        self.disable_crosshair_query()
        messagebox.showinfo(self.translations[self.lang]["calib_title"], self.translations[self.lang]["calib_elec_msg"])
        def onclick(event):
            if event.xdata:
                roi = self.current_img[int(event.ydata)-5:int(event.ydata)+5, int(event.xdata)-5:int(event.xdata)+5]
                self.current_elec_ref = np.mean(roi, axis=(0,1))
                self.ax_main.plot(event.xdata, event.ydata, 'mo') # 洋红色标记电极标定点
                self.canvas_main.draw()
                self.fig_main.canvas.mpl_disconnect(cid)
        cid = self.fig_main.canvas.mpl_connect('button_press_event', onclick)

    def generate_mask(self):
        """核心掩模逻辑：结合衬底和电极剔除"""
        if self.current_sub_ref is None: return None
        # 衬底距离
        dist_sub = np.sum(np.abs(self.current_img - self.current_sub_ref), axis=2)
        mask = dist_sub > 40
        # 电极距离 (如果标定了)
        if self.current_elec_ref is not None:
            dist_elec = np.sum(np.abs(self.current_img - self.current_elec_ref), axis=2)
            mask = mask & (dist_elec > 45)
        return mask

    def auto_avg_height(self):
        self.disable_crosshair_query()
        mask = self.generate_mask()
        if mask is None: return
        sample_pixels = self.current_img[mask]
        if len(sample_pixels) > 0:
            cal_pix = np.array([self.get_calibrated_rgb(p) for p in sample_pixels])
            preds = self.model.predict(cal_pix)
            avg_h = np.mean(preds)
            self.ax_main.imshow(mask, alpha=0.2, cmap='autumn')
            self.ax_main.set_title(f"{self.translations[self.lang]['avg_height_title']}: {avg_h:.2f} nm")
            self.canvas_main.draw()
            messagebox.showinfo(self.translations[self.lang]["analysis_result_title"], 
                                f"{self.translations[self.lang]['sample_points']}: {len(sample_pixels)}\n{self.translations[self.lang]['avg_height']}: {avg_h:.2f} nm")
            # 关闭信息框后恢复正常视图
            self.refresh_main_view()

    def generate_heatmap(self):
        """弹出独立的高度热力图窗口"""
        self.disable_crosshair_query()
        if self.current_img is None or len(self.calib_df) < 3: return
        mask = self.generate_mask()
        if mask is None: return
        
        # 降采样处理以提升渲染速度 (缩放到最大500像素宽)
        h, w = self.current_img.shape[:2]
        scale_f = 500 / max(h, w)
        small_img = cv2.resize(self.current_img, (int(w*scale_f), int(h*scale_f)))
        small_mask = cv2.resize(mask.astype(np.uint8), (int(w*scale_f), int(h*scale_f))).astype(bool)
        
        # 初始化高度图
        heatmap = np.zeros(small_img.shape[:2])
        valid_pixels = small_img[small_mask]
        
        if len(valid_pixels) > 0:
            cal_pix = np.array([self.get_calibrated_rgb(p) for p in valid_pixels])
            preds = self.model.predict(cal_pix)
            heatmap[small_mask] = preds
        
        # 创建独立窗口
        plt.figure(self.translations[self.lang]["heatmap_title"], figsize=(8, 6))
        plt.title(self.translations[self.lang]["heatmap_title"])
        # 将非样品区设为透明/背景
        heatmap_display = np.ma.masked_where(~small_mask, heatmap)
        im = plt.imshow(heatmap_display, cmap='jet')
        plt.colorbar(im, label="Thickness (nm)")
        plt.axis('off')
        plt.show()

    def enable_crosshair_query(self):
        # 先清理旧的绑定，避免重复叠加
        self.disable_crosshair_query()
        
        def onmove(event):
            if event.inaxes == self.ax_main:
                if hasattr(self, 'h_line'): 
                    try: self.h_line.remove()
                    except: pass
                if hasattr(self, 'v_line'): 
                    try: self.v_line.remove()
                    except: pass
                self.h_line = self.ax_main.axhline(y=event.ydata, color='red', lw=0.5, alpha=0.8)
                self.v_line = self.ax_main.axvline(x=event.xdata, color='red', lw=0.5, alpha=0.8)
                self.canvas_main.draw_idle()
        def onclick(event):
            if event.xdata:
                rgb_cal = self.get_calibrated_rgb(self.current_img[int(event.ydata), int(event.xdata)])
                pred = self.model.predict([rgb_cal])[0]
                self.ax_main.text(event.xdata, event.ydata, f" {pred:.1f}nm", color='white', bbox=dict(facecolor='red', alpha=0.6))
                self.canvas_main.draw()
        
        self.crosshair_move_cid = self.fig_main.canvas.mpl_connect('motion_notify_event', onmove)
        self.crosshair_click_cid = self.fig_main.canvas.mpl_connect('button_press_event', onclick)

    def disable_crosshair_query(self):
        """取消实时十字准心显示并移除绑定"""
        if self.crosshair_move_cid is not None:
            self.fig_main.canvas.mpl_disconnect(self.crosshair_move_cid)
            self.crosshair_move_cid = None
        if self.crosshair_click_cid is not None:
            self.fig_main.canvas.mpl_disconnect(self.crosshair_click_cid)
            self.crosshair_click_cid = None
        
        # 移除十字线
        if hasattr(self, 'h_line'): 
            try: self.h_line.remove()
            except: pass
            del self.h_line
        if hasattr(self, 'v_line'): 
            try: self.v_line.remove()
            except: pass
            del self.v_line
        self.canvas_main.draw_idle()

    def refresh_main_view(self):
        self.ax_main.clear()
        self.ax_main.imshow(cv2.cvtColor(self.current_img.astype(np.uint8), cv2.COLOR_BGR2RGB))
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
