import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import signal

# --- CLASS HỖ TRỢ THANH CUỘN ---
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, height=300) 
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# --- WIDGET DÙNG CHUNG CHO POLE VÀ ZERO ---
class ComponentRowWidget:
    def __init__(self, parent, c_type, index, initial_r, initial_c, update_callback, remove_callback, reorder_callback):
        self.update_callback = update_callback
        self.remove_callback = remove_callback
        self.reorder_callback = reorder_callback
        self.index = index
        self.c_type = c_type # "P" hoặc "Z"
        
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, pady=2)
        
        self.lbl_idx = ttk.Label(self.frame, text=f"{c_type}{index+1}", width=3, font=("Arial", 9, "bold"))
        self.lbl_idx.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Label(self.frame, text="R:").pack(side=tk.LEFT)
        self.var_r = tk.StringVar(value=str(initial_r))
        self.entry_r = ttk.Entry(self.frame, textvariable=self.var_r, width=7)
        self.entry_r.pack(side=tk.LEFT, padx=1)
        self.entry_r.bind('<Return>', self.on_change)
        self.entry_r.bind('<FocusOut>', self.on_change)

        ttk.Label(self.frame, text="C:").pack(side=tk.LEFT)
        self.var_c = tk.StringVar(value=f"{initial_c:.2e}")
        self.entry_c = ttk.Entry(self.frame, textvariable=self.var_c, width=7)
        self.entry_c.pack(side=tk.LEFT, padx=1)
        self.entry_c.bind('<Return>', self.on_change)
        self.entry_c.bind('<FocusOut>', self.on_change)

        ttk.Label(self.frame, text="Hz:").pack(side=tk.LEFT)
        initial_f = 1.0 / (2 * np.pi * initial_r * initial_c) if initial_c > 0 and initial_r > 0 else 0
        self.var_f = tk.StringVar(value=f"{initial_f:.1f}")
        self.entry_f = ttk.Entry(self.frame, textvariable=self.var_f, width=7)
        self.entry_f.pack(side=tk.LEFT, padx=1)
        self.entry_f.bind('<Return>', self.on_change_f)
        self.entry_f.bind('<FocusOut>', self.on_change_f)

        self.btn_del = ttk.Button(self.frame, text="X", width=2, command=lambda: remove_callback(self))
        self.btn_del.pack(side=tk.LEFT, padx=5)

    def get_values(self):
        try:
            r = float(self.var_r.get())
            c = float(self.var_c.get())
            return r, c
        except ValueError:
            return 1000, 1e-6

    def set_values(self, r, c, f=None):
        self.var_r.set(f"{r:.0f}")
        self.var_c.set(f"{c:.2e}")
        if f is None:
            f = 1.0 / (2 * np.pi * r * c)
        self.var_f.set(f"{f:.1f}")

    def get_freq(self):
        try:
            r = float(self.var_r.get())
            c = float(self.var_c.get())
            if r <= 0 or c <= 0: return 0
            return 1.0 / (2 * np.pi * r * c)
        except ValueError:
            return 0

    def on_change(self, event=None):
        try:
            r = float(self.var_r.get())
            c = float(self.var_c.get())
            if r <= 0 or c <= 0: return
            f = 1.0 / (2 * np.pi * r * c)
            self.var_f.set(f"{f:.1f}")
            self.reorder_callback()
        except ValueError:
            pass

    def on_change_f(self, event=None):
        try:
            f = float(self.var_f.get())
            r = float(self.var_r.get())
            if f <= 0 or r <= 0: return
            c = 1.0 / (2 * np.pi * r * f)
            self.var_c.set(f"{c:.2e}")
            self.reorder_callback()
        except ValueError:
            pass

    def update_from_drag(self, new_f):
        try:
            r = float(self.var_r.get())
            if new_f <= 0: return
            c = 1.0 / (2 * np.pi * r * new_f)
            self.var_f.set(f"{new_f:.1f}")
            self.var_c.set(f"{c:.2e}")
        except ValueError:
            pass

    def destroy(self):
        self.frame.destroy()

