import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from modules.database import get_conn

C_GOLD="#C8860A";C_DARK="#1A1A2E";C_WHITE="#FFFFFF";C_LIGHT="#F5F5F5"
C_GRAY="#AAAAAA";C_GREEN="#27AE60";C_RED="#E74C3C";C_ORANGE="#F39C12"
C_BLUE="#2980B9";C_BG="#F0F2F5"
FONT_TITLE=("Helvetica",20,"bold");FONT_HEADER=("Helvetica",13,"bold")
FONT_BOLD=("Helvetica",11,"bold");FONT_NORM=("Helvetica",10);FONT_SMALL=("Helvetica",9)
def btn(parent,text,cmd,bg=C_GOLD,fg=C_WHITE,font=FONT_BOLD,px=12,py=7):
    return tk.Button(parent,text=text,command=cmd,bg=bg,fg=fg,font=font,
                     relief="flat",bd=0,padx=px,pady=py,cursor="hand2")

STATUS_COLORS={"confirmee":C_GREEN,"annulee":C_RED,"en_attente":C_ORANGE,"arrivee":C_BLUE}
STATUS_LABELS={"confirmee":"Confirmée","annulee":"Annulée","en_attente":"En attente","arrivee":"Arrivée"}

class ReservationsTab(tk.Frame):
    def __init__(self, parent, user):
        super().__init__(parent, bg=C_BG)
        self.user = user
        self._build()
        self._load()

    def _build(self):
        hdr = tk.Frame(self, bg=C_BG)
        hdr.pack(fill="x", padx=24, pady=(18,8))
        tk.Label(hdr, text="📅  Réservations", font=FONT_TITLE, bg=C_BG, fg=C_DARK).pack(side="left")
        btn(hdr,"+ Nouvelle Réservation",self._add,bg=C_GREEN).pack(side="right",padx=4)
        btn(hdr,"↻ Actualiser",self._load,bg=C_BLUE).pack(side="right",padx=4)

        # Filter bar
        fbar = tk.Frame(self, bg=C_WHITE, pady=8)
        fbar.pack(fill="x", padx=24, pady=(0,8))
        tk.Label(fbar, text="Date:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=10).pack(side="left")
        self.date_entry = tk.Entry(fbar, font=FONT_NORM, width=12, relief="solid", bd=1)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.pack(side="left", padx=4)
        btn(fbar,"Aujourd'hui",lambda:self._set_today(),bg=C_GOLD,px=8,py=5).pack(side="left",padx=4)
        btn(fbar,"Tout Voir",lambda:self._clear_date(),bg="#95A5A6",px=8,py=5).pack(side="left",padx=4)
        btn(fbar,"🔍 Filtrer",self._load,bg=C_BLUE,px=8,py=5).pack(side="left",padx=6)

        tk.Label(fbar, text="Statut:", font=FONT_BOLD, bg=C_WHITE, fg=C_DARK, padx=10).pack(side="left")
        self.status_var = tk.StringVar(value="tous")
        for lbl, val in [("Tous","tous"),("Confirmées","confirmee"),("En attente","en_attente"),("Annulées","annulee")]:
            tk.Radiobutton(fbar, text=lbl, variable=self.status_var, value=val,
                           font=FONT_NORM, bg=C_WHITE, cursor="hand2",
                           command=self._load).pack(side="left", padx=6)

        # Table
        table_frame = tk.Frame(self, bg=C_WHITE, highlightthickness=1, highlightbackground="#E0E0E0")
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0,8))

        cols = ("ID","Client","Téléphone","Date","Heure","Couverts","Table","Statut","Notes")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)
        widths = [50,150,110,100,70,70,70,100,180]
        for col,w in zip(cols,widths):
            self.tree.heading(col,text=col)
            self.tree.column(col,width=w,anchor="center")
        self.tree.tag_configure("confirmee", foreground=C_GREEN)
        self.tree.tag_configure("annulee", foreground=C_RED)
        self.tree.tag_configure("en_attente", foreground=C_ORANGE)
        self.tree.tag_configure("arrivee", foreground=C_BLUE)
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)

        # Action bar
        act = tk.Frame(self, bg=C_BG)
        act.pack(fill="x", padx=24, pady=(0,10))
        btn(act,"✏ Modifier",self._edit,bg=C_BLUE).pack(side="left",padx=4)
        btn(act,"✔ Marquer Arrivée",lambda:self._set_status("arrivee"),bg=C_GREEN).pack(side="left",padx=4)
        btn(act,"✘ Annuler",lambda:self._set_status("annulee"),bg=C_RED).pack(side="left",padx=4)
        btn(act,"🗑 Supprimer",self._delete,bg="#7F8C8D").pack(side="left",padx=4)

    def _set_today(self):
        self.date_entry.delete(0,'end')
        self.date_entry.insert(0, date.today().isoformat())
        self._load()

    def _clear_date(self):
        self.date_entry.delete(0,'end')
        self._load()

    def _load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn(); c = conn.cursor()
        date_filter = self.date_entry.get().strip()
        status_filter = self.status_var.get()
        query = """SELECT r.id, r.client_name, r.phone, r.date, r.time, r.guests,
                   t.number, r.status, r.notes
                   FROM reservations r LEFT JOIN tables t ON r.table_id=t.id
                   WHERE 1=1"""
        params = []
        if date_filter:
            query += " AND r.date=?"; params.append(date_filter)
        if status_filter != "tous":
            query += " AND r.status=?"; params.append(status_filter)
        query += " ORDER BY r.date, r.time"
        c.execute(query, params)
        for row in c.fetchall():
            rid,client,phone,rdate,rtime,guests,tnum,status,notes = row
            self.tree.insert("","end",iid=str(rid),
                values=(rid,client,phone or"-",rdate,rtime,f"{guests} pers.",
                        f"T{tnum}" if tnum else"-",STATUS_LABELS.get(status,status),notes or""),
                tags=(status,))
        conn.close()

    def _get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sélection","Sélectionnez une réservation."); return None
        return int(sel[0])

    def _add(self): ReservationDialog(self, None, self._load)
    def _edit(self):
        rid = self._get_selected()
        if rid: ReservationDialog(self, rid, self._load)

    def _set_status(self, status):
        rid = self._get_selected()
        if not rid: return
        conn = get_conn(); c = conn.cursor()
        c.execute("UPDATE reservations SET status=? WHERE id=?", (status,rid))
        conn.commit(); conn.close()
        self._load()

    def _delete(self):
        rid = self._get_selected()
        if not rid: return
        if messagebox.askyesno("Supprimer","Supprimer cette réservation ?"):
            conn = get_conn(); c = conn.cursor()
            c.execute("DELETE FROM reservations WHERE id=?", (rid,))
            conn.commit(); conn.close()
            self._load()


