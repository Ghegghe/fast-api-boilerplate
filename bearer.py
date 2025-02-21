from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session, select
from database.enum import UserRoleEnum
from database.models import User
from dependencies import get_session, post


SECRET_KEY = "371ea583e239d0afd35f2057db4dd7f0b07f3b1cb773d3df965f11560115699f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(tags=["login"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class RegisterUser(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    username: str
    email: str
    role: UserRoleEnum


def authenticate_user(session: Session, username: str, password: str) -> User:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )
    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="uncorrect password"
        )
    return user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(session: Session, token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = decoded_token.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user


def administrator_rights(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> bool:
    user = get_user_from_token(session, token)
    if user.role != UserRoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="insufficient permissions, this action requires the 'admin' role",
        )
    return True


def user_rights(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> bool:
    user = get_user_from_token(session, token)
    if user.role != UserRoleEnum.user and user.role != UserRoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="insufficient permissions, this action requires the 'user' or the 'admin' role",
        )
    return True


@router.post("/register", tags=["login"], response_model=UserResponse)
def register(
    user: RegisterUser,
    session: Annotated[Session, Depends(get_session)],
):
    new_user = User(
        username=user.username,
        password_hash=pwd_context.hash(user.password),
        email=user.email,
        role=UserRoleEnum.user,
    )
    return post(User, new_user, session)


@router.post("/token", tags=["login"])
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
