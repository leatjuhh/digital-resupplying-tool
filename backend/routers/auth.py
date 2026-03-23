"""
Authentication router - Login, logout, refresh endpoints
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

import db_models
from database import get_db
from auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    decode_token
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Pydantic models voor request/response
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role_name: str
    role_display_name: str
    permissions: list[str]
    is_active: bool
    last_login: Optional[datetime]
    store_code: Optional[str] = None
    store_name: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember_me: bool = False,
    db: Session = Depends(get_db)
):
    """
    Login endpoint - Authenticeer gebruiker met username en password
    
    Returns JWT access en refresh tokens
    """
    # Authenticeer gebruiker
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Onjuiste gebruikersnaam of wachtwoord",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is gedeactiveerd"
        )
    
    # Haal rol en permissions op
    role = db.query(db_models.Role).filter(
        db_models.Role.id == user.role_id
    ).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gebruiker heeft geen geldige rol"
        )
    
    permissions = [perm.name for perm in role.permissions]
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Creëer tokens (sub moet een string zijn volgens JWT spec)
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": role.name,
        "permissions": permissions
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data={"sub": str(user.id)}, remember_me=remember_me)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh endpoint - Vernieuw access token met refresh token
    """
    try:
        payload = decode_token(token_data.refresh_token)
        
        # Check of het een refresh token is
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ongeldig refresh token"
            )
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ongeldig refresh token"
            )
        
        # Haal gebruiker op
        user = db.query(db_models.User).filter(
            db_models.User.id == user_id
        ).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Gebruiker niet gevonden of gedeactiveerd"
            )
        
        # Haal rol en permissions op
        role = db.query(db_models.Role).filter(
            db_models.Role.id == user.role_id
        ).first()
        
        permissions = [perm.name for perm in role.permissions]
        
        # Creëer nieuwe tokens (sub moet een string zijn volgens JWT spec)
        token_payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": role.name,
            "permissions": permissions
        }
        
        access_token = create_access_token(data=token_payload)
        # Hergebruik de refresh token
        
        return {
            "access_token": access_token,
            "refresh_token": token_data.refresh_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token kon niet vernieuwd worden"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: db_models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user endpoint - Haal info op van ingelogde gebruiker
    """
    # Haal rol en permissions op
    role = db.query(db_models.Role).filter(
        db_models.Role.id == current_user.role_id
    ).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gebruiker heeft geen geldige rol"
        )
    
    permissions = [perm.name for perm in role.permissions]
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role_name": role.name,
        "role_display_name": role.display_name,
        "permissions": permissions,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login,
        "store_code": current_user.store_code,
        "store_name": current_user.store_name,
    }


@router.post("/logout")
async def logout(
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Logout endpoint - In een JWT systeem gebeurt logout client-side
    
    Dit endpoint kan gebruikt worden voor server-side logging of cleanup
    """
    return {"message": "Succesvol uitgelogd"}