class ReservationDialog(tk.Toplevel):
    def __init__(self, parent, resa_id, callback):
        super().__init__(parent)
        self.resa_id = resa_id
        self.callback = callback
        self.title("Nouvelle Réservation" if not resa_id else "Modifier Réservation")
        self.geometry("500x560")
        self.resizable(False, False)
        self.configure(bg=C_BG)
        x=(self.winfo_screenwidth()-500)//2; y=(self.winfo_screenheight()-560)//2
        self.geometry(f"500x560+{x}+{y}")
        self._build()
        if resa_id: self._load()
        self.grab_set()

    def _build(self):
        tk.Frame(self, bg=C_GOLD, height=5).pack(fill="x")
        tk.Label(self, text="📅  Réservation", font=FONT_HEADER, bg=C_BG, fg=C_DARK, pady=12).pack()
        form = tk.Frame(self, bg=C_WHITE, padx=28, pady=16)
        form.pack(fill="x", padx=24)

        def lbl(text): return tk.Label(form, text=text, font=FONT_BOLD, bg=C_WHITE, fg=C_DARK)
        def ent(width=32): e = tk.Entry(form, font=FONT_NORM, relief="solid", bd=1, width=width); return e

        lbl("Nom du client *").pack(anchor="w", pady=(4,2))
        self.client_e = ent(); self.client_e.pack(fill="x")

        row = tk.Frame(form, bg=C_WHITE); row.pack(fill="x", pady=(8,0))
        c1 = tk.Frame(row, bg=C_WHITE); c1.pack(side="left", fill="x", expand=True, padx=(0,8))
        c2 = tk.Frame(row, bg=C_WHITE); c2.pack(side="right", fill="x", expand=True)
        lbl2 = lambda p,t: tk.Label(p, text=t, font=FONT_BOLD, bg=C_WHITE, fg=C_DARK)
        lbl2(c1,"Téléphone").pack(anchor="w", pady=(0,2))
        self.phone_e = tk.Entry(c1, font=FONT_NORM, relief="solid", bd=1); self.phone_e.pack(fill="x")
        lbl2(c2,"Email").pack(anchor="w", pady=(0,2))
        self.email_e = tk.Entry(c2, font=FONT_NORM, relief="solid", bd=1); self.email_e.pack(fill="x")

        row2 = tk.Frame(form, bg=C_WHITE); row2.pack(fill="x", pady=(8,0))
        c3 = tk.Frame(row2, bg=C_WHITE); c3.pack(side="left", fill="x", expand=True, padx=(0,8))
        c4 = tk.Frame(row2, bg=C_WHITE); c4.pack(side="left", fill="x", expand=True, padx=(0,8))
        c5 = tk.Frame(row2, bg=C_WHITE); c5.pack(side="right", fill="x", expand=True)
        lbl2(c3,"Date * (YYYY-MM-DD)").pack(anchor="w", pady=(0,2))
        self.date_e = tk.Entry(c3, font=FONT_NORM, relief="solid", bd=1)
        self.date_e.insert(0, date.today().isoformat()); self.date_e.pack(fill="x")
        lbl2(c4,"Heure * (HH:MM)").pack(anchor="w", pady=(0,2))
        self.time_e = tk.Entry(c4, font=FONT_NORM, relief="solid", bd=1)
        self.time_e.insert(0, "19:00"); self.time_e.pack(fill="x")
        lbl2(c5,"Couverts").pack(anchor="w", pady=(0,2))
        self.guests_e = tk.Entry(c5, font=FONT_NORM, relief="solid", bd=1, width=6)
        self.guests_e.insert(0,"2"); self.guests_e.pack(fill="x")

        lbl("Table (N°)").pack(anchor="w", pady=(10,2))
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT number FROM tables ORDER BY number"); conn.close()
        self.table_var = tk.StringVar()

        lbl("Table N°:").pack(anchor="w", pady=(10,2))
        self.table_e = tk.Entry(form, font=FONT_NORM, relief="solid", bd=1, width=8)
        self.table_e.pack(anchor="w")

        lbl("Statut").pack(anchor="w", pady=(10,2))
        self.status_var = tk.StringVar(value="confirmee")
        sf = tk.Frame(form, bg=C_WHITE); sf.pack(anchor="w")
        for lbl_t, val in [("Confirmée","confirmee"),("En attente","en_attente"),("Annulée","annulee")]:
            tk.Radiobutton(sf, text=lbl_t, variable=self.status_var, value=val,
                           font=FONT_NORM, bg=C_WHITE, cursor="hand2").pack(side="left", padx=6)

        lbl("Notes").pack(anchor="w", pady=(10,2))
        self.notes_e = tk.Text(form, font=FONT_NORM, height=3, relief="solid", bd=1)
        self.notes_e.pack(fill="x")

        btn_frame = tk.Frame(self, bg=C_BG, pady=14)
        btn_frame.pack(fill="x", padx=24)
        btn(btn_frame,"💾 Enregistrer",self._save,bg=C_GREEN).pack(side="left",padx=4)
        btn(btn_frame,"✖ Annuler",self.destroy,bg=C_RED).pack(side="left",padx=4)

    def _load(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT r.*, t.number FROM reservations r LEFT JOIN tables t ON r.table_id=t.id WHERE r.id=?", (self.resa_id,))
        r = c.fetchone(); conn.close()
        if not r: return
        self.client_e.insert(0, r['client_name'])
        if r['phone']: self.phone_e.insert(0, r['phone'])
        if r['email']: self.email_e.insert(0, r['email'])
        self.date_e.delete(0,'end'); self.date_e.insert(0, r['date'])
        self.time_e.delete(0,'end'); self.time_e.insert(0, r['time'])
        self.guests_e.delete(0,'end'); self.guests_e.insert(0, str(r['guests']))
        if r['number']: self.table_e.insert(0, str(r['number']))
        self.status_var.set(r['status'])
        if r['notes']: self.notes_e.insert("1.0", r['notes'])

    def _save(self):
        client = self.client_e.get().strip()
        if not client:
            messagebox.showerror("Erreur","Nom client obligatoire."); return
        rdate = self.date_e.get().strip()
        rtime = self.time_e.get().strip()
        if not rdate or not rtime:
            messagebox.showerror("Erreur","Date et heure obligatoires."); return
        try: guests = int(self.guests_e.get())
        except: guests = 2
        table_num = self.table_e.get().strip()
        table_id = None
        if table_num:
            conn = get_conn(); c = conn.cursor()
            c.execute("SELECT id FROM tables WHERE number=?", (table_num,))
            t = c.fetchone(); conn.close()
            if t: table_id = t[0]

        conn = get_conn(); c = conn.cursor()
        notes = self.notes_e.get("1.0","end").strip()
        status = self.status_var.get()
        if self.resa_id:
            c.execute("UPDATE reservations SET client_name=?,phone=?,email=?,date=?,time=?,guests=?,table_id=?,status=?,notes=? WHERE id=?",
                      (client,self.phone_e.get(),self.email_e.get(),rdate,rtime,guests,table_id,status,notes,self.resa_id))
        else:
            c.execute("INSERT INTO reservations (client_name,phone,email,date,time,guests,table_id,status,notes) VALUES (?,?,?,?,?,?,?,?,?)",
                      (client,self.phone_e.get(),self.email_e.get(),rdate,rtime,guests,table_id,status,notes))
            if table_id and status == "confirmee":
                c.execute("UPDATE tables SET status='reservee' WHERE id=?", (table_id,))
        conn.commit(); conn.close()
        self.callback(); self.destroy()
