from sqlalchemy.orm import Session
from .model import User
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


# =========================
# CREATE USER
# =========================

def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: str = "student"
):
    hashed_password = password_hash.hash(password)

    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================
# GET USER BY EMAIL
# =========================

def get_user_by_email(
    db: Session,
    email: str
):
    return db.query(User).filter(
        User.email == email
    ).first()


# =========================
# GET USER BY ID
# =========================

def get_user_by_id(
    db: Session,
    user_id: int
):
    return db.query(User).filter(
        User.id == user_id
    ).first()


# =========================
# GET ALL USERS
# =========================

def get_all_users(db: Session):
    return db.query(User).order_by(
        User.id.asc()
    ).all()


# =========================
# DELETE USER
# =========================

def delete_user(
    db: Session,
    user_id: int
):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    db.delete(user)
    db.commit()

    return user


# =========================
# UPDATE ROLE
# =========================

def update_user_role(
    db: Session,
    user_id: int,
    role: str
):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    user.role = role

    db.commit()
    db.refresh(user)

    return user


# =========================
# PASSWORD
# =========================

def verify_password(
    password: str,
    hashed_password: str
):
    return password_hash.verify(
        password,
        hashed_password
    )