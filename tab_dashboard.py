import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from modules.database import get_conn

C_GOLD="#C8860A"; C_DARK="#1A1A2E"; C_DARK2="#16213E"; C_PANEL="#0F3460"
C_WHITE="#FFFFFF"; C_LIGHT="#F5F5F5"; C_GRAY="#AAAAAA"
C_GREEN="#27AE60"; C_RED="#E74C3C"; C_ORANGE="#F39C12"; C_BLUE="#2980B9"; C_BG="#F0F2F5"
FONT_TITLE=("Helvetica",22,"bold"); FONT_HEADER=("Helvetica",14,"bold")
FONT_BOLD=("Helvetica",11,"bold"); FONT_NORM=("Helvetica",10); FONT_SMALL=("Helvetica",9)

def fmt(n): return "{:,.0f}".format(n).replace(",", " ")

class DashboardTab(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C_BG)
        self.user = user
        self._build()
        self._refresh()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C_BG)
        hdr.pack(fill="x", padx=24, pady=(18,8))
        tk.Label(hdr, text="📊  Tableau de Bord", font=FONT_TITLE, bg=C_BG, fg=C_DARK).pack(side="left")
        self.date_lbl = tk.Label(hdr, text="", font=FONT_NORM, bg=C_BG, fg=C_GRAY)
        self.date_lbl.pack(side="right")
        tk.Button(hdr, text="↻ Actualiser", font=FONT_SMALL, bg=C_GOLD, fg=C_WHITE,
                  relief="flat", bd=0, padx=10, pady=6, cursor="hand2",
                  command=self._refresh).pack(side="right", padx=10)

        # KPI row
        self.kpi_frame = tk.Frame(self, bg=C_BG)
        self.kpi_frame.pack(fill="x", padx=24, pady=(0,12))

        # Middle row: recent orders + table status
        mid = tk.Frame(self, bg=C_BG)
        mid.pack(fill="both", expand=True, padx=24, pady=(0,12))

        # Recent orders
        left = tk.Frame(mid, bg=C_WHITE, bd=0, relief="flat",
                        highlightthickness=1, highlightbackground="#E0E0E0")
        left.pack(side="left", fill="both", expand=True, padx=(0,8))
        tk.Label(left, text="🧾  Commandes Récentes", font=FONT_HEADER,
                 bg=C_WHITE, fg=C_DARK, pady=10).pack(anchor="w", padx=14)
        tk.Frame(left, bg=C_GOLD, height=2).pack(fill="x", padx=14, pady=(0,6))

        cols = ("N°","Table","Heure","Serveur","Total","Statut")
        self.orders_tree = ttk.Treeview(left, columns=cols, show="headings", height=10)
        widths = [50,60,80,110,110,100]
        for col, w in zip(cols, widths):
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=w, anchor="center")
        self.orders_tree.tag_configure("en_cours", foreground=C_ORANGE)
        self.orders_tree.tag_configure("servi", foreground=C_GREEN)
        self.orders_tree.tag_configure("paye", foreground=C_BLUE)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y", padx=(0,8))
        self.orders_tree.pack(fill="both", expand=True, padx=14, pady=(0,14))

        # Right column: table status + top items
        right = tk.Frame(mid, bg=C_BG, width=280)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # Table status card
        tbl_card = tk.Frame(right, bg=C_WHITE, highlightthickness=1, highlightbackground="#E0E0E0")
        tbl_card.pack(fill="x", pady=(0,8))
        tk.Label(tbl_card, text="🪑  Tables", font=FONT_HEADER, bg=C_WHITE, fg=C_DARK, pady=8).pack(anchor="w", padx=14)
        tk.Frame(tbl_card, bg=C_GOLD, height=2).pack(fill="x", padx=14, pady=(0,8))
        self.table_status_frame = tk.Frame(tbl_card, bg=C_WHITE)
        self.table_status_frame.pack(fill="x", padx=14, pady=(0,12))

        # Top selling card
        top_card = tk.Frame(right, bg=C_WHITE, highlightthickness=1, highlightbackground="#E0E0E0")
        top_card.pack(fill="both", expand=True)
        tk.Label(top_card, text="⭐  Top Ventes Aujourd'hui", font=FONT_BOLD,
                 bg=C_WHITE, fg=C_DARK, pady=8).pack(anchor="w", padx=14)
        tk.Frame(top_card, bg=C_GOLD, height=2).pack(fill="x", padx=14, pady=(0,8))
        self.top_frame = tk.Frame(top_card, bg=C_WHITE)
        self.top_frame.pack(fill="both", expand=True, padx=14, pady=(0,12))

    def _kpi_card(self, parent, title, value, sub, color, icon):
        card = tk.Frame(parent, bg=color, width=160, height=110)
        card.pack(side="left", padx=6, fill="y")
        card.pack_propagate(False)
        tk.Label(card, text=icon, font=("Helvetica", 24), bg=color, fg=C_WHITE).pack(pady=(10,0))
        tk.Label(card, text=value, font=("Helvetica", 14, "bold"), bg=color, fg=C_WHITE).pack()
        tk.Label(card, text=title, font=("Helvetica", 9, "bold"), bg=color, fg=C_WHITE).pack()
        tk.Label(card, text=sub, font=("Helvetica", 8), bg=color, fg="#FFFFFFAA").pack()

    def _refresh(self):
        today = date.today().isoformat()
        self.date_lbl.config(text=datetime.now().strftime("%A %d %B %Y"))
        conn = get_conn()
        c = conn.cursor()

        # KPIs
        c.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at)=? AND status!='annule'", (today,))
        nb_orders = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE DATE(created_at)=? AND status='paye'", (today,))
        ca_day = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE strftime('%Y-%m',created_at)=? AND status='paye'",
                  (today[:7],))
        ca_month = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM tables WHERE status='occupee'")
        nb_occ = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM tables")
        nb_total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM reservations WHERE date=?", (today,))
        nb_resa = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM orders WHERE status='en_cours'")
        nb_active = c.fetchone()[0]

        for w in self.kpi_frame.winfo_children():
            w.destroy()

        kpis = [
            ("CA Aujourd'hui", f"{fmt(ca_day)} F", f"Commandes: {nb_orders}", C_GOLD, "💵"),
            ("CA du Mois", f"{fmt(ca_month)} F", today[:7], "#8E44AD", "📈"),
            ("Tables Occupées", f"{nb_occ} / {nb_total}", "En ce moment", C_BLUE, "🪑"),
            ("Cmds Actives", str(nb_active), "En cours", C_ORANGE, "🔥"),
            ("Réservations", str(nb_resa), "Aujourd'hui", C_GREEN, "📅"),
        ]
        for t, v, s, col, ic in kpis:
            self._kpi_card(self.kpi_frame, t, v, s, col, ic)

        # Recent orders
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)
        c.execute("""SELECT o.id, t.number, o.created_at, u.full_name, o.total, o.status
                     FROM orders o
                     LEFT JOIN tables t ON o.table_id=t.id
                     LEFT JOIN users u ON o.user_id=u.id
                     ORDER BY o.id DESC LIMIT 20""")
        status_map = {"en_cours":"En cours","servi":"Servi","paye":"Payé","annule":"Annulé"}
        for row in c.fetchall():
            oid, tnum, cat, srv, total, status = row
            heure = cat[11:16] if cat and len(cat) > 15 else "-"
            lbl = status_map.get(status, status)
            self.orders_tree.insert("", "end",
                values=(f"#{oid}", f"T{tnum}" if tnum else "-", heure,
                        srv or "-", f"{fmt(total)} F", lbl),
                tags=(status,))

        # Table status
        for w in self.table_status_frame.winfo_children():
            w.destroy()
        c.execute("SELECT number, status, section FROM tables ORDER BY number")
        tables = c.fetchall()
        colors_map = {"libre": C_GREEN, "occupee": C_RED, "reservee": C_ORANGE, "nettoyage": C_BLUE}
        row_f = tk.Frame(self.table_status_frame, bg=C_WHITE)
        row_f.pack(fill="x")
        for i, (num, status, section) in enumerate(tables):
            col = colors_map.get(status, C_GRAY)
            card = tk.Frame(row_f, bg=col, width=48, height=40)
            card.pack(side="left", padx=3, pady=3)
            card.pack_propagate(False)
            tk.Label(card, text=f"T{num}", font=("Helvetica", 9, "bold"),
                     bg=col, fg=C_WHITE).place(relx=0.5, rely=0.5, anchor="center")
            if (i+1) % 5 == 0:
                row_f = tk.Frame(self.table_status_frame, bg=C_WHITE)
                row_f.pack(fill="x")

        leg = tk.Frame(self.table_status_frame, bg=C_WHITE)
        leg.pack(fill="x", pady=(6,0))
        for txt, col in [("Libre",C_GREEN),("Occupée",C_RED),("Réservée",C_ORANGE)]:
            f = tk.Frame(leg, bg=C_WHITE)
            f.pack(side="left", padx=4)
            tk.Label(f, bg=col, width=2, height=1).pack(side="left")
            tk.Label(f, text=txt, font=("Helvetica",8), bg=C_WHITE, fg=C_DARK).pack(side="left", padx=2)

        # Top selling
        for w in self.top_frame.winfo_children():
            w.destroy()
        c.execute("""SELECT m.name, SUM(oi.quantity) as qty
                     FROM order_items oi
                     JOIN menu_items m ON oi.menu_item_id=m.id
                     JOIN orders o ON oi.order_id=o.id
                     WHERE DATE(o.created_at)=?
                     GROUP BY m.id ORDER BY qty DESC LIMIT 5""", (today,))
        top_items = c.fetchall()
        if top_items:
            max_qty = top_items[0][1] if top_items else 1
            for rank, (name, qty) in enumerate(top_items, 1):
                row = tk.Frame(self.top_frame, bg=C_WHITE)
                row.pack(fill="x", pady=2)
                tk.Label(row, text=f"{rank}.", font=FONT_BOLD, bg=C_WHITE, fg=C_GOLD,
                         width=3).pack(side="left")
                tk.Label(row, text=name[:20], font=FONT_SMALL, bg=C_WHITE, fg=C_DARK,
                         width=18, anchor="w").pack(side="left")
                tk.Label(row, text=f"x{qty}", font=FONT_BOLD, bg=C_WHITE,
                         fg=C_BLUE).pack(side="right")
                bar_bg = tk.Frame(self.top_frame, bg="#EEEEEE", height=5)
                bar_bg.pack(fill="x", padx=24, pady=(0,2))
                pct = int((qty / max_qty) * 100)
                tk.Frame(bar_bg, bg=C_GOLD, height=5).place(relwidth=pct/100, relheight=1)
        else:
            tk.Label(self.top_frame, text="Aucune vente aujourd'hui",
                     font=FONT_SMALL, bg=C_WHITE, fg=C_GRAY).pack(pady=20)
        conn.close()
