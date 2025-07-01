import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import os
import subprocess
import threading
import coordinates

class WorkRecordViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("WorkRecord 数据管理系统")
        self.root.geometry("1200x800")
        
        # 数据库文件路径
        self.db_path = ""
        self.remote_db_path = ""  # 存储导航设备上的原始路径
        self.conn = None
        
        # 创建UI
        self.create_widgets()
        
    def create_widgets(self):
        # 顶部控制面板
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 数据库操作按钮
        db_btn_frame = ttk.Frame(control_frame)
        db_btn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            db_btn_frame, 
            text="从导航设备提取", 
            command=self.pull_db_from_导航
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            db_btn_frame, 
            text="推送回导航设备", 
            command=self.push_db_to_导航
        ).pack(side=tk.LEFT, padx=5)
        
        self.push_btn = ttk.Button(
            db_btn_frame, 
            text="选择本地数据库", 
            command=self.select_local_db
        )
        self.push_btn.pack(side=tk.LEFT, padx=5)
        
        # 数据操作按钮
        data_btn_frame = ttk.Frame(control_frame)
        data_btn_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            data_btn_frame, 
            text="刷新数据", 
            command=self.load_data
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            data_btn_frame, 
            text="添加记录", 
            command=self.add_obstacle_record
        ).pack(side=tk.LEFT, padx=5)
        
        # 数据显示区域
        data_frame = ttk.Frame(self.root)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 表格
        self.tree = ttk.Treeview(
            data_frame, 
            columns=("id", "routeid", "name", "pathtype", "countid", "obsnum", 
                    "obsatt", "x", "y", "head", "curv", "a1", "a2", "a3", "a4"), 
            show="headings"
        )
        
        # 设置列标题
        columns = [
            ("id", "id", 50),
            ("routeid", "routeid", 80),
            ("name", "name", 100),
            ("pathtype", "pathtype", 80),
            ("countid", "countid", 80),
            ("obsnum", "obsnum", 80),
            ("obsatt", "obsatt", 100),
            ("x", "X坐标", 80),
            ("y", "Y坐标", 80),
            ("head", "head", 80),
            ("curv", "curv", 80),
            ("a1", "a1", 80),
            ("a2", "a2", 80),
            ("a3", "a3", 80),
            ("a4", "a4", 80)
        ]
        
        for col, heading, width in columns:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        ).pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 存储推送按钮引用
        self.push_to_导航_btn = None
    
    def pull_db_from_导航(self):
        """从导航设备提取数据库文件"""
        default_remote_path = "/root/.nav/workrecord.db"
        
        remote_path = simpledialog.askstring(
            "输入路径", 
            "请输入导航设备上的数据库路径:", 
            initialvalue=default_remote_path
        )
        
        if not remote_path:
            return
            
        self.remote_db_path = remote_path  # 保存远程路径用于后续推送
        
        local_path = filedialog.asksaveasfilename(
            title="保存数据库文件到",
            defaultextension=".db",
            filetypes=[("SQLite数据库", "*.db"), ("所有文件", "*.*")]
        )
        
        if not local_path:
            return
            
        self.status_var.set("正在从导航设备提取数据库...")
        threading.Thread(
            target=self._do_pull_db, 
            args=(remote_path, local_path),
            daemon=True
        ).start()
    
    def _do_pull_db(self, remote_path, local_path):
        """实际执行adb pull操作"""
        try:
            result = subprocess.run(
                ["adb", "pull", remote_path, local_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            if os.path.exists(local_path):
                self.db_path = local_path
                self.root.after(0, lambda: self.load_data())
                self.root.after(0, lambda: self.status_var.set(f"数据库已保存到: {local_path}"))
                # 启用推送按钮
                self.root.after(0, lambda: self.push_btn.config(state=tk.NORMAL))
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", "提取数据库失败"))
                self.root.after(0, lambda: self.status_var.set("提取数据库失败"))
                
        except subprocess.CalledProcessError as e:
            error_msg = f"ADB命令执行失败:\n{e.stderr}"
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            self.root.after(0, lambda: self.status_var.set("ADB命令执行失败"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
            self.root.after(0, lambda: self.status_var.set(f"错误: {str(e)}"))
    
    def push_db_to_导航(self):
        """将数据库推送回导航设备"""
        if not self.db_path or not self.remote_db_path:
            messagebox.showwarning("警告", "请先通过ADB提取数据库以获取设备路径")
            return
            
        confirm = messagebox.askyesno(
            "确认",
            f"即将覆盖导航设备上的数据库:\n{self.remote_db_path}\n\n确定要继续吗?"
        )
        
        if not confirm:
            return
            
        self.status_var.set("正在推送数据库到导航设备...")
        threading.Thread(
            target=self._do_push_db,
            daemon=True
        ).start()
    
    def _do_push_db(self):
        """实际执行adb push操作"""
        try:
            result = subprocess.run(
                ["adb", "push", self.db_path, self.remote_db_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 检查是否推送成功
            check_result = subprocess.run(
                ["adb", "shell", "ls", self.remote_db_path],
                capture_output=True,
                text=True
            )
            
            if check_result.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("成功", "数据库已成功推送到导航设备"))
                self.root.after(0, lambda: self.status_var.set(f"数据库已推送到: {self.remote_db_path}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", "推送数据库失败"))
                self.root.after(0, lambda: self.status_var.set("推送数据库失败"))
                
        except subprocess.CalledProcessError as e:
            error_msg = f"ADB命令执行失败:\n{e.stderr}"
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
            self.root.after(0, lambda: self.status_var.set("ADB命令执行失败"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
            self.root.after(0, lambda: self.status_var.set(f"错误: {str(e)}"))
    
    def select_local_db(self):
        """选择本地数据库文件"""
        file_path = filedialog.askopenfilename(
            title="选择SQLite数据库文件",
            filetypes=[("SQLite数据库", "*.db"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.db_path = file_path
            self.load_data()
            self.status_var.set(f"已加载数据库: {os.path.basename(file_path)}")
            # 禁用推送按钮，因为不知道远程路径
            self.push_btn.config(state=tk.DISABLED)
    
    def load_data(self):
        """加载allobstacle表数据"""
        if not self.db_path:
            messagebox.showwarning("警告", "请先选择数据库文件")
            return
            
        try:
            # 连接数据库
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 获取表数据
            cursor.execute("SELECT * FROM allobstacle")
            rows = cursor.fetchall()
            
            # 插入到Treeview
            for row in rows:
                self.tree.insert("", tk.END, values=row)
                
            self.status_var.set(f"已加载障碍物数据 (共 {len(rows)} 条记录)")
            
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", str(e))
            self.status_var.set(f"加载数据错误: {str(e)}")
    
    def add_obstacle_record(self):
        """添加新的障碍物记录"""
        if not self.db_path or not self.conn:
            messagebox.showwarning("警告", "请先选择并加载数据库")
            return
            
        # 创建输入对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加障碍物记录")
        dialog.geometry("500x600")
        
        # 表单字段
        fields = [
            ("routeid", "routeid:"),
            ("name", "name:"),
            ("countid", "countid:"),
            ("obsnum", "obsnum:"),
            ("SimOne_x", "SimOne x坐标:"),
            ("SimOne_y", "SimOne y坐标:"),
            # ("u", "u坐标:")
            # ("x", "X坐标:"),
            # ("y", "Y坐标:"),
            # ("curv", "curv:")
        ]
        
        entries = {}
        for i, (field, label) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
            entry = ttk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)
            entries[field] = entry
        
        # 确认按钮
        def submit():
            try:
                # 获取输入值
                values = {field: entry.get() for field, entry in entries.items()}
                x, y, central_meridian = coordinates.enu_to_gauss(float(values["SimOne_x"]), float(values["SimOne_y"]), 0) 
                print(x, y, central_meridian)
                lon, lat, alt = coordinates.enu_to_wgs84(float(values["SimOne_x"]), float(values["SimOne_y"]), 0)
                print(lon, lat, alt)
                
                # 插入数据库
                cursor = self.conn.cursor()
                cursor.execute(
                    """INSERT INTO allobstacle 
                    (routeid, name, pathtype, countid, obsnum, obsatt, x, y, head, curv, a1, a2, a3, a4) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (values["routeid"], values["name"], 4, values["countid"],
                     values["obsnum"], 0, x, y, 0, central_meridian, None, None, None, None)
                )
                self.conn.commit()
                
                messagebox.showinfo("成功", f"障碍物记录添加成功，经纬度{lon}，{lat}")
                dialog.destroy()
                self.load_data()
                
            except Exception as e:
                messagebox.showerror("错误", f"添加记录失败: {str(e)}")
        
        ttk.Button(dialog, text="提交", command=submit).grid(
            row=len(fields), column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkRecordViewer(root)
    root.mainloop()