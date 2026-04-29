import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from modules.database import get_conn

C_GOLD="#C8860A";C_DARK="#1A1A2E";C_DARK2="#16213E";C_PANEL="#0F3460"
C_WHITE="#FFFFFF";C_LIGHT="#F5F5F5";C_GRAY="#AAAAAA"
C_GREEN="#27AE60";C_RED="#E74C3C";C_ORANGE="#F39C12";C_BLUE="#2980B9";C_BG="#F0F2F5"
FONT_TITLE=("Helvetica",20,"bold");FONT_HEADER=("Helvetica",13,"bold")
FONT_BOLD=("Helvetica",11,"bold");FONT_NORM=("Helvetica",10);FONT_SMALL=("Helvetica",9)
def fmt(n): return "{:,.0f}".format(n).replace(",", " ")

def btn(parent, text, cmd, bg=C_GOLD, fg=C_WHITE, font=FONT_BOLD, px=12, py=7):
    return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, font=font,
                     relief="flat", bd=0, padx=px, pady=py, cursor="hand2",
                     activebackground="#E6A020", activeforeground=C_WHITE)

class OrdersTab(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C_BG)
        self.user = user
        self._build()
        self._load_orders()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C_BG)
        hdr.pack(fill="x", padx=24, pady=(18,8))
        tk.Label(hdr, text="🧾  Gestion des Commandes", font=FONT_TITLE, bg=C_BG, fg=C_DARK).pack(side="left")
        btn(hdr, "+ Nouvelle Commande", self._new_order, bg=C_GREEN).pack(side="right", padx=4)
        btn(hdr, "↻ Actualiser", self._load_orders, bg=C_BLUE).pack(side="right", padx=4)

        # Filter bar
        fbar = tk.Frame(self, bg=C_WHITE, pady=8)
        fbar.pack(fill="x", padx=24, pady=(0,8))
        tk.Label(fbar, text="Filtrer:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=10).pack(side="left")
        self.filter_var = tk.StringVar(value="tous")
        statuses = [("Tous","tous"),("En cours","en_cours"),("Servis","servi"),("Payés","paye"),("Annulés","annule")]
        for lbl, val in statuses:
            tk.Radiobutton(fbar, text=lbl, variable=self.filter_var, value=val,
                           font=FONT_NORM, bg=C_WHITE, fg=C_DARK, cursor="hand2",
                           command=self._load_orders).pack(side="left", padx=8)
        tk.Label(fbar, text="Table:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=10).pack(side="left")
        self.table_filter = tk.Entry(fbar, font=FONT_NORM, width=6, relief="solid", bd=1)
        self.table_filter.pack(side="left", padx=4)
        self.table_filter.bind("<KeyRelease>", lambda e: self._load_orders())

        # Main pane: list left, detail right
        pane = tk.Frame(self, bg=C_BG)
        pane.pack(fill="both", expand=True, padx=24, pady=(0,16))

        # Order list
        left = tk.Frame(pane, bg=C_WHITE, highlightthickness=1, highlightbackground="#E0E0E0")
        left.pack(side="left", fill="both", expand=True)

        cols = ("ID","Table","Client","Heure","Articles","Total","Statut","Serveur")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=22)
        widths = [50,60,110,80,60,110,90,110]
        for col,w in zip(cols,widths):
            self.tree.heading(col, text=col, command=lambda c=col: None)
            self.tree.column(col, width=w, anchor="center")
        self.tree.tag_configure("en_cours", background="#FFF3E0")
        self.tree.tag_configure("servi", background="#E8F5E9")
        self.tree.tag_configure("paye", background="#E3F2FD")
        self.tree.tag_configure("annule", background="#FFEBEE")
        sb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._open_order())

        # Order detail panel
        right = tk.Frame(pane, bg=C_WHITE, width=320,
                         highlightthickness=1, highlightbackground="#E0E0E0")
        right.pack(side="right", fill="y", padx=(8,0))
        right.pack_propagate(False)

        tk.Label(right, text="Détail Commande", font=FONT_HEADER,
                 bg=C_WHITE, fg=C_DARK, pady=10).pack(anchor="w", padx=14)
        tk.Frame(right, bg=C_GOLD, height=2).pack(fill="x", padx=14, pady=(0,8))

        self.detail_frame = tk.Frame(right, bg=C_WHITE)
        self.detail_frame.pack(fill="both", expand=True, padx=14)

        act_frame = tk.Frame(right, bg=C_WHITE)
        act_frame.pack(fill="x", padx=14, pady=10)

        btn(act_frame,"✏ Modifier",self._open_order,bg=C_BLUE).pack(fill="x",pady=2)
        btn(act_frame,"✔ Marquer Servi",lambda:self._change_status("servi"),bg=C_GREEN).pack(fill="x",pady=2)
        btn(act_frame,"💰 Encaisser",self._encaisser,bg=C_GOLD).pack(fill="x",pady=2)
        btn(act_frame,"✖ Annuler",lambda:self._change_status("annule"),bg=C_RED).pack(fill="x",pady=2)

    def _load_orders(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn(); c = conn.cursor()
        status_filter = self.filter_var.get()
        table_filter = self.table_filter.get().strip()

        query = """SELECT o.id, t.number, o.client_name, o.created_at,
                   COUNT(oi.id), o.total, o.status, u.full_name
                   FROM orders o
                   LEFT JOIN tables t ON o.table_id=t.id
                   LEFT JOIN users u ON o.user_id=u.id
                   LEFT JOIN order_items oi ON oi.order_id=o.id
                   WHERE 1=1"""
        params = []
        if status_filter != "tous":
            query += " AND o.status=?"; params.append(status_filter)
        if table_filter:
            query += " AND t.number=?"; params.append(table_filter)
        query += " GROUP BY o.id ORDER BY o.id DESC"
        c.execute(query, params)
        smap={"en_cours":"En cours","servi":"Servi","paye":"Payé","annule":"Annulé"}
        for row in c.fetchall():
            oid,tnum,client,cat,nb,total,status,srv = row
            heure = cat[11:16] if cat else "-"
            self.tree.insert("","end",iid=str(oid),
                values=(f"#{oid}",f"T{tnum}"if tnum else"-",client or"-",heure,
                        f"{nb} art.",f"{fmt(total)} F",smap.get(status,status),srv or"-"),
                tags=(status,))
        conn.close()

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        oid = int(sel[0])
        self._show_detail(oid)

    def _show_detail(self, oid):
        for w in self.detail_frame.winfo_children():
            w.destroy()
        conn = get_conn(); c = conn.cursor()
        c.execute("""SELECT o.*, t.number, u.full_name FROM orders o
                     LEFT JOIN tables t ON o.table_id=t.id
                     LEFT JOIN users u ON o.user_id=u.id
                     WHERE o.id=?""", (oid,))
        o = c.fetchone()
        if not o: conn.close(); return

        smap={"en_cours":"🟡 En cours","servi":"🟢 Servi","paye":"🔵 Payé","annule":"🔴 Annulé"}
        fields = [
            ("Commande N°", f"#{o['id']}"),
            ("Table", f"N°{o['number']}" if o['number'] else "-"),
            ("Client", o['client_name'] or "-"),
            ("Serveur", o['full_name'] or "-"),
            ("Date/Heure", (o['created_at'] or "")[:16]),
            ("Statut", smap.get(o['status'], o['status'])),
        ]
        for lbl, val in fields:
            row = tk.Frame(self.detail_frame, bg=C_WHITE)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=lbl+":", font=("Helvetica",9,"bold"),
                     bg=C_WHITE, fg=C_GRAY, width=12, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=FONT_SMALL, bg=C_WHITE, fg=C_DARK,
                     anchor="w").pack(side="left")

        tk.Frame(self.detail_frame, bg="#EEEEEE", height=1).pack(fill="x", pady=6)
        tk.Label(self.detail_frame, text="Articles:", font=FONT_BOLD,
                 bg=C_WHITE, fg=C_DARK).pack(anchor="w")

        c.execute("""SELECT m.name, oi.quantity, oi.unit_price, oi.status, oi.notes
                     FROM order_items oi JOIN menu_items m ON oi.menu_item_id=m.id
                     WHERE oi.order_id=?""", (oid,))
        total = 0
        for item in c.fetchall():
            sub = item[1]*item[2]; total += sub
            row = tk.Frame(self.detail_frame, bg=C_LIGHT)
            row.pack(fill="x", pady=1, padx=2)
            tk.Label(row, text=f"{item[1]}x {item[0][:20]}", font=FONT_SMALL,
                     bg=C_LIGHT, fg=C_DARK, anchor="w").pack(side="left", padx=4, pady=3)
            tk.Label(row, text=f"{fmt(sub)} F", font=("Helvetica",9,"bold"),
                     bg=C_LIGHT, fg=C_GOLD).pack(side="right", padx=4)

        tk.Frame(self.detail_frame, bg=C_GOLD, height=1).pack(fill="x", pady=4)
        tot_row = tk.Frame(self.detail_frame, bg=C_WHITE)
        tot_row.pack(fill="x")
        tk.Label(tot_row, text="TOTAL:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack(side="left")
        tk.Label(tot_row, text=f"{fmt(total)} FCFA", font=("Helvetica",13,"bold"),
                 bg=C_WHITE, fg=C_GOLD).pack(side="right")
        if o['notes']:
            tk.Label(self.detail_frame, text=f"📝 {o['notes']}", font=FONT_SMALL,
                     bg=C_WHITE, fg=C_GRAY, wraplength=260, justify="left").pack(anchor="w", pady=4)
        conn.close()

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner une commande.")
            return None
        return int(sel[0])

    def _change_status(self, new_status):
        oid = self._get_selected_id()
        if not oid: return
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT status FROM orders WHERE id=?", (oid,))
        row = c.fetchone()
        if row and row[0] == 'paye':
            messagebox.showinfo("Info", "Cette commande est déjà payée.")
            conn.close(); return
        if new_status == "annule":
            if not messagebox.askyesno("Annuler", f"Annuler la commande #{oid} ?"): conn.close(); return
        c.execute("UPDATE orders SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (new_status, oid))
        if new_status in ('en_cours','servi','annule'):
            c.execute("UPDATE tables SET status=? WHERE id=(SELECT table_id FROM orders WHERE id=?)",
                      ('libre' if new_status=='annule' else 'occupee', oid))
        conn.commit(); conn.close()
        self._load_orders()

    def _encaisser(self):
        oid = self._get_selected_id()
        if not oid: return
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT status, total FROM orders WHERE id=?", (oid,))
        row = c.fetchone()
        if not row: conn.close(); return
        if row[0] == 'paye':
            messagebox.showinfo("Info", "Commande déjà payée."); conn.close(); return
        conn.close()
        PaymentDialog(self, oid, row[1], self._load_orders)

    def _new_order(self):
        OrderEditDialog(self, None, self.user, self._load_orders)

    def _open_order(self):
        oid = self._get_selected_id()
        if not oid: return
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT status FROM orders WHERE id=?", (oid,))
        row = c.fetchone(); conn.close()
        if row and row[0] == 'paye':
            messagebox.showinfo("Info","Commande payée, non modifiable."); return
        OrderEditDialog(self, oid, self.user, self._load_orders)


# ─── Dialogue: Créer/Modifier commande ───────────────────────────
class OrderEditDialog(tk.Toplevel):
    def __init__(self, parent, order_id, user, callback):
        super().__init__(parent)
        self.order_id = order_id
        self.user = user
        self.callback = callback
        self.cart = []  # list of {menu_item_id, name, price, qty, notes}
        self.title("Nouvelle Commande" if not order_id else f"Modifier Commande #{order_id}")
        self.geometry("950x680")
        self.resizable(True, True)
        self.configure(bg=C_BG)
        self._center()
        self._build()
        if order_id:
            self._load_existing()
        self.grab_set()

    def _center(self):
        self.update_idletasks()
        x=(self.winfo_screenwidth()-950)//2; y=(self.winfo_screenheight()-680)//2
        self.geometry(f"950x680+{x}+{y}")

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C_DARK, pady=12)
        hdr.pack(fill="x")
        title = "Nouvelle Commande" if not self.order_id else f"Modifier Commande #{self.order_id}"
        tk.Label(hdr, text=f"🧾  {title}", font=FONT_HEADER,
                 bg=C_DARK, fg=C_GOLD, padx=20).pack(side="left")

        # Info bar: table + client
        info = tk.Frame(self, bg=C_WHITE, pady=8)
        info.pack(fill="x", padx=16, pady=(8,0))
        tk.Label(info, text="Table N°:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=8).pack(side="left")
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT number FROM tables ORDER BY number")
        table_nums = [str(r[0]) for r in c.fetchall()]
        conn.close()
        self.table_var = tk.StringVar()
        table_cb = ttk.Combobox(info, textvariable=self.table_var, values=table_nums, width=5, font=FONT_NORM)
        table_cb.pack(side="left", padx=4)
        tk.Label(info, text="Client:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=8).pack(side="left")
        self.client_entry = tk.Entry(info, font=FONT_NORM, width=20, relief="solid", bd=1)
        self.client_entry.pack(side="left", padx=4)
        tk.Label(info, text="Notes:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=8).pack(side="left")
        self.notes_entry = tk.Entry(info, font=FONT_NORM, width=22, relief="solid", bd=1)
        self.notes_entry.pack(side="left", padx=4)

        # Main: menu left, cart right
        main = tk.Frame(self, bg=C_BG)
        main.pack(fill="both", expand=True, padx=16, pady=8)

        # Menu panel
        menu_panel = tk.Frame(main, bg=C_WHITE, highlightthickness=1, highlightbackground="#E0E0E0")
        menu_panel.pack(side="left", fill="both", expand=True)
        tk.Label(menu_panel, text="Menu", font=FONT_HEADER, bg=C_WHITE, fg=C_DARK, pady=8).pack(anchor="w", padx=12)

        # Category tabs
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id, name, color FROM categories")
        self.categories = c.fetchall()
        conn.close()

        cat_bar = tk.Frame(menu_panel, bg="#EEEEEE")
        cat_bar.pack(fill="x", padx=12, pady=(0,6))
        self.cat_var = tk.IntVar(value=0)

        def load_cat(cat_id):
            self.cat_var.set(cat_id)
            self._load_menu_items(cat_id)
            for btn_id, b in self.cat_buttons.items():
                b.config(bg=C_GOLD if btn_id==cat_id else C_WHITE,
                         fg=C_WHITE if btn_id==cat_id else C_DARK)

        self.cat_buttons = {}
        btn_all = tk.Button(cat_bar, text="Tous", font=FONT_SMALL, bg=C_GOLD, fg=C_WHITE,
                            relief="flat", bd=0, padx=8, pady=5, cursor="hand2",
                            command=lambda: load_cat(0))
        btn_all.pack(side="left", padx=2, pady=4)
        self.cat_buttons[0] = btn_all
        for cid, cname, ccolor in self.categories:
            b = tk.Button(cat_bar, text=cname, font=FONT_SMALL, bg=C_WHITE, fg=C_DARK,
                          relief="flat", bd=1, padx=8, pady=5, cursor="hand2",
                          command=lambda ci=cid: load_cat(ci))
            b.pack(side="left", padx=2, pady=4)
            self.cat_buttons[cid] = b

        # Search
        search_frame = tk.Frame(menu_panel, bg=C_WHITE)
        search_frame.pack(fill="x", padx=12, pady=(0,4))
        tk.Label(search_frame, text="🔍", font=FONT_NORM, bg=C_WHITE).pack(side="left")
        self.search_var = tk.StringVar()
        se = tk.Entry(search_frame, textvariable=self.search_var, font=FONT_NORM,
                      relief="solid", bd=1, width=25)
        se.pack(side="left", padx=4)
        self.search_var.trace("w", lambda *a: self._load_menu_items(self.cat_var.get()))

        # Menu items grid in scrollable frame
        canvas = tk.Canvas(menu_panel, bg=C_WHITE, highlightthickness=0)
        vsb = ttk.Scrollbar(menu_panel, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True, padx=12)
        self.items_frame = tk.Frame(canvas, bg=C_WHITE)
        self.items_win = canvas.create_window((0,0), window=self.items_frame, anchor="nw")
        self.items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(self.items_win, width=e.width))
        self._load_menu_items(0)

        # Cart panel
        cart_panel = tk.Frame(main, bg=C_WHITE, width=300,
                              highlightthickness=1, highlightbackground="#E0E0E0")
        cart_panel.pack(side="right", fill="y", padx=(8,0))
        cart_panel.pack_propagate(False)
        tk.Label(cart_panel, text="🛒  Panier", font=FONT_HEADER,
                 bg=C_WHITE, fg=C_DARK, pady=8).pack(anchor="w", padx=12)
        tk.Frame(cart_panel, bg=C_GOLD, height=2).pack(fill="x", padx=12, pady=(0,6))

        # Cart items
        self.cart_canvas = tk.Canvas(cart_panel, bg=C_WHITE, highlightthickness=0)
        cart_vsb = ttk.Scrollbar(cart_panel, orient="vertical", command=self.cart_canvas.yview)
        self.cart_canvas.configure(yscrollcommand=cart_vsb.set)
        cart_vsb.pack(side="right", fill="y")
        self.cart_canvas.pack(fill="both", expand=True, padx=4)
        self.cart_inner = tk.Frame(self.cart_canvas, bg=C_WHITE)
        self.cart_inner_win = self.cart_canvas.create_window((0,0), window=self.cart_inner, anchor="nw")
        self.cart_inner.bind("<Configure>", lambda e: self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all")))

        # Total & save
        footer = tk.Frame(cart_panel, bg=C_WHITE)
        footer.pack(fill="x", padx=12, pady=8)
        tk.Frame(footer, bg=C_GOLD, height=1).pack(fill="x", pady=(0,6))
        self.total_label = tk.Label(footer, text="TOTAL: 0 FCFA",
                                    font=("Helvetica",13,"bold"), bg=C_WHITE, fg=C_GOLD)
        self.total_label.pack(anchor="e", pady=4)
        btn(footer,"💾 Enregistrer", self._save, bg=C_GREEN, py=10).pack(fill="x", pady=2)
        btn(footer,"✖ Fermer", self.destroy, bg=C_RED, py=10).pack(fill="x", pady=2)

    def _load_menu_items(self, cat_id):
        for w in self.items_frame.winfo_children():
            w.destroy()
        conn = get_conn(); c = conn.cursor()
        search = self.search_var.get().strip()
        if cat_id == 0:
            if search:
                c.execute("SELECT id,name,description,price FROM menu_items WHERE available=1 AND name LIKE ? ORDER BY name",
                          (f"%{search}%",))
            else:
                c.execute("SELECT id,name,description,price FROM menu_items WHERE available=1 ORDER BY category_id,name")
        else:
            if search:
                c.execute("SELECT id,name,description,price FROM menu_items WHERE available=1 AND category_id=? AND name LIKE ? ORDER BY name",
                          (cat_id, f"%{search}%"))
            else:
                c.execute("SELECT id,name,description,price FROM menu_items WHERE available=1 AND category_id=? ORDER BY name",
                          (cat_id,))
        items = c.fetchall(); conn.close()

        cols = 3
        for idx, (iid, name, desc, price) in enumerate(items):
            row_n = idx // cols; col_n = idx % cols
            card = tk.Frame(self.items_frame, bg=C_WHITE, bd=1, relief="solid",
                            highlightthickness=1, highlightbackground="#E0E0E0",
                            cursor="hand2")
            card.grid(row=row_n, column=col_n, padx=4, pady=4, sticky="nsew")
            self.items_frame.columnconfigure(col_n, weight=1)
            tk.Label(card, text=name[:22], font=FONT_BOLD, bg=C_WHITE, fg=C_DARK,
                     wraplength=140, justify="left").pack(anchor="w", padx=8, pady=(8,2))
            if desc:
                tk.Label(card, text=desc[:40], font=("Helvetica",8), bg=C_WHITE, fg=C_GRAY,
                         wraplength=140, justify="left").pack(anchor="w", padx=8)
            price_row = tk.Frame(card, bg=C_WHITE)
            price_row.pack(fill="x", padx=8, pady=(4,6))
            tk.Label(price_row, text=f"{fmt(price)} F", font=("Helvetica",10,"bold"),
                     bg=C_WHITE, fg=C_GOLD).pack(side="left")
            tk.Button(price_row, text="+ Ajouter", font=FONT_SMALL, bg=C_GREEN, fg=C_WHITE,
                      relief="flat", bd=0, padx=6, pady=3, cursor="hand2",
                      command=lambda i=iid,n=name,p=price: self._add_to_cart(i,n,p)).pack(side="right")
            card.bind("<Double-1>", lambda e,i=iid,n=name,p=price: self._add_to_cart(i,n,p))

    def _add_to_cart(self, item_id, name, price):
        for item in self.cart:
            if item['menu_item_id'] == item_id:
                item['qty'] += 1
                self._render_cart()
                return
        self.cart.append({'menu_item_id': item_id, 'name': name, 'price': price, 'qty': 1, 'notes': ''})
        self._render_cart()

    def _render_cart(self):
        for w in self.cart_inner.winfo_children():
            w.destroy()
        total = 0
        for idx, item in enumerate(self.cart):
            sub = item['qty'] * item['price']; total += sub
            row = tk.Frame(self.cart_inner, bg=C_LIGHT if idx%2==0 else C_WHITE)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=item['name'][:18], font=FONT_SMALL,
                     bg=row['bg'], fg=C_DARK, anchor="w", width=16).pack(side="left", padx=4, pady=4)
            # qty controls
            ctrl = tk.Frame(row, bg=row['bg'])
            ctrl.pack(side="left")
            tk.Button(ctrl, text="-", font=FONT_BOLD, bg="#FF7043", fg=C_WHITE,
                      relief="flat", bd=0, width=2, cursor="hand2",
                      command=lambda i=idx: self._change_qty(i,-1)).pack(side="left")
            tk.Label(ctrl, text=str(item['qty']), font=FONT_BOLD, bg=row['bg'],
                     fg=C_DARK, width=3).pack(side="left")
            tk.Button(ctrl, text="+", font=FONT_BOLD, bg=C_GREEN, fg=C_WHITE,
                      relief="flat", bd=0, width=2, cursor="hand2",
                      command=lambda i=idx: self._change_qty(i,1)).pack(side="left")
            tk.Label(row, text=f"{fmt(sub)}F", font=("Helvetica",9,"bold"),
                     bg=row['bg'], fg=C_GOLD).pack(side="right", padx=6)
        self.total_label.config(text=f"TOTAL: {fmt(total)} FCFA")

    def _change_qty(self, idx, delta):
        self.cart[idx]['qty'] += delta
        if self.cart[idx]['qty'] <= 0:
            self.cart.pop(idx)
        self._render_cart()

    def _load_existing(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT o.*, t.number FROM orders o LEFT JOIN tables t ON o.table_id=t.id WHERE o.id=?",
                  (self.order_id,))
        o = c.fetchone()
        if not o: conn.close(); return
        if o['number']: self.table_var.set(str(o['number']))
        if o['client_name']: self.client_entry.insert(0, o['client_name'])
        if o['notes']: self.notes_entry.insert(0, o['notes'])
        c.execute("SELECT oi.menu_item_id, m.name, oi.unit_price, oi.quantity FROM order_items oi JOIN menu_items m ON oi.menu_item_id=m.id WHERE oi.order_id=?", (self.order_id,))
        for row in c.fetchall():
            self.cart.append({'menu_item_id':row[0],'name':row[1],'price':row[2],'qty':row[3],'notes':''})
        conn.close()
        self._render_cart()

    def _save(self):
        if not self.cart:
            messagebox.showwarning("Panier vide", "Veuillez ajouter des articles."); return
        table_num = self.table_var.get().strip()
        client = self.client_entry.get().strip()
        notes = self.notes_entry.get().strip()
        total = sum(i['qty']*i['price'] for i in self.cart)

        conn = get_conn(); c = conn.cursor()
        table_id = None
        if table_num:
            c.execute("SELECT id FROM tables WHERE number=?", (table_num,))
            t = c.fetchone()
            if t: table_id = t[0]

        if self.order_id:
            c.execute("UPDATE orders SET table_id=?,client_name=?,notes=?,total=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                      (table_id, client, notes, total, self.order_id))
            c.execute("DELETE FROM order_items WHERE order_id=?", (self.order_id,))
        else:
            c.execute("INSERT INTO orders (table_id,user_id,client_name,notes,total,status) VALUES (?,?,?,?,?,?)",
                      (table_id, self.user['id'], client, notes, total, 'en_cours'))
            self.order_id = c.lastrowid

        for item in self.cart:
            c.execute("INSERT INTO order_items (order_id,menu_item_id,quantity,unit_price) VALUES (?,?,?,?)",
                      (self.order_id, item['menu_item_id'], item['qty'], item['price']))

        if table_id:
            c.execute("UPDATE tables SET status='occupee' WHERE id=?", (table_id,))

        conn.commit(); conn.close()
        messagebox.showinfo("Succès", f"Commande #{self.order_id} enregistrée !")
        self.callback()
        self.destroy()


# ─── Dialogue: Encaissement ──────────────────────────────────────
class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, order_id, total, callback):
        super().__init__(parent)
        self.order_id = order_id
        self.total = total
        self.callback = callback
        self.title(f"Encaissement - Commande #{order_id}")
        self.geometry("460x420")
        self.resizable(False, False)
        self.configure(bg=C_BG)
        x=(self.winfo_screenwidth()-460)//2; y=(self.winfo_screenheight()-420)//2
        self.geometry(f"460x420+{x}+{y}")
        self._build()
        self.grab_set()

    def _build(self):
        tk.Frame(self, bg=C_GOLD, height=8).pack(fill="x")
        tk.Label(self, text=f"💰  Encaisser Commande #{self.order_id}",
                 font=FONT_HEADER, bg=C_BG, fg=C_DARK, pady=14).pack()

        card = tk.Frame(self, bg=C_WHITE, padx=30, pady=20)
        card.pack(fill="x", padx=30)

        tk.Label(card, text=f"Montant total à payer:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack()
        tk.Label(card, text=f"{fmt(self.total)} FCFA", font=("Helvetica",20,"bold"),
                 bg=C_WHITE, fg=C_GOLD).pack(pady=4)

        tk.Frame(card, bg="#EEEEEE", height=1).pack(fill="x", pady=10)

        # TVA toggle
        self.tva_var = tk.BooleanVar(value=False)
        tva_frame = tk.Frame(card, bg=C_WHITE)
        tva_frame.pack(fill="x")
        tk.Checkbutton(tva_frame, text="Appliquer TVA (19.25%)", variable=self.tva_var,
                       font=FONT_NORM, bg=C_WHITE, cursor="hand2",
                       command=self._update_tva).pack(side="left")
        self.tva_label = tk.Label(tva_frame, text="", font=FONT_NORM, bg=C_WHITE, fg=C_RED)
        self.tva_label.pack(side="right")
        self.total_ttc_label = tk.Label(card, text=f"Total TTC: {fmt(self.total)} FCFA",
                                        font=FONT_BOLD, bg=C_WHITE, fg=C_DARK)
        self.total_ttc_label.pack(pady=(4,10))

        tk.Label(card, text="Mode de paiement:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK).pack(anchor="w")
        self.pay_var = tk.StringVar(value="especes")
        pays = [("💵 Espèces","especes"),("💳 Carte Bancaire","carte"),
                ("📱 Mobile Money","mobile_money"),("🏦 Virement","virement")]
        frm = tk.Frame(card, bg=C_WHITE)
        frm.pack(fill="x", pady=6)
        for lbl, val in pays:
            tk.Radiobutton(frm, text=lbl, variable=self.pay_var, value=val,
                           font=FONT_NORM, bg=C_WHITE, cursor="hand2").pack(side="left", padx=6)

        btn_frame = tk.Frame(self, bg=C_BG)
        btn_frame.pack(fill="x", padx=30, pady=16)
        btn(btn_frame,"✔ Confirmer le Paiement",self._confirm,bg=C_GREEN,py=12).pack(fill="x",pady=4)
        btn(btn_frame,"✖ Annuler",self.destroy,bg=C_RED,py=10).pack(fill="x")

    def _update_tva(self):
        if self.tva_var.get():
            tva = self.total * 0.1925
            ttc = self.total + tva
            self.tva_label.config(text=f"+{fmt(tva)} F")
            self.total_ttc_label.config(text=f"Total TTC: {fmt(ttc)} FCFA")
        else:
            self.tva_label.config(text="")
            self.total_ttc_label.config(text=f"Total TTC: {fmt(self.total)} FCFA")

    def _confirm(self):
        tva = self.total * 0.1925 if self.tva_var.get() else 0
        total_ttc = self.total + tva
        pay_method = self.pay_var.get()
        from datetime import datetime
        inv_num = f"FAC{datetime.now().strftime('%Y%m%d%H%M%S')}"

        conn = get_conn(); c = conn.cursor()
        c.execute("UPDATE orders SET status='paye', updated_at=CURRENT_TIMESTAMP WHERE id=?", (self.order_id,))
        c.execute("UPDATE tables SET status='libre' WHERE id=(SELECT table_id FROM orders WHERE id=?)",
                  (self.order_id,))
        c.execute("""INSERT INTO invoices (order_id,invoice_number,total_ht,tva,total_ttc,payment_method)
                     VALUES (?,?,?,?,?,?)""", (self.order_id, inv_num, self.total, tva, total_ttc, pay_method))
        inv_id = c.lastrowid
        conn.commit()

        # Generate PDF
        c.execute("""SELECT o.*, t.number, u.full_name FROM orders o
                     LEFT JOIN tables t ON o.table_id=t.id
                     LEFT JOIN users u ON o.user_id=u.id WHERE o.id=?""", (self.order_id,))
        o = c.fetchone()
        c.execute("""SELECT m.name, oi.quantity, oi.unit_price FROM order_items oi
                     JOIN menu_items m ON oi.menu_item_id=m.id WHERE oi.order_id=?""", (self.order_id,))
        items = [{"name":r[0],"quantity":r[1],"unit_price":r[2]} for r in c.fetchall()]
        conn.close()

        from modules.pdf_generator import generate_invoice
        from datetime import datetime as dt
        inv_data = {
            "invoice_number": inv_num,
            "table_number": o['number'] if o else "-",
            "client_name": (o['client_name'] if o else "") or "Client",
            "serveur": (o['full_name'] if o else "") or "-",
            "paid_at": dt.now().strftime("%d/%m/%Y %H:%M"),
            "payment_method": pay_method,
            "items": items,
            "total_ht": self.total,
            "tva": tva,
            "total_ttc": total_ttc,
        }
        pdf_path = generate_invoice(inv_data)
        messagebox.showinfo("Paiement enregistré",
            f"✅ Paiement confirmé !\nFacture N°: {inv_num}\n\nPDF généré:\n{pdf_path}")
        try:
            import subprocess, sys
            if sys.platform == "win32": os.startfile(pdf_path)
            elif sys.platform == "darwin": subprocess.run(["open", pdf_path])
            else: subprocess.run(["xdg-open", pdf_path])
        except: pass
        self.callback()
        self.destroy()
