import tkinter as tk
from tkinter import ttk, messagebox, font
import os, sys

sys.path.insert(0, os.path.dirname(__file__))
from modules.database import init_db, authenticate

# ── Palette de couleurs ──────────────────────────────────────────
C_GOLD   = "#C8860A"
C_GOLD2  = "#E6A020"
C_DARK   = "#1A1A2E"
C_DARK2  = "#16213E"
C_PANEL  = "#0F3460"
C_WHITE  = "#FFFFFF"
C_LIGHT  = "#F5F5F5"
C_GRAY   = "#AAAAAA"
C_GREEN  = "#27AE60"
C_RED    = "#E74C3C"
C_ORANGE = "#F39C12"
C_BLUE   = "#2980B9"
C_BG     = "#F0F2F5"

# ── Polices ──────────────────────────────────────────────────────
FONT_TITLE  = ("Helvetica", 22, "bold")
FONT_HEADER = ("Helvetica", 14, "bold")
FONT_BOLD   = ("Helvetica", 11, "bold")
FONT_NORM   = ("Helvetica", 10)
FONT_SMALL  = ("Helvetica", 9)

def styled_button(parent, text, command=None, bg=C_GOLD, fg=C_WHITE, font=FONT_BOLD,
                  padx=16, pady=8, width=None, cursor="hand2", radius=6):
    btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                    font=font, relief="flat", bd=0,
                    padx=padx, pady=pady, cursor=cursor,
                    activebackground=C_GOLD2, activeforeground=C_WHITE)
    if width:
        btn.config(width=width)
    return btn

def entry_field(parent, placeholder="", show=None, width=30):
    frame = tk.Frame(parent, bg=C_WHITE, bd=1, relief="solid",
                     highlightthickness=1, highlightbackground="#CCCCCC",
                     highlightcolor=C_GOLD)
    e = tk.Entry(frame, font=FONT_NORM, bd=0, relief="flat",
                 bg=C_WHITE, fg=C_DARK, insertbackground=C_DARK,
                 width=width)
    if show:
        e.config(show=show)
    e.pack(padx=8, pady=6, fill="x")

    def on_focus_in(event):
        frame.config(highlightbackground=C_GOLD, highlightcolor=C_GOLD)
    def on_focus_out(event):
        frame.config(highlightbackground="#CCCCCC")
    e.bind("<FocusIn>", on_focus_in)
    e.bind("<FocusOut>", on_focus_out)

    if placeholder:
        e.insert(0, placeholder)
        e.config(fg=C_GRAY)
        def on_click(event):
            if e.get() == placeholder:
                e.delete(0, tk.END)
                e.config(fg=C_DARK)
                if show: e.config(show=show)
        def on_leave(event):
            if e.get() == "":
                e.insert(0, placeholder)
                e.config(fg=C_GRAY)
                if show: e.config(show="")
        e.bind("<FocusIn>", lambda ev: (on_click(ev), on_focus_in(ev)))
        e.bind("<FocusOut>", lambda ev: (on_leave(ev), on_focus_out(ev)))

    return frame, e

