import tkinter as tk
from tkinter import ttk, messagebox
from modules.database import get_conn

C_GOLD="#C8860A";C_DARK="#1A1A2E";C_WHITE="#FFFFFF";C_LIGHT="#F5F5F5"
C_GRAY="#AAAAAA";C_GREEN="#27AE60";C_RED="#E74C3C";C_ORANGE="#F39C12"
C_BLUE="#2980B9";C_BG="#F0F2F5"
FONT_TITLE=("Helvetica",20,"bold");FONT_HEADER=("Helvetica",13,"bold")
FONT_BOLD=("Helvetica",11,"bold");FONT_NORM=("Helvetica",10);FONT_SMALL=("Helvetica",9)
def fmt(n): return "{:,.0f}".format(n).replace(",", " ")
def btn(parent,text,cmd,bg=C_GOLD,fg=C_WHITE,font=FONT_BOLD,px=12,py=7):
    return tk.Button(parent,text=text,command=cmd,bg=bg,fg=fg,font=font,
                     relief="flat",bd=0,padx=px,pady=py,cursor="hand2")

class MenuTab(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C_BG)
        self.user = user
        self._build()
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=C_BG)
        hdr.pack(fill="x", padx=24, pady=(18,8))
        tk.Label(hdr, text="🍴  Gestion du Menu", font=FONT_TITLE, bg=C_BG, fg=C_DARK).pack(side="left")
        btn(hdr,"+ Ajouter Plat",self._add_item,bg=C_GREEN).pack(side="right",padx=4)
        btn(hdr,"+ Catégorie",self._add_category,bg=C_BLUE).pack(side="right",padx=4)
        btn(hdr,"↻",self._load,bg="#95A5A6",px=8).pack(side="right",padx=4)

        # Filter bar
        fbar = tk.Frame(self, bg=C_WHITE, pady=8)
        fbar.pack(fill="x", padx=24, pady=(0,8))
        tk.Label(fbar, text="Catégorie:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=10).pack(side="left")
        self.cat_var = tk.StringVar(value="Toutes")
        self.cat_cb = ttk.Combobox(fbar, textvariable=self.cat_var, font=FONT_NORM, width=20, state="readonly")
        self.cat_cb.pack(side="left", padx=6)
        self.cat_cb.bind("<<ComboboxSelected>>", lambda e: self._load())
        tk.Label(fbar, text="Recherche:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=10).pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(fbar, textvariable=self.search_var, font=FONT_NORM, width=20,
                 relief="solid", bd=1).pack(side="left", padx=4)
        self.search_var.trace("w", lambda *a: self._load())
        self.avail_var = tk.BooleanVar(value=False)
        tk.Checkbutton(fbar, text="Indisponibles seulement", variable=self.avail_var,
                       font=FONT_NORM, bg=C_WHITE, cursor="hand2", command=self._load).pack(side="left", padx=10)

        # Table
        table_frame = tk.Frame(self, bg=C_WHITE, highlightthickness=1, highlightbackground="#E0E0E0")
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0,16))

        cols = ("ID","Nom","Catégorie","Description","Prix","Disponible")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=22)
        widths = [50,200,150,250,110,90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        self.tree.tag_configure("unavail", foreground=C_RED)
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.tree.bind("<Double-1>", lambda e: self._edit_item())

        # Action bar
        act = tk.Frame(self, bg=C_BG)
        act.pack(fill="x", padx=24, pady=(0,10))
        btn(act,"✏ Modifier",self._edit_item,bg=C_BLUE).pack(side="left",padx=4)
        btn(act,"✔ Toggle Disponibilité",self._toggle_avail,bg=C_ORANGE).pack(side="left",padx=4)
        btn(act,"🗑 Supprimer",self._delete_item,bg=C_RED).pack(side="left",padx=4)

    def _load_categories(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT name FROM categories ORDER BY name")
        cats = ["Toutes"] + [r[0] for r in c.fetchall()]
        conn.close()
        self.cat_cb['values'] = cats
        return cats

    def _load(self):
        self._load_categories()
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn(); c = conn.cursor()
        cat = self.cat_var.get()
        search = self.search_var.get().strip()
        only_unavail = self.avail_var.get()

        query = """SELECT m.id, m.name, cat.name, m.description, m.price, m.available
                   FROM menu_items m LEFT JOIN categories cat ON m.category_id=cat.id
                   WHERE 1=1"""
        params = []
        if cat != "Toutes":
            query += " AND cat.name=?"; params.append(cat)
        if search:
            query += " AND m.name LIKE ?"; params.append(f"%{search}%")
        if only_unavail:
            query += " AND m.available=0"
        query += " ORDER BY cat.name, m.name"
        c.execute(query, params)
        for row in c.fetchall():
            iid, name, catname, desc, price, avail = row
            self.tree.insert("","end", iid=str(iid),
                values=(iid, name, catname or "-", (desc or "")[:50],
                        f"{fmt(price)} F", "✔ Oui" if avail else "✘ Non"),
                tags=() if avail else ("unavail",))
        conn.close()

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection","Sélectionnez un plat."); return None
        return int(sel[0])

    def _add_item(self):
        MenuItemDialog(self, None, self._load)

    def _edit_item(self):
        iid = self._get_selected()
        if iid: MenuItemDialog(self, iid, self._load)

    def _toggle_avail(self):
        iid = self._get_selected()
        if not iid: return
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT available FROM menu_items WHERE id=?", (iid,))
        row = c.fetchone()
        if row:
            new_val = 0 if row[0] else 1
            c.execute("UPDATE menu_items SET available=? WHERE id=?", (new_val, iid))
            conn.commit()
        conn.close()
        self._load()

    def _delete_item(self):
        iid = self._get_selected()
        if not iid: return
        if messagebox.askyesno("Supprimer","Supprimer ce plat ?"):
            conn = get_conn(); c = conn.cursor()
            c.execute("DELETE FROM menu_items WHERE id=?", (iid,))
            conn.commit(); conn.close()
            self._load()

    def _add_category(self):
        CategoryDialog(self, self._load)


class MenuItemDialog(tk.Toplevel):
    def __init__(self, parent, item_id, callback):
        super().__init__(parent)
        self.item_id = item_id
        self.callback = callback
        self.title("Ajouter Plat" if not item_id else "Modifier Plat")
        self.geometry("480x500")
        self.resizable(False, False)
        self.configure(bg=C_BG)
        x=(self.winfo_screenwidth()-480)//2; y=(self.winfo_screenheight()-500)//2
        self.geometry(f"480x500+{x}+{y}")
        self._build()
        if item_id: self._load()
        self.grab_set()

    def _build(self):
        tk.Frame(self, bg=C_GOLD, height=5).pack(fill="x")
        title = "Ajouter un Plat" if not self.item_id else "Modifier le Plat"
        tk.Label(self, text=f"🍴  {title}", font=FONT_HEADER, bg=C_BG, fg=C_DARK, pady=12).pack()
        form = tk.Frame(self, bg=C_WHITE, padx=28, pady=20)
        form.pack(fill="x", padx=24)

        tk.Label(form, text="Nom du plat *", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack(anchor="w", pady=(4,2))
        self.name_e = tk.Entry(form, font=FONT_NORM, relief="solid", bd=1); self.name_e.pack(fill="x")

        tk.Label(form, text="Description", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack(anchor="w", pady=(10,2))
        self.desc_e = tk.Text(form, font=FONT_NORM, height=3, relief="solid", bd=1, wrap="word")
        self.desc_e.pack(fill="x")

        row1 = tk.Frame(form, bg=C_WHITE); row1.pack(fill="x", pady=(10,0))
        tk.Label(row1, text="Prix (FCFA) *", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack(anchor="w")
        self.price_e = tk.Entry(row1, font=FONT_NORM, relief="solid", bd=1, width=16); self.price_e.pack(anchor="w")

        row2 = tk.Frame(form, bg=C_WHITE); row2.pack(fill="x", pady=(10,0))
        tk.Label(row2, text="Catégorie *", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack(anchor="w")
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id, name FROM categories ORDER BY name")
        self.cats = c.fetchall(); conn.close()
        self.cat_var = tk.StringVar()
        cat_names = [r[1] for r in self.cats]
        ttk.Combobox(row2, textvariable=self.cat_var, values=cat_names,
                     font=FONT_NORM, width=22, state="readonly").pack(anchor="w")
        if cat_names: self.cat_var.set(cat_names[0])

        self.avail_var = tk.BooleanVar(value=True)
        tk.Checkbutton(form, text="✔ Plat disponible", variable=self.avail_var,
                       font=FONT_NORM, bg=C_WHITE, fg=C_DARK, cursor="hand2").pack(anchor="w", pady=(10,0))

        btn_frame = tk.Frame(self, bg=C_BG, pady=14)
        btn_frame.pack(fill="x", padx=24)
        btn(btn_frame,"💾 Enregistrer",self._save,bg=C_GREEN).pack(side="left",padx=4)
        btn(btn_frame,"✖ Annuler",self.destroy,bg=C_RED).pack(side="left",padx=4)

    def _load(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT m.*, cat.name as catname FROM menu_items m LEFT JOIN categories cat ON m.category_id=cat.id WHERE m.id=?", (self.item_id,))
        m = c.fetchone(); conn.close()
        if not m: return
        self.name_e.insert(0, m['name'])
        self.desc_e.insert("1.0", m['description'] or "")
        self.price_e.insert(0, str(int(m['price'])))
        if m['catname']: self.cat_var.set(m['catname'])
        self.avail_var.set(bool(m['available']))

    def _save(self):
        name = self.name_e.get().strip()
        desc = self.desc_e.get("1.0","end").strip()
        if not name:
            messagebox.showerror("Erreur","Le nom est obligatoire."); return
        try: price = float(self.price_e.get())
        except: messagebox.showerror("Erreur","Prix invalide."); return

        cat_name = self.cat_var.get()
        cat_id = None
        for cid, cname in self.cats:
            if cname == cat_name: cat_id = cid; break

        conn = get_conn(); c = conn.cursor()
        avail = 1 if self.avail_var.get() else 0
        if self.item_id:
            c.execute("UPDATE menu_items SET name=?,description=?,price=?,category_id=?,available=? WHERE id=?",
                      (name,desc,price,cat_id,avail,self.item_id))
        else:
            c.execute("INSERT INTO menu_items (name,description,price,category_id,available) VALUES (?,?,?,?,?)",
                      (name,desc,price,cat_id,avail))
        conn.commit(); conn.close()
        self.callback(); self.destroy()


class CategoryDialog(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Nouvelle Catégorie")
        self.geometry("360x250")
        self.resizable(False, False)
        self.configure(bg=C_BG)
        x=(self.winfo_screenwidth()-360)//2; y=(self.winfo_screenheight()-250)//2
        self.geometry(f"360x250+{x}+{y}")
        self._build()
        self.grab_set()

    def _build(self):
        tk.Frame(self, bg=C_GOLD, height=5).pack(fill="x")
        tk.Label(self, text="Nouvelle Catégorie", font=FONT_HEADER, bg=C_BG, fg=C_DARK, pady=12).pack()
        form = tk.Frame(self, bg=C_WHITE, padx=28, pady=20)
        form.pack(fill="x", padx=24)
        tk.Label(form, text="Nom de la catégorie *", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack(anchor="w")
        self.name_e = tk.Entry(form, font=FONT_NORM, relief="solid", bd=1); self.name_e.pack(fill="x")
        colors = ["#4CAF50","#FF6B35","#E91E8C","#2196F3","#9C27B0","#FF9800","#795548","#607D8B"]
        tk.Label(form, text="Couleur:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack(anchor="w", pady=(10,4))
        self.color_var = tk.StringVar(value=colors[0])
        cf = tk.Frame(form, bg=C_WHITE); cf.pack(anchor="w")
        for col in colors:
            tk.Radiobutton(cf, bg=col, variable=self.color_var, value=col,
                           width=2, height=1, cursor="hand2", indicatoron=0,
                           selectcolor=col, relief="raised").pack(side="left", padx=2)
        btn_frame = tk.Frame(self, bg=C_BG, pady=12)
        btn_frame.pack(fill="x", padx=24)
        btn(btn_frame,"💾 Créer",self._save,bg=C_GREEN).pack(side="left",padx=4)
        btn(btn_frame,"✖ Annuler",self.destroy,bg=C_RED).pack(side="left",padx=4)

    def _save(self):
        name = self.name_e.get().strip()
        if not name:
            messagebox.showerror("Erreur","Nom obligatoire."); return
        conn = get_conn(); c = conn.cursor()
        c.execute("INSERT INTO categories (name,color) VALUES (?,?)", (name, self.color_var.get()))
        conn.commit(); conn.close()
        self.callback(); self.destroy()
