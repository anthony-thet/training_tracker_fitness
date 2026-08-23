from datetime import timedelta

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token
from app.dependencies.auth_dependencies import get_current_user
from app.models import User
from app.schemas.auth_schema import Token
from app.schemas.user_schema import UserRead, UserCreate
from app.database import get_db
from app.services.auth_service import register_user, authenticate_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user_route(
        user_in: UserCreate,
        db: Session = Depends(get_db)
):
    return register_user(user_in, db)


@router.post("/login", response_model=Token)
def login_user_route(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserRead)
def get_current_user_route(
        current_user: User = Depends(get_current_user),
):
    return current_user