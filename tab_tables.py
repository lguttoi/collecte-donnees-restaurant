import tkinter as tk
from tkinter import ttk, messagebox
from modules.database import get_conn

C_GOLD="#C8860A";C_DARK="#1A1A2E";C_WHITE="#FFFFFF";C_LIGHT="#F5F5F5"
C_GRAY="#AAAAAA";C_GREEN="#27AE60";C_RED="#E74C3C";C_ORANGE="#F39C12"
C_BLUE="#2980B9";C_BG="#F0F2F5";C_PURPLE="#8E44AD"
FONT_TITLE=("Helvetica",20,"bold");FONT_HEADER=("Helvetica",13,"bold")
FONT_BOLD=("Helvetica",11,"bold");FONT_NORM=("Helvetica",10);FONT_SMALL=("Helvetica",9)
def fmt(n): return "{:,.0f}".format(n).replace(",", " ")
def btn(parent,text,cmd,bg=C_GOLD,fg=C_WHITE,font=FONT_BOLD,px=12,py=7):
    return tk.Button(parent,text=text,command=cmd,bg=bg,fg=fg,font=font,
                     relief="flat",bd=0,padx=px,pady=py,cursor="hand2",
                     activebackground="#E6A020",activeforeground=C_WHITE)

STATUS_COLORS={"libre":C_GREEN,"occupee":C_RED,"reservee":C_ORANGE,"nettoyage":C_BLUE}
STATUS_LABELS={"libre":"Libre","occupee":"Occupée","reservee":"Réservée","nettoyage":"Nettoyage"}
STATUS_ICONS={"libre":"✓","occupee":"●","reservee":"📅","nettoyage":"🧹"}

