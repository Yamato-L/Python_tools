import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import os
import subprocess
import threading
import math
import numpy as np
import coordinates

class PathDataViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("路径数据查看器")
        self.root.geometry("1000x700")
        
        # 数据库文件路径
        self.db_path = ""
        self.conn = None
        self.current_table = ""
        self.original_data = []  # 存储原始数据
        self.transformed_data = []  # 存储转换后的数据
        self.is_transformed = False  # 标记当前显示的是否是转换后的数据
        
        # 坐标转换参数
        self.ref_point = (36.5653323, 119.1605849, 0)  # 参考点 (lat0, lon0, alt0)
        self.ellipsoid = "WGS84"  # 默认椭球体
        
        # 创建UI
        self.create_widgets()
        
    def create_widgets(self):
        # 顶部控制面板
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 数据库操作按钮
        db_frame = ttk.LabelFrame(control_frame, text="数据库操作", padding="5")
        db_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            db_frame, 
            text="从导航设备提取", 
            command=self.pull_db_from_导航
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            db_frame, 
            text="选择本地数据库", 
            command=self.select_local_db
        ).pack(side=tk.LEFT, padx=5)
        
        # 路径选择下拉框
        self.path_var = tk.StringVar()
        self.path_combobox = ttk.Combobox(
            db_frame, 
            textvariable=self.path_var, 
            state="readonly",
            width=30
        )
        self.path_combobox.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.path_combobox.bind("<<ComboboxSelected>>", self.load_path_data)
        
        # 坐标转换按钮
        transform_frame = ttk.LabelFrame(control_frame, text="坐标转换", padding="5")
        transform_frame.pack(side=tk.LEFT, padx=10)
        
        # ttk.Button(
        #     transform_frame, 
        #     text="设置参考点", 
        #     command=self.set_reference_point
        # ).pack(side=tk.LEFT, padx=5)
        
        self.transform_btn = ttk.Button(
            transform_frame, 
            text="高斯→ENU", 
            command=self.transform_coordinates,
            state=tk.DISABLED
        )
        self.transform_btn.pack(side=tk.LEFT, padx=5)
        
        # 数据显示区域
        data_frame = ttk.Frame(self.root)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 表格
        self.tree = ttk.Treeview(
            data_frame, 
            columns=("id", "x", "y", "head", "curv", "type", "e", "n", "u"), 
            show="headings"
        )
        
        # 设置列标题
        self.tree.heading("id", text="id")
        self.tree.heading("x", text="x")
        self.tree.heading("y", text="y")
        self.tree.heading("head", text="head")
        self.tree.heading("curv", text="curv")
        self.tree.heading("type", text="type")
        self.tree.heading("e", text="E(ENU)")
        self.tree.heading("n", text="N(ENU)")
        self.tree.heading("u", text="U(ENU)")
        
        # 设置列宽
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("x", width=100, anchor=tk.CENTER)
        self.tree.column("y", width=100, anchor=tk.CENTER)
        self.tree.column("head", width=80, anchor=tk.CENTER)
        self.tree.column("curv", width=80, anchor=tk.CENTER)
        self.tree.column("type", width=80, anchor=tk.CENTER)
        self.tree.column("e", width=100, anchor=tk.CENTER)
        self.tree.column("n", width=100, anchor=tk.CENTER)
        self.tree.column("u", width=100, anchor=tk.CENTER)
        
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
    
    def pull_db_from_导航(self):
        """从导航设备提取数据库文件"""
        default_remote_path = "/root/.nav/sql_path.db"
        
        remote_path = simpledialog.askstring(
            "输入路径", 
            "请输入导航设备上的数据库路径:", 
            initialvalue=default_remote_path
        )
        
        if not remote_path:
            return
            
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
                self.root.after(0, lambda: self.load_table_list())
                self.root.after(0, lambda: self.status_var.set(f"数据库已保存到: {local_path}"))
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
    
    def select_local_db(self):
        """选择本地数据库文件"""
        file_path = filedialog.askopenfilename(
            title="选择SQLite数据库文件",
            filetypes=[("SQLite数据库", "*.db"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.db_path = file_path
            self.load_table_list()
            self.status_var.set(f"已加载数据库: {os.path.basename(file_path)}")
    
    def load_table_list(self):
        """加载数据库中的表列表"""
        if not self.db_path:
            return
            
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.path_combobox["values"] = tables
            if tables:
                self.path_combobox.current(0)
                self.load_path_data()
                
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", str(e))
            self.status_var.set(f"数据库错误: {str(e)}")
    
    def load_path_data(self, event=None):
        """加载选中的路径数据"""
        table_name = self.path_var.get()
        if not table_name or not self.conn:
            return
            
        try:
            cursor = self.conn.cursor()
            
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 获取表数据
            cursor.execute(f"SELECT id, x, y, head, curv, type FROM {table_name} ORDER BY id")
            rows = cursor.fetchall()
            self.original_data = rows
            self.current_table = table_name
            self.is_transformed = False
            
            # 插入到Treeview
            for row in rows:
                self.tree.insert("", tk.END, values=row + ("", "", ""))
                
            self.status_var.set(f"已加载路径: {table_name} (共 {len(rows)} 条记录)")
            self.transform_btn["state"] = tk.NORMAL if self.ref_point else tk.DISABLED
            
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", str(e))
            self.status_var.set(f"加载数据错误: {str(e)}")
    
    # def set_reference_point(self):
    #     """设置坐标转换的参考点"""
    #     ref_str = simpledialog.askstring(
    #         "设置参考点", 
    #         "请输入参考点坐标(纬度,经度,高度)，逗号分隔:\n例如: 39.9042,116.4074,50.0",
    #         parent=self.root
    #     )
        
    #     if not ref_str:
    #         return
            
    #     try:
    #         parts = [float(x.strip()) for x in ref_str.split(",")]
    #         if len(parts) != 3:
    #             raise ValueError("需要3个值: 纬度,经度,高度")
                
    #         self.ref_point = tuple(parts)
    #         self.status_var.set(f"参考点已设置: 纬度={parts[0]}, 经度={parts[1]}, 高度={parts[2]}")
    #         self.transform_btn["state"] = tk.NORMAL if self.current_table else tk.DISABLED
            
    #     except ValueError as e:
    #         messagebox.showerror("输入错误", f"无效的参考点格式: {str(e)}")
    
    def transform_coordinates(self):
        """将高斯坐标转换为ENU坐标"""
        # if not self.ref_point or not self.original_data:
        #     messagebox.showwarning("警告", "请先设置参考点并加载数据")
        #     return
            
        try:
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 转换坐标
            lat0, lon0, alt0 = self.ref_point
            self.transformed_data = []
            
            for row in self.original_data:
                id_, x, y, head, curv, type_ = row
                e, n, u = coordinates.gauss_to_enu(x, y, curv) 
                print(x, y, curv)
                self.transformed_data.append((id_, x, y, head, curv, type_, e, n, u))
                
            # 显示转换后的数据
            for row in self.transformed_data:
                self.tree.insert("", tk.END, values=row)
                
            self.is_transformed = True
            self.status_var.set(f"坐标已转换(参考点: 纬度={lat0}, 经度={lon0}, 高度={alt0})")
            
        except Exception as e:
            messagebox.showerror("转换错误", str(e))
            self.status_var.set(f"坐标转换错误: {str(e)}")
    

if __name__ == "__main__":
    root = tk.Tk()
    app = PathDataViewer(root)
    root.mainloop()