# ╔══════════════════════════════════════════════════════════════╗
# ║                     PAGE DE CONNEXION                       ║
# ╚══════════════════════════════════════════════════════════════╝
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Priscilia Restaurant - Connexion")
        self.geometry("900x580")
        self.resizable(False, False)
        self.configure(bg=C_DARK)
        self._center()
        self._build()

    def _center(self):
        self.update_idletasks()
        w, h = 900, 580
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        # LEFT panel – branding
        left = tk.Frame(self, bg=C_DARK2, width=440)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Frame(left, bg=C_DARK2).pack(expand=True)

        logo_frame = tk.Frame(left, bg=C_GOLD, width=90, height=90)
        logo_frame.pack()
        logo_frame.pack_propagate(False)
        tk.Label(logo_frame, text="🍽", font=("Helvetica", 38),
                 bg=C_GOLD, fg=C_WHITE).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(left, text="PRISCILIA", font=("Helvetica", 28, "bold"),
                 bg=C_DARK2, fg=C_GOLD).pack(pady=(14,0))
        tk.Label(left, text="RESTAURANT", font=("Helvetica", 14, "bold"),
                 bg=C_DARK2, fg=C_WHITE).pack()
        tk.Label(left, text="Système de Gestion Intégré",
                 font=("Helvetica", 10, "italic"), bg=C_DARK2, fg=C_GRAY).pack(pady=(6,0))

        tk.Frame(left, bg=C_GOLD, height=2).pack(fill="x", padx=40, pady=20)

        features = ["✦  Gestion des Commandes", "✦  Plan de Salle Interactif",
                    "✦  Facturation & PDF", "✦  Réservations", "✦  Statistiques & Rapports"]
        for f in features:
            tk.Label(left, text=f, font=("Helvetica", 10),
                     bg=C_DARK2, fg=C_LIGHT).pack(anchor="w", padx=50, pady=2)

        tk.Frame(left, bg=C_DARK2).pack(expand=True)
        tk.Label(left, text="v1.0 © 2025 Priscilia Restaurant",
                 font=FONT_SMALL, bg=C_DARK2, fg=C_GRAY).pack(pady=10)

        # RIGHT panel – login form
        right = tk.Frame(self, bg=C_WHITE)
        right.pack(side="right", fill="both", expand=True)

        tk.Frame(right, bg=C_WHITE).pack(expand=True)

        container = tk.Frame(right, bg=C_WHITE)
        container.pack(padx=50, pady=20, fill="x")

        tk.Label(container, text="Bienvenue 👋", font=("Helvetica", 22, "bold"),
                 bg=C_WHITE, fg=C_DARK).pack(anchor="w")
        tk.Label(container, text="Connectez-vous à votre espace",
                 font=("Helvetica", 11), bg=C_WHITE, fg=C_GRAY).pack(anchor="w", pady=(2,20))

        tk.Label(container, text="Identifiant", font=FONT_BOLD,
                 bg=C_WHITE, fg=C_DARK).pack(anchor="w")
        self.user_frame, self.user_entry = entry_field(container, placeholder="Entrez votre identifiant")
        self.user_frame.pack(fill="x", pady=(4,12))

        tk.Label(container, text="Mot de passe", font=FONT_BOLD,
                 bg=C_WHITE, fg=C_DARK).pack(anchor="w")
        self.pass_frame, self.pass_entry = entry_field(container, placeholder="••••••••", show="")
        self.pass_frame.pack(fill="x", pady=(4,6))

        # Show/hide password
        self.show_pass = tk.BooleanVar()
        def toggle_pass():
            if self.show_pass.get():
                self.pass_entry.config(show="")
            else:
                self.pass_entry.config(show="•")
        tk.Checkbutton(container, text="Afficher le mot de passe", variable=self.show_pass,
                       command=toggle_pass, bg=C_WHITE, fg=C_GRAY,
                       font=FONT_SMALL, activebackground=C_WHITE, cursor="hand2").pack(anchor="w", pady=(0,16))

        btn = styled_button(container, "  SE CONNECTER  ", command=self._login,
                            bg=C_GOLD, pady=12)
        btn.pack(fill="x")

        self.msg_label = tk.Label(container, text="", font=FONT_SMALL,
                                  bg=C_WHITE, fg=C_RED)
        self.msg_label.pack(pady=(8,0))

        tk.Frame(right, bg=C_WHITE).pack(expand=True)

        # Demo credentials hint
        hint = tk.Frame(right, bg=C_BG)
        hint.pack(fill="x", side="bottom")
        tk.Label(hint, text="Demo: admin / admin123   |   serveur1 / 1234   |   caissier / 1234",
                 font=FONT_SMALL, bg=C_BG, fg=C_GRAY, pady=8).pack()

        # Bind Enter key
        self.bind("<Return>", lambda e: self._login())

    def _login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not username or username == "Entrez votre identifiant":
            self.msg_label.config(text="⚠  Veuillez entrer votre identifiant")
            return
        if not password or password == "••••••••":
            self.msg_label.config(text="⚠  Veuillez entrer votre mot de passe")
            return
        user = authenticate(username, password)
        if user:
            self.destroy()
            app = MainApp(user)
            app.mainloop()
        else:
            self.msg_label.config(text="✗  Identifiant ou mot de passe incorrect")
            self.pass_entry.delete(0, tk.END)


