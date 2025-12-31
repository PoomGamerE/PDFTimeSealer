import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import threading
import io
import platform

# Library External
from tkinterdnd2 import DND_FILES, TkinterDnD
from pyhanko.sign import signers, fields
from pyhanko.sign.timestamps import HTTPTimeStamper
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils import reader
from pypdf import PdfReader, PdfWriter

class PDFTimeSealer(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        # --- App Config ---
        self.app_name = "PDFTimeSealer"
        self.version = "1.0.0"
        self.title(f"{self.app_name} v{self.version}")
        self.geometry("800x650")
        self.configure(bg="#f4f4f4")
        
        # --- Cross-Platform Icon Setup ---
        # พยายามโหลด Icon ถ้ามีไฟล์แนบไป (สำหรับ Window Title)
        icon_path = self.resource_path("app_icon.ico")
        if os.path.exists(icon_path):
            try:
                # Windows ใช้ iconbitmap, OS อื่นใช้ iconphoto
                if platform.system() == "Windows":
                    self.iconbitmap(icon_path)
                    # ตั้งค่า Taskbar Icon สำหรับ Windows
                    import ctypes
                    myappid = f'opensource.{self.app_name}.{self.version}'
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                else:
                    img = tk.PhotoImage(file=icon_path)
                    self.iconphoto(False, img)
            except Exception:
                pass # ใช้ Default icon ถ้าโหลดไม่ได้

        # --- Variables ---
        self.default_url = "http://timestamp.digicert.com"
        self.repair_var = tk.BooleanVar(value=True)
        self.filename_suffix = tk.StringVar(value="_sealed")
        
        self.create_widgets()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def create_widgets(self):
        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        
        COLOR_BG = "#f4f4f4"
        COLOR_BTN_ADD = "#28a745"   # Green
        COLOR_BTN_DEL = "#dc3545"   # Red
        COLOR_BTN_CLR = "#6c757d"   # Gray
        COLOR_PRIMARY = "#007bff"   # Blue
        
        style.configure("TLabel", background=COLOR_BG, font=("Segoe UI", 10))
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabelframe", background=COLOR_BG, font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background=COLOR_BG)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        # Main Layout
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # 1. Configuration Area
        config_frame = ttk.LabelFrame(main_frame, text=" Configuration ", padding=15)
        config_frame.pack(fill="x", pady=(0, 15))
        
        # URL
        ttk.Label(config_frame, text="Server URL:").grid(row=0, column=0, padx=5, sticky="w")
        self.url_entry = ttk.Entry(config_frame, font=("Consolas", 10), width=45)
        self.url_entry.insert(0, self.default_url)
        self.url_entry.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Suffix
        ttk.Label(config_frame, text="File Suffix:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.suffix_entry = ttk.Entry(config_frame, textvariable=self.filename_suffix, width=20)
        self.suffix_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(config_frame, text="(Example: '_signed')").grid(row=1, column=2, sticky="w")

        # Repair Checkbox
        chk_repair = ttk.Checkbutton(
            config_frame, 
            text="Repair PDF Structure (Fixes corrupted file errors)", 
            variable=self.repair_var
        )
        chk_repair.grid(row=2, column=1, padx=5, pady=(5,0), sticky="w")
        config_frame.columnconfigure(1, weight=1)

        # 2. File List Area
        file_frame = ttk.LabelFrame(main_frame, text=" Files ", padding=10)
        file_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Toolbar
        btn_box = ttk.Frame(file_frame)
        btn_box.pack(fill="x", pady=(0, 5))
        
        tk.Button(btn_box, text="+ Add Files", bg=COLOR_BTN_ADD, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, command=self.browse_files).pack(side="left", padx=2)
        tk.Button(btn_box, text="- Remove Selected", bg=COLOR_BTN_DEL, fg="white", font=("Segoe UI", 9), relief="flat", padx=10, command=self.remove_selected).pack(side="left", padx=2)
        tk.Button(btn_box, text="Clear All", bg=COLOR_BTN_CLR, fg="white", font=("Segoe UI", 9), relief="flat", padx=10, command=self.clear_list).pack(side="right", padx=2)

        # Treeview
        tree_container = ttk.Frame(file_frame)
        tree_container.pack(fill="both", expand=True)

        columns = ("filename", "status", "fullpath")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("filename", text="Filename")
        self.tree.heading("status", text="Status")
        self.tree.column("filename", width=400)
        self.tree.column("status", width=150, anchor="center")
        self.tree.column("fullpath", width=0, stretch=False) # Hidden

        self.tree.tag_configure("success", foreground="#28a745")
        self.tree.tag_configure("error", foreground="#dc3545")
        self.tree.tag_configure("waiting", foreground="black")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Drag & Drop Binding
        self.tree.bind('<B1-Motion>', self.on_drag_select)
        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind('<<Drop>>', self.drop_files)
        file_frame.drop_target_register(DND_FILES)
        file_frame.dnd_bind('<<Drop>>', self.drop_files)

        # 3. Action Area
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", side="bottom")
        
        self.progress = ttk.Progressbar(action_frame, orient="horizontal", mode='determinate')
        self.progress.pack(fill="x", pady=(0, 10))
        
        self.btn_run = tk.Button(
            action_frame, 
            text="START TIMESTAMPING", 
            bg=COLOR_PRIMARY, fg="white", 
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            command=self.start_thread,
            cursor="hand2"
        )
        self.btn_run.pack(fill="x", ipady=12)

    # --- Logic ---
    def on_drag_select(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_add(item)

    def drop_files(self, event):
        files = self.tk.splitlist(event.data)
        self.add_files_logic(files)

    def browse_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
        if files:
            self.add_files_logic(files)

    def add_files_logic(self, files):
        existing_paths = {self.tree.item(item)['values'][2] for item in self.tree.get_children()}
        for f in files:
            f = f.strip("{}")
            if f.lower().endswith(".pdf") and f not in existing_paths:
                fname = os.path.basename(f)
                self.tree.insert("", "end", values=(fname, "Waiting", f), tags=('waiting',))

    def remove_selected(self):
        for item in self.tree.selection():
            self.tree.delete(item)

    def clear_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def start_thread(self):
        if not self.tree.get_children():
            messagebox.showwarning("Warning", "Please add PDF files.")
            return
        threading.Thread(target=self.process_files, daemon=True).start()

    def process_files(self):
        ts_url = self.url_entry.get().strip()
        suffix = self.filename_suffix.get().strip()
        do_repair = self.repair_var.get()
        
        self.btn_run.config(state="disabled", bg="#cccccc")
        items = self.tree.get_children()
        self.progress['maximum'] = len(items)
        self.progress['value'] = 0
        success_count = 0

        try:
            http_stamper = HTTPTimeStamper(url=ts_url)
            timestamper = signers.PdfTimeStamper(timestamper=http_stamper)
        except Exception as e:
            messagebox.showerror("Error", f"Server Connection Failed:\n{e}")
            self.btn_run.config(state="normal", bg="#007bff")
            return

        for idx, item_id in enumerate(items):
            vals = self.tree.item(item_id)['values']
            filename = vals[0]
            file_path = vals[2]
            
            self.tree.item(item_id, values=(filename, "Processing...", file_path), tags=('waiting',))
            self.update_idletasks()

            try:
                folder = os.path.dirname(file_path)
                name_part = os.path.splitext(filename)[0]
                new_name = f"{name_part}{suffix}.pdf"
                output_path = os.path.join(folder, new_name)

                input_stream = None
                
                # Repair Logic
                if do_repair:
                    try:
                        reader_repair = PdfReader(file_path)
                        writer_repair = PdfWriter()
                        writer_repair.append_pages_from_reader(reader_repair)
                        memory_buffer = io.BytesIO()
                        writer_repair.write(memory_buffer)
                        memory_buffer.seek(0)
                        input_stream = memory_buffer
                    except Exception as e:
                        raise ValueError(f"Repair Failed: {str(e)}")
                else:
                    input_stream = open(file_path, 'rb')

                # Timestamping Logic
                try:
                    try:
                        r = reader.PdfFileReader(input_stream, strict=False)
                    except Exception:
                        raise ValueError("Invalid PDF Structure")

                    w = IncrementalPdfFileWriter(input_stream)
                    fields.append_signature_field(
                        w, sig_field_spec=fields.SigFieldSpec(sig_field_name='TimestampSignature', on_page=0)
                    )
                    
                    with open(output_path, 'wb') as outf:
                        timestamper.timestamp_pdf(w, 'sha256', output=outf)
                        
                finally:
                    if not do_repair and input_stream:
                        input_stream.close()

                self.tree.item(item_id, values=(filename, "Done", file_path), tags=('success',))
                success_count += 1

            except Exception as e:
                err_msg = str(e) if len(str(e)) < 40 else "Error (Check Console)"
                print(f"Error {filename}: {e}")
                self.tree.item(item_id, values=(filename, err_msg, file_path), tags=('error',))
            
            self.progress['value'] = idx + 1
        
        self.btn_run.config(state="normal", bg="#007bff")
        
        if success_count == len(items):
            messagebox.showinfo("Success", "All files timestamped successfully!")
        else:
            messagebox.showwarning("Complete", f"Finished with errors.\nSuccess: {success_count}\nFailed: {len(items)-success_count}")

if __name__ == "__main__":
    app = PDFTimeSealer()
    app.mainloop()