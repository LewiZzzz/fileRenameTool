import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

class RenameTool:
    def __init__(self, root):
        self.root = root
        self.root.title("文件重命名工具")
        self.root.geometry("600x600")

        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 文件夹选择按钮和路径显示
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        self.folder_label = ttk.Label(folder_frame, text="选择文件夹:")
        self.folder_label.pack(side=tk.LEFT)
        self.folder_button = ttk.Button(folder_frame, text="浏览", command=self.select_folder)
        self.folder_button.pack(side=tk.LEFT, padx=5)
        self.path_label = ttk.Label(folder_frame, text="未选择文件夹", foreground="grey")
        self.path_label.pack(side=tk.LEFT, padx=10)

        # 全选按钮
        select_all_frame = ttk.Frame(main_frame)
        select_all_frame.pack(fill=tk.X, pady=5)
        self.select_all_button = ttk.Button(select_all_frame, text="全选", command=self.select_all)
        self.select_all_button.pack(side=tk.LEFT)

        # 文件列表显示
        self.file_listbox = tk.Listbox(main_frame, selectmode=tk.MULTIPLE, width=80, height=15, relief=tk.GROOVE, borderwidth=2)
        self.file_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        # 排序方式和顺序选择
        sort_frame = ttk.Frame(main_frame)
        sort_frame.pack(fill=tk.X, pady=5)
        self.sort_label = ttk.Label(sort_frame, text="排序方式:")
        self.sort_label.pack(side=tk.LEFT)
        self.sort_options = ["修改时间", "名称", "大小"]
        self.sort_var = tk.StringVar(value=self.sort_options[0])
        self.sort_menu = ttk.Combobox(sort_frame, textvariable=self.sort_var, values=self.sort_options, state="readonly")
        self.sort_menu.pack(side=tk.LEFT, padx=5)
        self.sort_menu.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        self.order_var = tk.StringVar(value="升序")
        self.order_menu = ttk.Combobox(sort_frame, textvariable=self.order_var, values=["升序", "降序"], state="readonly")
        self.order_menu.pack(side=tk.LEFT, padx=5)
        self.order_menu.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # 重命名方式选择
        rename_frame = ttk.Frame(main_frame)
        rename_frame.pack(fill=tk.X, pady=5)
        self.rename_label = ttk.Label(rename_frame, text="重命名方式:")
        self.rename_label.pack(side=tk.LEFT)
        self.rename_options = ["序号重命名", "序号+原名称", "自定义前缀+序号+原名称"]
        self.rename_var = tk.StringVar(value=self.rename_options[0])
        self.rename_menu = ttk.Combobox(rename_frame, textvariable=self.rename_var, values=self.rename_options, state="readonly")
        self.rename_menu.pack(side=tk.RIGHT)

        # 自定义前缀输入框
        prefix_frame = ttk.Frame(main_frame)
        prefix_frame.pack(fill=tk.X, pady=5)
        self.prefix_label = ttk.Label(prefix_frame, text="自定义前缀（可选）:")
        self.prefix_label.pack(side=tk.LEFT)
        self.prefix_entry = ttk.Entry(prefix_frame)
        self.prefix_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # 开始重命名按钮
        self.rename_button = ttk.Button(main_frame, text="开始重命名", command=self.start_renaming)
        self.rename_button.pack(pady=10)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
            self.path_label.config(text=self.folder_path, foreground="black")
            self.load_files()

    def load_files(self):
        self.file_listbox.delete(0, tk.END)
        supported_formats = [".png", ".txt", ".jpg", ".webp", ".doc", ".docx", ".pdf", ".mp3", ".mp4", ".zip", ".rar", ".7z"]
        self.files = [f for f in os.listdir(self.folder_path) if os.path.splitext(f)[1] in supported_formats]
        self.update_preview()

    def update_preview(self):
        self.file_listbox.delete(0, tk.END)
        sorted_files = self.sort_files(self.files.copy(), self.sort_var.get(), self.order_var.get())
        for file in sorted_files:
            self.file_listbox.insert(tk.END, file)

    def select_all(self):
        self.file_listbox.select_set(0, tk.END)

    def start_renaming(self):
        selected_files = [self.files[i] for i in self.file_listbox.curselection()]
        if not selected_files:
            messagebox.showwarning("未选择文件", "请选择要重命名的文件。")
            return

        sort_option = self.sort_var.get()
        order_option = self.order_var.get()
        rename_method = self.rename_var.get()
        custom_prefix = self.prefix_entry.get()

        # 按照排序方式排序文件
        sorted_files = self.sort_files(selected_files, sort_option, order_option)
        self.rename_files(sorted_files, rename_method, custom_prefix)

    def sort_files(self, files, sort_option, order_option):
        reverse = True if order_option == "降序" else False
        if sort_option == "修改时间":
            files.sort(key=lambda f: os.path.getmtime(os.path.join(self.folder_path, f)), reverse=reverse)
        elif sort_option == "名称":
            files.sort(reverse=reverse)
        elif sort_option == "大小":
            files.sort(key=lambda f: os.path.getsize(os.path.join(self.folder_path, f)), reverse=reverse)
        return files

    def rename_files(self, files, rename_method, custom_prefix):
        total_files = len(files)
        for index, file in enumerate(files):
            file_path = os.path.join(self.folder_path, file)
            file_ext = os.path.splitext(file)[1]
            new_name = ""

            if rename_method == "序号重命名":
                new_name = f"{index+1:03d}{file_ext}"
            elif rename_method == "序号+原名称":
                new_name = f"{index+1:03d}-{file}"
            elif rename_method == "自定义前缀+序号+原名称":
                new_name = f"{custom_prefix}{index+1:03d}-{file}"

            new_file_path = os.path.join(self.folder_path, new_name)
            os.rename(file_path, new_file_path)
            self.progress['value'] = (index + 1) / total_files * 100
            self.root.update_idletasks()

        messagebox.showinfo("重命名完成", f"{total_files} 个文件已成功重命名。")
        self.load_files()

if __name__ == "__main__":
    root = tk.Tk()
    app = RenameTool(root)
    root.mainloop()
