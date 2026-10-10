from app.database import SessionLocal
from app.models.user import User

def voir_users():
    db = SessionLocal()
    utilisateurs = db.query(User).all()
    if not utilisateurs:
        print("\nAucun utilisateur n'est inscrit dans la base de données pour le moment.\n")
    else:
        print(f"\n=== {len(utilisateurs)} Utilisateur(s) dans la base de données ===")
        for u in utilisateurs:
            print(f"- ID: {u.id} | {u.prenom} {u.nom} | Email: {u.email} | Téléphone: {u.telephone}")
        print("=========================================================\n")
    db.close()

if __name__ == "__main__":
    voir_users()