# --- QUẢN LÝ HỆ THỐNG ---
class SystemManager:
    def __init__(self, name, color, line_style):
        self.name = name
        self.color = color
        self.line_style = line_style
        self.active = False
        self.gain_val = 10000000.0 
        
        self.pole_widgets = [] 
        self.zero_widgets = [] 
        
        self.container_frame = None 
        
        # Miller Variables
        self.var_miller = None 
        self.miller_mode = False
        self.miller_av2 = 100.0
        self.cc_val = 0.0
        self.entry_cc = None 
        self.lbl_cin = None
        self.lbl_cout = None
        self.base_poles = [] 

    def get_poles_rad(self):
        # Trả về list các Pole (rad/s) - LHP Pole có phần thực âm
        pole_rads = []
        
        c_miller_in = 0.0
        c_miller_out = 0.0
        if self.miller_mode:
            c_miller_in = self.cc_val * (1 + self.miller_av2)
            c_miller_out = self.cc_val * (1 + 1.0/self.miller_av2)

        for i, widget in enumerate(self.pole_widgets):
            r, c_base = widget.get_values()
            c_total = c_base
            if self.miller_mode:
                if i == 0: c_total += c_miller_in
                elif i == 1: c_total += c_miller_out
            
            w = 1.0/(r*c_total)
            pole_rads.append(-w) 
            
        return sorted(pole_rads, key=lambda x: abs(x))

    def get_zeros_rad(self):
        # Trả về list các Zero (rad/s) - RHP Zero có phần thực dương
        zero_rads = []
        for widget in self.zero_widgets:
            r, c = widget.get_values()
            w = 1.0/(r*c)
            zero_rads.append(w) 
        return sorted(zero_rads)

    def reorder_widgets(self):
        if not self.container_frame: return
        
        # Sort Poles
        self.pole_widgets.sort(key=lambda w: w.get_freq())
        for i, widget in enumerate(self.pole_widgets):
            widget.frame.pack_forget()
            widget.frame.pack(fill=tk.X, pady=2)
            widget.lbl_idx.config(text=f"P{i+1}")
            widget.index = i
            
        # Sort Zeros
        self.zero_widgets.sort(key=lambda w: w.get_freq())
        for i, widget in enumerate(self.zero_widgets):
            widget.frame.pack_forget()
            widget.frame.pack(fill=tk.X, pady=2)
            widget.lbl_idx.config(text=f"Z{i+1}")
            widget.index = i

