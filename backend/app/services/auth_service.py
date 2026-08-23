from app.core.security import get_password_hash, verify_password
from app.database import get_db
from app.models import User
from app.schemas.user_schema import UserCreate
from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


def register_user(
        user_in: UserCreate,
        db: Session,
) -> User:
    user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or username already exists.",
        )

    return user


def get_user_by_email(
        db: Session,
        email: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_username(
        db: Session,
        username: str,
) -> User | None:
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def authenticate_user(
        db: Session,
        username_or_email: str,
        password: str,
) -> User | None:

    user = get_user_by_email(db, username_or_email)

    if user is None:
        user = get_user_by_username(db, username_or_email)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user