import mysql.connector
from mysql.connector import Error

# ==============================
# CONNEXION A LA BASE DE DONNEES
# ==============================
def connexion_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="tontine_db"
        )
        return conn
    except Error as e:
        print(" Erreur de connexion :", e)
        return None


# ==============================
# GESTION DES MEMBRES
# ==============================
def ajouter_membre(nom, prenom, telephone):
    conn = connexion_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO membre (nom, prenom, telephone, date_inscription)
        VALUES (%s, %s, %s, CURDATE())
    """
    cursor.execute(sql, (nom, prenom, telephone))
    conn.commit()
    print("Membre ajouté")
    conn.close()


def afficher_membres():
    conn = connexion_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM membre")
    for m in cursor.fetchall():
        print(m)
    conn.close()


# ==============================
# GESTION DES TONTINES
# ==============================
def ajouter_tontine(nom, type_tontine, montant_part, nombre_tours):
    conn = connexion_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO tontine (nom, type_tontine, montant_part, nombre_tours)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (nom, type_tontine, montant_part, nombre_tours))
    conn.commit()
    print(" Tontine ajoutée")
    conn.close()


def afficher_tontines():
    conn = connexion_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tontine")
    for t in cursor.fetchall():
        print(t)
    conn.close()


# ==============================
# ADHESION
# ==============================
def ajouter_adhesion(id_membre, id_tontine, nb_parts):
    conn = connexion_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO adhesion (id_membre, id_tontine, nb_parts)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (id_membre, id_tontine, nb_parts))
    conn.commit()
    print(" Adhésion enregistrée")
    conn.close()


# ==============================
# SEANCES
# ==============================
def ajouter_seance(id_tontine, date_seance):
    conn = connexion_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO seance (id_tontine, date_seance)
        VALUES (%s, %s)
    """
    cursor.execute(sql, (id_tontine, date_seance))
    conn.commit()
    print(" Séance créée")
    conn.close()


# ==============================
# COTISATIONS
# ==============================
def ajouter_cotisation(id_seance, id_membre, montant):
    conn = connexion_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO cotisation (id_seance, id_membre, montant)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (id_seance, id_membre, montant))
    conn.commit()
    print(" Cotisation enregistrée")
    conn.close()


# ==============================
# CREDITS
# ==============================
def ajouter_credit(id_membre, id_tontine, montant):
    conn = connexion_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO credit (id_membre, id_tontine, montant)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (id_membre, id_tontine, montant))
    conn.commit()
    print(" Crédit accordé")
    conn.close()


# ==============================
# BENEFICES
# ==============================
def ajouter_benefice(id_membre, id_tontine, montant):
    conn = connexion_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO benefice (id_membre, id_tontine, montant)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (id_membre, id_tontine, montant))
    conn.commit()
    print(" Bénéfice enregistré")
    conn.close()


# ==============================
# PENALITES
# ==============================
def ajouter_penalite(id_membre, id_seance, montant, motif):
    conn = connexion_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO penalite (id_membre, id_seance, montant, motif)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (id_membre, id_seance, montant, motif))
    conn.commit()
    print(" Pénalité appliquée")
    conn.close()


# ==============================
# MENU PRINCIPAL
# ==============================
def menu():
    while True:
        print("\n========= MENU TONTINE =========")
        print("1. Ajouter un membre")
        print("2. Afficher les membres")
        print("3. Ajouter une tontine")
        print("4. Afficher les tontines")
        print("5. Adhérer à une tontine")
        print("6. Créer une séance")
        print("7. Enregistrer une cotisation")
        print("8. Accorder un crédit")
        print("9. Enregistrer un bénéfice")
        print("10. Appliquer une pénalité")
        print("0. Quitter")

        choix = input("Votre choix : ")

        if choix == "1":
            ajouter_membre(
                input("Nom : "),
                input("Prénom : "),
                input("Téléphone : ")
            )

        elif choix == "2":
            afficher_membres()

        elif choix == "3":
            ajouter_tontine(
                input("Nom : "),
                input("Type (presence/optionnelle) : "),
                int(input("Montant part : ")),
                int(input("Nombre de tours : "))
            )

        elif choix == "4":
            afficher_tontines()

        elif choix == "5":
            ajouter_adhesion(
                int(input("ID membre : ")),
                int(input("ID tontine : ")),
                int(input("Nombre de parts : "))
            )

        elif choix == "6":
            ajouter_seance(
                int(input("ID tontine : ")),
                input("Date (YYYY-MM-DD) : ")
            )

        elif choix == "7":
            ajouter_cotisation(
                int(input("ID séance : ")),
                int(input("ID membre : ")),
                int(input("Montant : "))
            )

        elif choix == "8":
            ajouter_credit(
                int(input("ID membre : ")),
                int(input("ID tontine : ")),
                int(input("Montant : "))
            )

        elif choix == "9":
            ajouter_benefice(
                int(input("ID membre : ")),
                int(input("ID tontine : ")),
                int(input("Montant : "))
            )

        elif choix == "10":
            ajouter_penalite(
                int(input("ID membre : ")),
                int(input("ID séance : ")),
                int(input("Montant : ")),
                input("Motif : ")
            )

        elif choix == "0":
            print(" Fin du programme")
            break

        else:
            print(" Choix invalide")


# ==============================
# PROGRAMME PRINCIPAL
# ==============================
if __name__ == "__main__":
    menu()