# --- APP CHÍNH ---
class BodePlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Bode Simulator (Poles & RHP Zeros)")
        self.root.geometry("1400x900")

        self.sys1 = SystemManager("Av1", "blue", "-")
        self.sys1.active = True
        self.sys2 = SystemManager("Av2", "orange", "-.")

        self.dragging_sys = None
        self.dragging_widget = None
        self.cursor_annotation = None 
        self.plot_data = {} 

        # Control Panel
        control_panel = ttk.Frame(self.root, padding="10")
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.btn_add_av2 = ttk.Button(control_panel, text="+ Kích hoạt Av2", command=self.activate_av2)
        self.btn_add_av2.pack(fill=tk.X, pady=(0, 10))

        self.notebook = ttk.Notebook(control_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Hệ thống 1 (Av1)')
        self.notebook.add(self.tab2, text='Hệ thống 2 (Av2)')

        self.setup_tab(self.tab1, self.sys1)
        self.setup_tab(self.tab2, self.sys2)
        self.notebook.tab(1, state="disabled")

        # Plot Frame
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        self.fig.subplots_adjust(left=0.08, bottom=0.08, right=0.95, top=0.92, hspace=0.35)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        self.update_plot()

    def setup_tab(self, parent, system):
        top_frame = ttk.Frame(parent, padding=5)
        top_frame.pack(fill=tk.X)

        # Gain DC
        ttk.Label(top_frame, text=f"Gain DC Total (lần):").pack(anchor=tk.W)
        gain_entry = ttk.Entry(top_frame)
        gain_entry.insert(0, "10000000") 
        gain_entry.pack(fill=tk.X, pady=5)
        gain_entry.bind('<Return>', lambda e: self.update_gain(system, gain_entry))
        gain_entry.bind('<FocusOut>', lambda e: self.update_gain(system, gain_entry))
        ttk.Button(top_frame, text="Cập nhật Gain", command=lambda: self.update_gain(system, gain_entry)).pack(fill=tk.X)

        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)

        # Miller Frame
        miller_frame = ttk.LabelFrame(parent, text="Op-Amp Compensation (Miller)", padding=5)
        miller_frame.pack(fill=tk.X, pady=10)

        system.var_miller = tk.BooleanVar(value=False)
        chk_miller = ttk.Checkbutton(miller_frame, text="Bật tính Cc (Miller)", variable=system.var_miller, 
                                     command=lambda: self.toggle_miller(system, entry_av2, entry_cc))
        chk_miller.pack(anchor=tk.W)

        # Av2
        ttk.Label(miller_frame, text="Gain Tầng 2 (Av2):").pack(anchor=tk.W, pady=(5,0))
        entry_av2 = ttk.Entry(miller_frame)
        entry_av2.insert(0, "100") 
        entry_av2.pack(fill=tk.X)
        entry_av2.bind('<Return>', lambda e: self.update_miller_params_from_entry(system, entry_av2, entry_cc))
        entry_av2.bind('<FocusOut>', lambda e: self.update_miller_params_from_entry(system, entry_av2, entry_cc))
        entry_av2.config(state="disabled")

        # Cc Entry
        ttk.Label(miller_frame, text="Tụ Bù Cc (F):").pack(anchor=tk.W, pady=(5,0))
        entry_cc = ttk.Entry(miller_frame)
        entry_cc.insert(0, "0.0") 
        entry_cc.pack(fill=tk.X)
        entry_cc.bind('<Return>', lambda e: self.update_miller_params_from_entry(system, entry_av2, entry_cc))
        entry_cc.bind('<FocusOut>', lambda e: self.update_miller_params_from_entry(system, entry_av2, entry_cc))
        entry_cc.config(state="disabled")
        system.entry_cc = entry_cc

        # Hiển thị Cin, Cout
        lbl_cin = ttk.Label(miller_frame, text="Cin_m: 0.00 pF", foreground="green")
        lbl_cin.pack(anchor=tk.W, padx=10)
        system.lbl_cin = lbl_cin
        lbl_cout = ttk.Label(miller_frame, text="Cout_m: 0.00 pF", foreground="green")
        lbl_cout.pack(anchor=tk.W, padx=10)
        system.lbl_cout = lbl_cout

        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)

        # Buttons Panel
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="+ Thêm Pole", command=lambda: self.add_component(system, "P")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_frame, text="+ Thêm Zero (RHP)", command=lambda: self.add_component(system, "Z")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        lbl_header = ttk.Frame(parent)
        lbl_header.pack(fill=tk.X)
        ttk.Label(lbl_header, text="Idx", width=4).pack(side=tk.LEFT)
        ttk.Label(lbl_header, text="R", width=9).pack(side=tk.LEFT)
        ttk.Label(lbl_header, text="C_base", width=9).pack(side=tk.LEFT)
        ttk.Label(lbl_header, text="Freq", width=9).pack(side=tk.LEFT)

        scroll_container = ScrollableFrame(parent)
        scroll_container.pack(fill=tk.BOTH, expand=True)
        system.container_frame = scroll_container.scrollable_frame 

    def toggle_miller(self, system, entry_av2, entry_cc):
        system.miller_mode = system.var_miller.get()
        if system.miller_mode:
            if len(system.pole_widgets) < 2:
                messagebox.showwarning("Cảnh báo", "Cần ít nhất 2 Pole (P1, P2) để chạy chế độ Miller.")
                system.var_miller.set(False)
                system.miller_mode = False
                return

            entry_av2.config(state="normal")
            entry_cc.config(state="normal")
            
            try:
                system.miller_av2 = float(entry_av2.get())
            except:
                system.miller_av2 = 100.0

            system.base_poles = []
            system.reorder_widgets()
            for w in system.pole_widgets:
                r, c = w.get_values()
                system.base_poles.append((r, c))
            
            system.cc_val = 0.0
            entry_cc.delete(0, tk.END)
            entry_cc.insert(0, "0.0")
            self.update_miller_display(system)
        else:
            entry_av2.config(state="disabled")
            entry_cc.config(state="disabled")
            system.lbl_cin.config(text="Cin_m: 0.00 pF")
            system.lbl_cout.config(text="Cout_m: 0.00 pF")
            
        self.update_plot()

    def update_miller_params_from_entry(self, system, entry_av2, entry_cc):
        if not system.miller_mode: return
        try:
            av2 = float(entry_av2.get())
            cc_str = entry_cc.get()
            cc = float(cc_str) if cc_str else 0.0
            
            if av2 <= 0: av2 = 1.0
            if cc < 0: cc = 0.0

            system.miller_av2 = av2
            system.cc_val = cc
            
            self.update_miller_display(system)
            self.update_plot()
        except ValueError:
            pass
            
    def update_miller_display(self, system):
        c_in = system.cc_val * (1 + system.miller_av2)
        c_out = system.cc_val * (1 + 1.0/system.miller_av2)
        system.lbl_cin.config(text=f"Cin_m (P1): {c_in*1e12:.2f} pF")
        system.lbl_cout.config(text=f"Cout_m (P2): {c_out*1e12:.2f} pF")

    def handle_reorder_and_plot(self, system):
        if not system.miller_mode:
            system.reorder_widgets()
        self.update_plot()

    def add_component(self, system, c_type):
        if c_type == "P":
            target_list = system.pole_widgets
            def_r = 1000; def_c = 1e-6
            if len(target_list) > 0:
                pr, pc = target_list[-1].get_values()
                def_c = pc / 10
        else: 
            target_list = system.zero_widgets
            def_r = 1000; def_c = 1e-9 

        idx = len(target_list)
        new_widget = ComponentRowWidget(
            system.container_frame, c_type, idx, def_r, def_c, 
            update_callback=self.update_plot, 
            remove_callback=lambda w: self.remove_component(system, w, c_type),
            reorder_callback=lambda: self.handle_reorder_and_plot(system) 
        )
        target_list.append(new_widget)
        
        if c_type == "P" and system.miller_mode:
            system.base_poles.append((def_r, def_c))
            
        self.handle_reorder_and_plot(system)

    def remove_component(self, system, widget, c_type):
        if c_type == "P":
            if system.miller_mode and widget.index < 2:
                messagebox.showwarning("Lỗi", "Không thể xóa P1/P2 trong chế độ Miller.")
                return
            if system.miller_mode and widget.index < len(system.base_poles):
                 system.base_poles.pop(widget.index)
            system.pole_widgets.remove(widget)
        else:
            system.zero_widgets.remove(widget)
            
        widget.destroy()
        self.handle_reorder_and_plot(system)

    def activate_av2(self):
        self.sys2.active = True
        self.notebook.tab(1, state="normal")
        self.notebook.select(1)
        self.btn_add_av2.config(text="- Xóa Đồ Thị Av2", command=self.deactivate_av2)
        self.update_plot()

    def deactivate_av2(self):
        self.sys2.active = False
        self.notebook.tab(1, state="disabled")
        self.notebook.select(0)
        self.btn_add_av2.config(text="+ Kích hoạt Av2", command=self.activate_av2)
        self.update_plot()

    def update_gain(self, system, entry):
        try:
            val = float(entry.get())
            system.gain_val = val
            self.update_plot()
        except: pass

    # --- DRAG LOGIC ---
    def on_press(self, event):
        if event.inaxes != self.ax1 and event.inaxes != self.ax2: return
        if not event.xdata: return

        click_hz = event.xdata
        closest_dist = float('inf')
        target_sys = None; target_widget = None
        
        for sys in [self.sys1, self.sys2]:
            if not sys.active: continue
            
            pole_rads = sys.get_poles_rad()
            for i, p_rad in enumerate(pole_rads):
                f_hz = abs(p_rad) / (2 * np.pi)
                dist = abs(np.log10(f_hz) - np.log10(click_hz))
                if dist < 0.05 and dist < closest_dist:
                    closest_dist = dist
                    target_sys = sys
                    target_widget = sys.pole_widgets[i] 

            zero_rads = sys.get_zeros_rad()
            for i, z_rad in enumerate(zero_rads):
                f_hz = abs(z_rad) / (2 * np.pi)
                dist = abs(np.log10(f_hz) - np.log10(click_hz))
                if dist < 0.05 and dist < closest_dist:
                    closest_dist = dist
                    target_sys = sys
                    target_widget = sys.zero_widgets[i]

        if target_sys:
            self.dragging_sys = target_sys
            self.dragging_widget = target_widget
            if self.cursor_annotation:
                self.cursor_annotation.remove(); self.cursor_annotation = None
                self.canvas.draw()
        else:
            self.handle_curve_click(event)

    def on_drag(self, event):
        if self.dragging_widget is None: return
        if event.inaxes is None or event.xdata <= 0: return

        new_f = event.xdata
        sys = self.dragging_sys
        
        is_zero = self.dragging_widget.c_type == "Z"
        
        if not is_zero and sys.miller_mode and (self.dragging_widget.index == 0 or self.dragging_widget.index == 1):
            idx = self.dragging_widget.index
            r_base, c_base = sys.base_poles[idx]
            
            c_total_req = 1.0 / (2 * np.pi * r_base * new_f)
            
            c_miller_needed = 0.0
            if idx == 0: 
                if c_total_req > c_base:
                    c_miller_needed = (c_total_req - c_base) / (1 + sys.miller_av2)
            else: 
                if c_total_req > c_base:
                    c_miller_needed = (c_total_req - c_base) / (1 + 1.0/sys.miller_av2)
            
            if c_miller_needed < 0: c_miller_needed = 0.0

            sys.cc_val = c_miller_needed
            sys.entry_cc.delete(0, tk.END)
            sys.entry_cc.insert(0, f"{c_miller_needed:.2e}")
            self.update_miller_display(sys)
            self.update_plot()
            
        else:
            self.dragging_widget.update_from_drag(new_f)
            self.update_plot()

    def on_release(self, event):
        if self.dragging_sys:
            self.handle_reorder_and_plot(self.dragging_sys)
        self.dragging_sys = None; self.dragging_widget = None

    def handle_curve_click(self, event):
        if self.cursor_annotation:
            self.cursor_annotation.remove(); self.cursor_annotation = None
        
        min_dist = 20; clicked_info = None 
        click_px = event.inaxes.transData.transform((event.xdata, event.ydata))

        for sys_name, data in self.plot_data.items():
            if sys_name == "sys1": sys = self.sys1
            else: sys = self.sys2
            if not sys.active: continue
            f_arr, mag_arr, phase_arr = data
            y_arr = mag_arr if event.inaxes == self.ax1 else phase_arr
            unit = "dB" if event.inaxes == self.ax1 else "deg"

            idx = np.searchsorted(f_arr, event.xdata)
            if idx >= len(f_arr): idx = len(f_arr) - 1
            if idx > 0 and abs(np.log10(f_arr[idx])-np.log10(event.xdata)) > abs(np.log10(f_arr[idx-1])-np.log10(event.xdata)):
                idx -= 1
            
            pt_px = event.inaxes.transData.transform((f_arr[idx], y_arr[idx]))
            dist = np.hypot(pt_px[0]-click_px[0], pt_px[1]-click_px[1])
            if dist < min_dist:
                min_dist = dist
                clicked_info = (f_arr[idx], y_arr[idx], sys.color, f"{sys.name}: {y_arr[idx]:.2f} {unit}")

        if clicked_info:
            px, py, col, txt = clicked_info
            self.cursor_annotation = event.inaxes.annotate(
                f"Freq: {px:.2e} Hz\n{txt}", xy=(px, py), xytext=(20, 20), textcoords='offset points',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=col, alpha=0.9),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color=col))
            self.canvas.draw()
        else: self.canvas.draw()

    def update_plot(self):
        self.ax1.clear(); self.ax2.clear()
        self.plot_data = {}

        # [UPDATE] Tìm tần số Start phù hợp (0.01Hz)
        # Tìm pole/zero có tần số thấp nhất để set trục X, tối thiểu là 0.01Hz
        poles_all = self.sys1.get_poles_rad() + (self.sys2.get_poles_rad() if self.sys2.active else [])
        zeros_all = self.sys1.get_zeros_rad() + (self.sys2.get_zeros_rad() if self.sys2.active else [])
        all_freqs_rad = [abs(x) for x in poles_all + zeros_all]
        
        # Determine F_max
        if not all_freqs_rad: 
            f_max_hz = 1e6
        else: 
            f_max_hz = max(all_freqs_rad) / (2*np.pi) * 100.0
        
        # [FIX] Start frequency at 0.01 Hz
        f = np.logspace(-2, np.log10(f_max_hz), 1000)
        w = 2 * np.pi * f
        
        global_min_phase = 0
        info_str = ""

        for s_key, sys in [("sys1", self.sys1), ("sys2", self.sys2)]:
            if not sys.active: continue
            
            poles_rad = sys.get_poles_rad()
            zeros_rad = sys.get_zeros_rad()
            
            # Tính K
            denom = 1.0
            if zeros_rad: denom = np.prod([-z for z in zeros_rad])
            numer = 1.0
            if poles_rad: numer = np.prod([-p for p in poles_rad])
            k_gain = sys.gain_val * numer / denom
            
            sys_model = signal.ZerosPolesGain(zeros_rad, poles_rad, k_gain)
            _, mag, phase = signal.bode(sys_model, w)
            
            if np.min(phase) < global_min_phase: global_min_phase = np.min(phase)
            mask = mag >= -40
            if np.any(mask):
                fm, mm, pm = f[mask], mag[mask], phase[mask]
                self.plot_data[s_key] = (fm, mm, pm)
                self.ax1.semilogx(fm, mm, color=sys.color, ls=sys.line_style, lw=2, label=f'{sys.name} (Gain)')
                self.ax2.semilogx(fm, pm, color=sys.color, ls=sys.line_style, lw=2, label=f'{sys.name} (Phase)')
                
                # Vẽ Poles
                for i, p_rad in enumerate(poles_rad):
                    f_hz = abs(p_rad)/(2*np.pi)
                    if f_hz <= f_max_hz:
                        self.ax1.axvline(x=f_hz, color=sys.color, ls='--', alpha=0.5)
                        self.ax2.axvline(x=f_hz, color=sys.color, ls='--', alpha=0.5)
                        self.ax1.text(f_hz, -0.1, f"P{i+1}", transform=self.ax1.get_xaxis_transform(), rotation=0, va='top', ha='center', fontweight='bold', color=sys.color)
                
                # Vẽ Zeros
                for i, z_rad in enumerate(zeros_rad):
                    f_hz = abs(z_rad)/(2*np.pi)
                    if f_hz <= f_max_hz:
                        self.ax1.axvline(x=f_hz, color=sys.color, ls=':', alpha=0.8, lw=2)
                        self.ax2.axvline(x=f_hz, color=sys.color, ls=':', alpha=0.8, lw=2)
                        self.ax1.text(f_hz, -0.15, f"Z{i+1}", transform=self.ax1.get_xaxis_transform(), rotation=0, va='top', ha='center', fontweight='bold', color='red')

                # Metrics
                idx0 = np.where(mag <= 0)[0]
                f0_str, pm_str = "N/A", "N/A"
                if len(idx0) > 0:
                    fc = f[idx0[0]]
                    phm = 180 + phase[idx0[0]]
                    f0_str, pm_str = f"{fc:.2e} Hz", f"{phm:.1f}°"
                    self.ax1.plot(fc, 0, 'o', color=sys.color)
                    self.ax1.axvline(x=fc, color=sys.color, ls='-.', alpha=0.8)
                    self.ax2.axvline(x=fc, color=sys.color, ls='-.', alpha=0.8)
                
                av_db = mag[0]
                idx_3db = np.where(mag <= (av_db - 3))[0]
                bw_hz = f[idx_3db[0]] if len(idx_3db) > 0 else 0

                info_str += f"[{sys.name}]\nAv: {mag[0]:.1f}dB | BW: {bw_hz:.2e}Hz\nGain Cross: {f0_str}\nPM: {pm_str}\n\n"

        if info_str:
            self.ax1.text(0.02, 0.05, info_str.strip(), transform=self.ax1.transAxes, fontsize=9, va='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        self.ax1.set_title("Biểu đồ Bode (Gain & Phase)") # [NEW] Title
        self.ax1.axhline(0, color='k', lw=1.5); self.ax1.grid(True, which="major", alpha=0.5); self.ax1.legend(fontsize='small')
        self.ax1.set_ylabel('Mag (dB)'); self.ax1.set_ylim(bottom=-40, top=max(self.ax1.get_ylim()[1], 10))
        self.ax2.set_ylabel('Phase (deg)'); self.ax2.set_xlabel('Freq (Hz)'); self.ax2.grid(True, which="major", alpha=0.5)
        
        # [UPDATE] X-Axis start at 0.01Hz explicitly
        self.ax2.set_xlim(left=0.01) 
        
        pb = max(np.floor(global_min_phase/45)*45, -270)
        self.ax2.set_ylim(bottom=pb, top=10); self.ax2.set_yticks(np.arange(0, pb-1, -45))
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = BodePlotterApp(root)
    root.mainloop()