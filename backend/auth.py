"""
Authentication utilities voor password hashing en JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

import db_models
from database import get_db

load_dotenv()

# Password hashing context met bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme voor token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
REFRESH_TOKEN_REMEMBER_ME_DAYS = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify een plain text password tegen een hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash een plain text password met bcrypt
    """
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)


def validate_password_strength(password: str, username: str = "") -> tuple[bool, str]:
    """
    Valideer password sterkte volgens OWASP guidelines
    
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    # Minimale en maximale lengte
    if len(password) < 12:
        return False, "Password moet minimaal 12 karakters lang zijn"
    
    if len(password) > 128:
        return False, "Password mag maximaal 128 karakters lang zijn"
    
    # Check voor hoofdletter
    if not any(c.isupper() for c in password):
        return False, "Password moet minimaal 1 hoofdletter bevatten"
    
    # Check voor kleine letter
    if not any(c.islower() for c in password):
        return False, "Password moet minimaal 1 kleine letter bevatten"
    
    # Check voor cijfer
    if not any(c.isdigit() for c in password):
        return False, "Password moet minimaal 1 cijfer bevatten"
    
    # Check voor speciaal karakter
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        return False, f"Password moet minimaal 1 speciaal karakter bevatten ({special_chars})"
    
    # Check voor username in password
    if username and username.lower() in password.lower():
        return False, "Password mag geen deel van gebruikersnaam bevatten"
    
    # Check voor sequenties
    sequences = ["123456", "abcdef", "qwerty", "password", "admin"]
    for seq in sequences:
        if seq in password.lower():
            return False, f"Password mag geen veelvoorkomende sequenties bevatten"
    
    # Check voor herhalingen
    for i in range(len(password) - 5):
        if len(set(password[i:i+6])) == 1:
            return False, "Password mag geen herhaalde karakters bevatten"
    
    return True, ""


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creëer een JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, remember_me: bool = False) -> str:
    """
    Creëer een JWT refresh token
    """
    to_encode = data.copy()
    if remember_me:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_REMEMBER_ME_DAYS)
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decodeer en valideer een JWT token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token kon niet gevalideerd worden",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> db_models.User:
    """
    Haal de huidige ingelogde gebruiker op basis van JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credentials konden niet gevalideerd worden",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is gedeactiveerd"
        )
    
    return user


async def get_current_active_user(
    current_user: db_models.User = Depends(get_current_user)
) -> db_models.User:
    """
    Verify dat de gebruiker actief is
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactieve gebruiker"
        )
    return current_user


def require_permission(permission_name: str):
    """
    Decorator om te checken of gebruiker een specifieke permission heeft
    """
    async def permission_checker(
        current_user: db_models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> db_models.User:
        # Haal de rol en permissions op
        role = db.query(db_models.Role).filter(
            db_models.Role.id == current_user.role_id
        ).first()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Gebruiker heeft geen geldige rol"
            )
        
        # Check of de permission bestaat in de rol
        has_permission = any(
            perm.name == permission_name for perm in role.permissions
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Je hebt geen toegang tot deze actie (vereist: {permission_name})"
            )
        
        return current_user
    
    return permission_checker


def require_role(role_name: str):
    """
    Decorator om te checken of gebruiker een specifieke rol heeft
    """
    async def role_checker(
        current_user: db_models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> db_models.User:
        role = db.query(db_models.Role).filter(
            db_models.Role.id == current_user.role_id
        ).first()
        
        if not role or role.name != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Deze actie vereist de '{role_name}' rol"
            )
        
        return current_user
    
    return role_checker


def authenticate_user(db: Session, username: str, password: str) -> Optional[db_models.User]:
    """
    Authenticeer een gebruiker met username en password
    """
    user = db.query(db_models.User).filter(
        db_models.User.username == username
    ).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user
