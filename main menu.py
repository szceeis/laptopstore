import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

class LaptopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Penjualan Laptop Desktop")
        self.root.geometry("700x500")
        self.root.configure(bg="#5B21B6")  # Ungu gelap

        self.conn = sqlite3.connect("laptop.db")
        self.create_table()

        frame = tk.Frame(root, bg="#7C3AED", pady=10, padx=10)
        frame.pack(pady=15, padx=15, fill="x")

        lbl_style = {'bg': '#7C3AED', 'fg': 'white', 'font': ('Arial', 12, 'bold')}
        entry_bg = 'white'

        tk.Label(frame, text="Nama Laptop", **lbl_style).grid(row=0, column=0, sticky="w", pady=5)
        tk.Label(frame, text="Merek", **lbl_style).grid(row=1, column=0, sticky="w", pady=5)
        tk.Label(frame, text="Harga (Rp)", **lbl_style).grid(row=2, column=0, sticky="w", pady=5)

        self.nama_var = tk.StringVar()
        self.merek_var = tk.StringVar()
        self.harga_var = tk.StringVar()

        e1 = tk.Entry(frame, textvariable=self.nama_var, bg=entry_bg, font=('Arial', 12))
        e2 = tk.Entry(frame, textvariable=self.merek_var, bg=entry_bg, font=('Arial', 12))
        e3 = tk.Entry(frame, textvariable=self.harga_var, bg=entry_bg, font=('Arial', 12))

        e1.grid(row=0, column=1, pady=5, padx=5)
        e2.grid(row=1, column=1, pady=5, padx=5)
        e3.grid(row=2, column=1, pady=5, padx=5)

        btn_tambah = tk.Button(frame, text="Tambah Laptop", bg="#6D28D9", fg="white", font=('Arial', 12, 'bold'),
                              activebackground="#4C1D95", activeforeground="white", command=self.add_laptop)
        btn_tambah.grid(row=3, column=0, columnspan=2, pady=10, sticky="we")

        search_frame = tk.Frame(root, bg="#5B21B6")
        search_frame.pack(padx=15, fill="x")

        tk.Label(search_frame, text="Cari (Nama/Merek):", bg="#5B21B6", fg="white", font=('Arial', 12, 'bold')).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 12))
        search_entry.pack(side="left", padx=5, fill="x", expand=True)
        search_entry.bind("<KeyRelease>", lambda event: self.load_laptops())

        style = ttk.Style()
        style.theme_use('default')

        style.configure("Treeview",
                        background="#DDD6FE",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="#DDD6FE",
                        font=('Arial', 11))
        style.map('Treeview', background=[('selected', '#7C3AED')], foreground=[('selected', 'white')])

        style.configure("Treeview.Heading",
                        background="#6D28D9",
                        foreground="white",
                        font=('Arial', 12, 'bold'))

        self.tree = ttk.Treeview(root, columns=("id", "nama", "merek", "harga"), show='headings', selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("nama", text="Nama Laptop")
        self.tree.heading("merek", text="Merek")
        self.tree.heading("harga", text="Harga (Rp)")

        self.tree.column("id", width=40, anchor='center')
        self.tree.column("nama", width=200)
        self.tree.column("merek", width=150)
        self.tree.column("harga", width=120, anchor='e')

        self.tree.pack(padx=15, pady=10, fill="both", expand=True)

        btn_frame = tk.Frame(root, bg="#5B21B6")
        btn_frame.pack(padx=15, pady=10, fill="x")

        btn_edit = tk.Button(btn_frame, text="Edit Laptop Terpilih", bg="#C084FC", fg="#5B21B6",
                              font=('Arial', 12, 'bold'), activebackground="#A855F7",
                              activeforeground="white", command=self.edit_laptop)
        btn_edit.pack(side="left", expand=True, fill="x", padx=5)

        btn_hapus = tk.Button(btn_frame, text="Hapus Laptop Terpilih", bg="#A855F7", fg="white",
                              font=('Arial', 12, 'bold'), activebackground="#7E22CE",
                              activeforeground="white", command=self.delete_laptop)
        btn_hapus.pack(side="left", expand=True, fill="x", padx=5)

        self.load_laptops()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS laptops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT,
                merek TEXT,
                harga INTEGER
            )
        ''')
        self.conn.commit()

    def add_laptop(self):
        nama = self.nama_var.get().strip()
        merek = self.merek_var.get().strip()
        harga = self.harga_var.get().strip()

        if not nama or not merek or not harga:
            messagebox.showwarning("Input Salah", "Semua kolom harus diisi!")
            return
        
        try:
            harga_int = int(harga)
        except ValueError:
            messagebox.showwarning("Input Salah", "Harga harus angka!")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO laptops (nama, merek, harga) VALUES (?, ?, ?)", (nama, merek, harga_int))
        self.conn.commit()
        self.load_laptops()

        self.nama_var.set("")
        self.merek_var.set("")
        self.harga_var.set("")

    def load_laptops(self):
        search_text = self.search_var.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        cursor = self.conn.cursor()
        if search_text:
            cursor.execute("SELECT * FROM laptops WHERE LOWER(nama) LIKE ? OR LOWER(merek) LIKE ?", 
                           (f'%{search_text}%', f'%{search_text}%'))
        else:
            cursor.execute("SELECT * FROM laptops")
        for row in cursor.fetchall():
            laptop_id, nama, merek, harga = row
            harga_rupiah = f"Rp {harga:,}".replace(",", ".")
            self.tree.insert("", tk.END, values=(laptop_id, nama, merek, harga_rupiah))

    def delete_laptop(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", "Pilih laptop yang ingin dihapus.")
            return
        laptop_id = self.tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Konfirmasi Hapus", "Yakin ingin menghapus data laptop ini?"):
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM laptops WHERE id=?", (laptop_id,))
            self.conn.commit()
            self.load_laptops()

    def edit_laptop(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", "Pilih laptop yang ingin diedit.")
            return

        laptop_id, nama, merek, harga = self.tree.item(selected[0])['values']

        # Ubah harga dari format Rp ke int
        harga_str = harga.replace("Rp", "").replace(" ", "").replace(".", "")
        try:
            harga_int = int(harga_str)
        except ValueError:
            harga_int = 0

        new_nama = simpledialog.askstring("Edit Nama Laptop", "Nama Laptop:", initialvalue=nama, parent=self.root)
        if new_nama is None:
            return
        new_merek = simpledialog.askstring("Edit Merek Laptop", "Merek:", initialvalue=merek, parent=self.root)
        if new_merek is None:
            return
        new_harga = simpledialog.askstring("Edit Harga Laptop", "Harga (Rp):", initialvalue=str(harga_int), parent=self.root)
        if new_harga is None:
            return
        new_nama = new_nama.strip()
        new_merek = new_merek.strip()
        new_harga = new_harga.strip()

        if not new_nama or not new_merek or not new_harga:
            messagebox.showwarning("Input Salah", "Semua kolom harus diisi!")
            return

        try:
            new_harga_int = int(new_harga)
        except ValueError:
            messagebox.showwarning("Input Salah", "Harga harus angka!")
            return

        cursor = self.conn.cursor()
        cursor.execute("UPDATE laptops SET nama=?, merek=?, harga=? WHERE id=?",
                       (new_nama, new_merek, new_harga_int, laptop_id))
        self.conn.commit()
        self.load_laptops()

if __name__ == "__main__":
    root = tk.Tk()
    app = LaptopApp(root)
    root.mainloop()