class TablesTab(tk.Frame):
    def __init__(self, parent, user, app=None):
        super().__init__(parent, bg=C_BG)
        self.user = user
        self.app = app
        self._build()
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=C_BG)
        hdr.pack(fill="x", padx=24, pady=(18,8))
        tk.Label(hdr, text="🪑  Plan de Salle", font=FONT_TITLE, bg=C_BG, fg=C_DARK).pack(side="left")
        btn(hdr,"+ Ajouter Table",self._add_table,bg=C_GREEN).pack(side="right",padx=4)
        btn(hdr,"↻ Actualiser",self._load,bg=C_BLUE).pack(side="right",padx=4)

        # Legend
        leg = tk.Frame(self, bg=C_WHITE, pady=6)
        leg.pack(fill="x", padx=24, pady=(0,6))
        tk.Label(leg, text="Légende:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=10).pack(side="left")
        for status, color in STATUS_COLORS.items():
            f = tk.Frame(leg, bg=C_WHITE)
            f.pack(side="left", padx=10)
            tk.Frame(f, bg=color, width=16, height=16).pack(side="left")
            tk.Label(f, text=STATUS_LABELS[status], font=FONT_SMALL, bg=C_WHITE, fg=C_DARK).pack(side="left", padx=4)

        # Section tabs
        section_bar = tk.Frame(self, bg=C_WHITE)
        section_bar.pack(fill="x", padx=24, pady=(0,6))
        self.section_var = tk.StringVar(value="Toutes")
        self.section_buttons = {}
        sections = ["Toutes","Salle Principale","Terrasse","Salon Prive"]
        for sec in sections:
            b = tk.Button(section_bar, text=sec, font=FONT_SMALL,
                          bg=C_GOLD if sec=="Toutes" else C_WHITE,
                          fg=C_WHITE if sec=="Toutes" else C_DARK,
                          relief="flat", bd=1, padx=12, pady=6, cursor="hand2",
                          command=lambda s=sec: self._filter_section(s))
            b.pack(side="left", padx=4, pady=6)
            self.section_buttons[sec] = b

        # Main: canvas floor plan + detail panel
        main = tk.Frame(self, bg=C_BG)
        main.pack(fill="both", expand=True, padx=24, pady=(0,16))

        # Floor plan canvas
        canvas_frame = tk.Frame(main, bg=C_WHITE, highlightthickness=1, highlightbackground="#E0E0E0")
        canvas_frame.pack(side="left", fill="both", expand=True)
        tk.Label(canvas_frame, text="Vue Plan de Salle", font=FONT_HEADER,
                 bg=C_WHITE, fg=C_DARK, pady=8).pack(anchor="w", padx=14)
        self.canvas = tk.Canvas(canvas_frame, bg="#F9F5F0", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.canvas.bind("<Button-1>", self._canvas_click)

        # Detail panel
        detail = tk.Frame(main, bg=C_WHITE, width=280,
                          highlightthickness=1, highlightbackground="#E0E0E0")
        detail.pack(side="right", fill="y", padx=(8,0))
        detail.pack_propagate(False)
        tk.Label(detail, text="Détail Table", font=FONT_HEADER,
                 bg=C_WHITE, fg=C_DARK, pady=8).pack(anchor="w", padx=14)
        tk.Frame(detail, bg=C_GOLD, height=2).pack(fill="x", padx=14, pady=(0,8))
        self.detail_frame = tk.Frame(detail, bg=C_WHITE)
        self.detail_frame.pack(fill="both", expand=True, padx=14)

        act_frame = tk.Frame(detail, bg=C_WHITE, pady=8)
        act_frame.pack(fill="x", padx=14)
        btn(act_frame,"🧾 Voir Commande",self._view_order,bg=C_BLUE).pack(fill="x",pady=2)
        btn(act_frame,"🧾 Nouvelle Commande",self._new_order,bg=C_GREEN).pack(fill="x",pady=2)
        btn(act_frame,"🟡 Marquer Libre",lambda:self._set_status("libre"),bg=C_GREEN).pack(fill="x",pady=2)
        btn(act_frame,"🔴 Marquer Occupée",lambda:self._set_status("occupee"),bg=C_RED).pack(fill="x",pady=2)
        btn(act_frame,"🧹 Nettoyage",lambda:self._set_status("nettoyage"),bg=C_BLUE).pack(fill="x",pady=2)
        btn(act_frame,"✏ Modifier",self._edit_table,bg="#7F8C8D").pack(fill="x",pady=2)

        self.selected_table = None

    def _filter_section(self, section):
        self.section_var.set(section)
        for s, b in self.section_buttons.items():
            b.config(bg=C_GOLD if s==section else C_WHITE,
                     fg=C_WHITE if s==section else C_DARK)
        self._load()

    def _load(self):
        self.canvas.delete("all")
        conn = get_conn(); c = conn.cursor()
        section = self.section_var.get()
        if section == "Toutes":
            c.execute("SELECT id,number,capacity,status,section FROM tables ORDER BY number")
        else:
            c.execute("SELECT id,number,capacity,status,section FROM tables WHERE section=? ORDER BY number",
                      (section,))
        self.tables_data = c.fetchall()
        conn.close()

        # Draw decorative elements
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width() or 600
        h = self.canvas.winfo_height() or 400

        # Background grid
        for x in range(0, w, 80):
            self.canvas.create_line(x, 0, x, h, fill="#EEE8E0", width=1)
        for y in range(0, h, 80):
            self.canvas.create_line(0, y, w, y, fill="#EEE8E0", width=1)

        # Section labels
        self.canvas.create_text(10, 10, text="🍴 Salle Principale", font=("Helvetica",10,"bold"),
                                fill="#BBBBBB", anchor="nw")

        self.table_rects = {}
        cols = max(4, w // 130)
        for idx, (tid, num, cap, status, sec) in enumerate(self.tables_data):
            col = idx % cols
            row = idx // cols
            x = 40 + col * 130
            y = 50 + row * 120
            color = STATUS_COLORS.get(status, C_GRAY)
            shadow = self.canvas.create_rectangle(x+4, y+4, x+100, y+80, fill="#CCCCCC", outline="")
            rect = self.canvas.create_rectangle(x, y, x+100, y+80, fill=color, outline=C_WHITE, width=2)
            icon = self.canvas.create_text(x+50, y+22, text=f"TABLE {num}",
                                           font=("Helvetica",10,"bold"), fill=C_WHITE)
            cap_text = self.canvas.create_text(x+50, y+42, text=f"👥 {cap} pers.",
                                              font=("Helvetica",9), fill=C_WHITE)
            status_text = self.canvas.create_text(x+50, y+62, text=STATUS_LABELS.get(status, status),
                                                  font=("Helvetica",8,"bold"), fill=C_WHITE)
            if sec:
                s_text = self.canvas.create_text(x+50, y+88, text=sec[:15],
                                                 font=("Helvetica",7), fill="#888888")
            self.table_rects[rect] = tid
            self.table_rects[icon] = tid
            self.table_rects[cap_text] = tid
            self.table_rects[status_text] = tid

    def _canvas_click(self, event):
        items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        for item in items:
            if item in self.table_rects:
                tid = self.table_rects[item]
                self._select_table(tid)
                return

    def _select_table(self, tid):
        self.selected_table = tid
        for w in self.detail_frame.winfo_children():
            w.destroy()
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT * FROM tables WHERE id=?", (tid,))
        t = c.fetchone()
        if not t: conn.close(); return

        color = STATUS_COLORS.get(t['status'], C_GRAY)
        indicator = tk.Frame(self.detail_frame, bg=color, height=6)
        indicator.pack(fill="x", pady=(0,8))

        fields = [("N° Table", f"Table {t['number']}"),
                  ("Capacité", f"{t['capacity']} personnes"),
                  ("Section", t['section'] or "-"),
                  ("Statut", STATUS_LABELS.get(t['status'], t['status']))]
        for lbl, val in fields:
            row = tk.Frame(self.detail_frame, bg=C_WHITE)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl+":", font=("Helvetica",9,"bold"),
                     bg=C_WHITE, fg=C_GRAY, width=12, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FONT_NORM, bg=C_WHITE, fg=C_DARK).pack(side="left")

        # Current order if occupied
        if t['status'] == 'occupee':
            c.execute("""SELECT o.id, o.total, o.created_at FROM orders o
                         WHERE o.table_id=? AND o.status='en_cours' ORDER BY o.id DESC LIMIT 1""", (tid,))
            order = c.fetchone()
            if order:
                tk.Frame(self.detail_frame, bg="#EEEEEE", height=1).pack(fill="x", pady=6)
                tk.Label(self.detail_frame, text="Commande en cours:", font=FONT_BOLD,
                         bg=C_WHITE, fg=C_DARK).pack(anchor="w")
                tk.Label(self.detail_frame, text=f"N° #{order['id']}", font=FONT_NORM,
                         bg=C_WHITE, fg=C_BLUE).pack(anchor="w")
                tk.Label(self.detail_frame, text=f"Total: {fmt(order['total'])} F",
                         font=FONT_BOLD, bg=C_WHITE, fg=C_GOLD).pack(anchor="w")
                heure = (order['created_at'] or "")[:16]
                tk.Label(self.detail_frame, text=f"Depuis: {heure}", font=FONT_SMALL,
                         bg=C_WHITE, fg=C_GRAY).pack(anchor="w")
        conn.close()
        self._load()  # redraw to highlight selected

    def _set_status(self, status):
        if not self.selected_table:
            messagebox.showwarning("Sélection", "Cliquez d'abord sur une table."); return
        conn = get_conn(); c = conn.cursor()
        c.execute("UPDATE tables SET status=? WHERE id=?", (status, self.selected_table))
        conn.commit(); conn.close()
        self._load()
        self._select_table(self.selected_table)

    def _view_order(self):
        if not self.selected_table:
            messagebox.showwarning("Sélection","Cliquez d'abord sur une table."); return
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id FROM orders WHERE table_id=? AND status='en_cours' ORDER BY id DESC LIMIT 1",
                  (self.selected_table,))
        row = c.fetchone(); conn.close()
        if not row:
            messagebox.showinfo("Info","Pas de commande en cours pour cette table."); return
        from modules.tab_orders import OrderEditDialog
        OrderEditDialog(self, row[0], self.user, lambda: self._load())

    def _new_order(self):
        if not self.selected_table:
            messagebox.showwarning("Sélection","Cliquez d'abord sur une table."); return
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT number FROM tables WHERE id=?", (self.selected_table,))
        t = c.fetchone(); conn.close()
        from modules.tab_orders import OrderEditDialog
        d = OrderEditDialog(self, None, self.user, lambda: self._load())
        if t: d.table_var.set(str(t[0]))

    def _add_table(self):
        TableEditDialog(self, None, self._load)

    def _edit_table(self):
        if not self.selected_table:
            messagebox.showwarning("Sélection","Cliquez d'abord sur une table."); return
        TableEditDialog(self, self.selected_table, self._load)


class TableEditDialog(tk.Toplevel):
    def __init__(self, parent, table_id, callback):
        super().__init__(parent)
        self.table_id = table_id
        self.callback = callback
        self.title("Ajouter Table" if not table_id else "Modifier Table")
        self.geometry("380x320")
        self.resizable(False, False)
        self.configure(bg=C_BG)
        x=(self.winfo_screenwidth()-380)//2; y=(self.winfo_screenheight()-320)//2
        self.geometry(f"380x320+{x}+{y}")
        self._build()
        if table_id: self._load()
        self.grab_set()

    def _build(self):
        tk.Frame(self, bg=C_GOLD, height=5).pack(fill="x")
        tk.Label(self, text="Configuration de Table", font=FONT_HEADER,
                 bg=C_BG, fg=C_DARK, pady=14).pack()
        form = tk.Frame(self, bg=C_WHITE, padx=24, pady=20)
        form.pack(fill="x", padx=24)

        fields = [("Numéro de table:","number"),("Capacité (personnes):","capacity"),("Section:","section")]
        self.vars = {}
        for lbl, key in fields:
            tk.Label(form, text=lbl, font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack(anchor="w", pady=(6,2))
            if key == "section":
                var = tk.StringVar(value="Salle Principale")
                cb = ttk.Combobox(form, textvariable=var, font=FONT_NORM,
                                  values=["Salle Principale","Terrasse","Salon Prive"])
                cb.pack(fill="x")
                self.vars[key] = var
            else:
                e = tk.Entry(form, font=FONT_NORM, relief="solid", bd=1)
                e.pack(fill="x")
                self.vars[key] = e

        btn_frame = tk.Frame(self, bg=C_BG, pady=12)
        btn_frame.pack(fill="x", padx=24)
        btn(btn_frame,"💾 Enregistrer",self._save,bg=C_GREEN).pack(side="left",padx=4)
        btn(btn_frame,"✖ Annuler",self.destroy,bg=C_RED).pack(side="left",padx=4)

    def _load(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT * FROM tables WHERE id=?", (self.table_id,))
        t = c.fetchone(); conn.close()
        if not t: return
        self.vars['number'].delete(0,'end'); self.vars['number'].insert(0,str(t['number']))
        self.vars['capacity'].delete(0,'end'); self.vars['capacity'].insert(0,str(t['capacity']))
        self.vars['section'].set(t['section'] or "Salle Principale")

    def _save(self):
        try:
            num = int(self.vars['number'].get()); cap = int(self.vars['capacity'].get())
        except:
            messagebox.showerror("Erreur","Numéro et capacité doivent être des nombres."); return
        section = self.vars['section'].get()
        conn = get_conn(); c = conn.cursor()
        try:
            if self.table_id:
                c.execute("UPDATE tables SET number=?,capacity=?,section=? WHERE id=?",
                          (num,cap,section,self.table_id))
            else:
                c.execute("INSERT INTO tables (number,capacity,section) VALUES (?,?,?)", (num,cap,section))
            conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur",str(e)); conn.close(); return
        conn.close()
        self.callback(); self.destroy()