# ╔══════════════════════════════════════════════════════════════╗
# ║                    APPLICATION PRINCIPALE                   ║
# ╚══════════════════════════════════════════════════════════════╝
class MainApp(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.title(f"Priscilia Restaurant — {user['full_name']} ({user['role'].title()})")
        self.state("zoomed")
        self.configure(bg=C_BG)
        self.current_frame = None
        self._build_layout()
        self._show_tab("dashboard")

    def _build_layout(self):
        # ── TOP BAR ──
        topbar = tk.Frame(self, bg=C_DARK, height=56)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="🍽  PRISCILIA RESTAURANT",
                 font=("Helvetica", 15, "bold"), bg=C_DARK, fg=C_GOLD).pack(side="left", padx=20)

        from datetime import datetime
        self.clock_label = tk.Label(topbar, text="", font=("Helvetica", 11),
                                    bg=C_DARK, fg=C_LIGHT)
        self.clock_label.pack(side="right", padx=20)
        self._tick()

        tk.Label(topbar, text=f"👤  {self.user['full_name']}",
                 font=FONT_BOLD, bg=C_DARK, fg=C_GOLD).pack(side="right", padx=10)
        tk.Label(topbar, text=f"[{self.user['role'].upper()}]",
                 font=FONT_SMALL, bg=C_DARK, fg=C_GRAY).pack(side="right", padx=(10,0))

        styled_button(topbar, "⏻ Déconnexion", command=self._logout,
                      bg="#C0392B", pady=6).pack(side="right", padx=10)

        # ── SIDEBAR ──
        sidebar = tk.Frame(self, bg=C_DARK2, width=210)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, bg=C_GOLD, height=2).pack(fill="x")

        self.nav_buttons = {}
        nav_items = [
            ("dashboard",    "📊  Tableau de Bord", "admin caissier staff"),
            ("orders",       "🧾  Commandes",        "admin caissier staff"),
            ("tables",       "🪑  Plan de Salle",    "admin caissier staff"),
            ("menu",         "🍴  Menu & Plats",     "admin"),
            ("reservations", "📅  Réservations",     "admin caissier staff"),
            ("invoices",     "💰  Facturation",       "admin caissier"),
            ("kitchen",      "👨‍🍳  Cuisine",          "admin staff"),
            ("expenses",     "📋  Dépenses",          "admin"),
            ("staff",        "👥  Personnel",         "admin"),
            ("settings",     "⚙️  Paramètres",        "admin"),
        ]

        for key, label, roles in nav_items:
            if self.user['role'] not in roles and self.user['role'] != 'admin':
                continue
            btn = tk.Button(sidebar, text=label, font=("Helvetica", 10, "bold"),
                            bg=C_DARK2, fg=C_LIGHT, relief="flat", bd=0,
                            padx=16, pady=12, anchor="w", cursor="hand2",
                            activebackground=C_PANEL, activeforeground=C_GOLD,
                            command=lambda k=key: self._show_tab(k))
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        tk.Frame(sidebar, bg=C_DARK2).pack(expand=True)
        tk.Label(sidebar, text="Priscilia Restaurant\nv1.0 © 2025",
                 font=("Helvetica", 8), bg=C_DARK2, fg=C_GRAY, justify="center").pack(pady=10)

        # ── CONTENT AREA ──
        self.content = tk.Frame(self, bg=C_BG)
        self.content.pack(fill="both", expand=True, side="right")

    def _tick(self):
        from datetime import datetime
        now = datetime.now().strftime("%A %d/%m/%Y   %H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self._tick)

    def _show_tab(self, key):
        # Highlight active nav button
        for k, b in self.nav_buttons.items():
            if k == key:
                b.config(bg=C_PANEL, fg=C_GOLD)
            else:
                b.config(bg=C_DARK2, fg=C_LIGHT)

        # Destroy previous content
        for w in self.content.winfo_children():
            w.destroy()

        # Load module
        if key == "dashboard":
            from modules.tab_dashboard import DashboardTab
            DashboardTab(self.content, self.user).pack(fill="both", expand=True)
        elif key == "orders":
            from modules.tab_orders import OrdersTab
            OrdersTab(self.content, self.user).pack(fill="both", expand=True)
        elif key == "tables":
            from modules.tab_tables import TablesTab
            TablesTab(self.content, self.user, self).pack(fill="both", expand=True)
        elif key == "menu":
            from modules.tab_menu import MenuTab
            MenuTab(self.content, self.user).pack(fill="both", expand=True)
        elif key == "reservations":
            from modules.tab_reservations import ReservationsTab
            ReservationsTab(self.content, self.user).pack(fill="both", expand=True)
        elif key == "invoices":
            from modules.tab_invoices import InvoicesTab
            InvoicesTab(self.content, self.user).pack(fill="both", expand=True)
        elif key == "kitchen":
            from modules.tab_kitchen import KitchenTab
            KitchenTab(self.content, self.user).pack(fill="both", expand=True)
        elif key == "expenses":
            from modules.tab_expenses import ExpensesTab
            ExpensesTab(self.content, self.user).pack(fill="both", expand=True)
        elif key == "staff":
            from modules.tab_staff import StaffTab
            StaffTab(self.content, self.user).pack(fill="both", expand=True)
        elif key == "settings":
            from modules.tab_settings import SettingsTab
            SettingsTab(self.content, self.user).pack(fill="both", expand=True)

    def _logout(self):
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            self.destroy()
            login = LoginWindow()
            login.mainloop()


if __name__ == "__main__":
    init_db()
    app = LoginWindow()
    app.mainloop()
