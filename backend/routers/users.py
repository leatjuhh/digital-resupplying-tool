"""
Users management router - CRUD operations voor gebruikers
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

import db_models
from database import get_db
from auth import (
    get_current_active_user,
    require_permission,
    get_password_hash,
    validate_password_strength
)

router = APIRouter(prefix="/api/users", tags=["users"])


# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    role_id: int
    is_active: bool = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role_id: int
    role_name: str
    role_display_name: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=list[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: db_models.User = Depends(require_permission("view_users")),
    db: Session = Depends(get_db)
):
    """
    Haal alle gebruikers op (alleen voor users met view_users permission)
    """
    users = db.query(db_models.User).offset(skip).limit(limit).all()
    
    # Voeg rol info toe
    result = []
    for user in users:
        role = db.query(db_models.Role).filter(
            db_models.Role.id == user.role_id
        ).first()
        
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role_id": user.role_id,
            "role_name": role.name if role else "unknown",
            "role_display_name": role.display_name if role else "Unknown",
            "is_active": user.is_active,
            "last_login": user.last_login,
            "created_at": user.created_at
        }
        result.append(user_data)
    
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: db_models.User = Depends(require_permission("view_users")),
    db: Session = Depends(get_db)
):
    """
    Haal een specifieke gebruiker op
    """
    user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gebruiker niet gevonden"
        )
    
    role = db.query(db_models.Role).filter(
        db_models.Role.id == user.role_id
    ).first()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role_id": user.role_id,
        "role_name": role.name if role else "unknown",
        "role_display_name": role.display_name if role else "Unknown",
        "is_active": user.is_active,
        "last_login": user.last_login,
        "created_at": user.created_at
    }


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: db_models.User = Depends(require_permission("manage_users")),
    db: Session = Depends(get_db)
):
    """
    Maak een nieuwe gebruiker aan (alleen voor users met manage_users permission)
    """
    # Check of username al bestaat
    existing_user = db.query(db_models.User).filter(
        db_models.User.username == user_data.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gebruikersnaam bestaat al"
        )
    
    # Check of email al bestaat
    existing_email = db.query(db_models.User).filter(
        db_models.User.email == user_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mailadres is al in gebruik"
        )
    
    # Valideer password sterkte
    is_valid, error_msg = validate_password_strength(
        user_data.password,
        user_data.username
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Check of rol bestaat
    role = db.query(db_models.Role).filter(
        db_models.Role.id == user_data.role_id
    ).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol niet gevonden"
        )
    
    # Maak gebruiker aan
    hashed_password = get_password_hash(user_data.password)
    
    new_user = db_models.User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role_id=user_data.role_id,
        is_active=user_data.is_active
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "role_id": new_user.role_id,
        "role_name": role.name,
        "role_display_name": role.display_name,
        "is_active": new_user.is_active,
        "last_login": new_user.last_login,
        "created_at": new_user.created_at
    }


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: db_models.User = Depends(require_permission("manage_users")),
    db: Session = Depends(get_db)
):
    """
    Update een gebruiker (alleen voor users met manage_users permission)
    """
    user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gebruiker niet gevonden"
        )
    
    # Check of er minimaal 1 actieve admin overblijft
    if user_id == current_user.id and user_data.is_active is False:
        role = db.query(db_models.Role).filter(
            db_models.Role.id == user.role_id
        ).first()
        
        if role and role.name == "admin":
            active_admins = db.query(db_models.User).join(
                db_models.Role
            ).filter(
                db_models.Role.name == "admin",
                db_models.User.is_active == True,
                db_models.User.id != user_id
            ).count()
            
            if active_admins == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Kan laatste actieve admin niet deactiveren"
                )
    
    # Update velden
    if user_data.username is not None:
        # Check of nieuwe username al bestaat
        existing = db.query(db_models.User).filter(
            db_models.User.username == user_data.username,
            db_models.User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gebruikersnaam bestaat al"
            )
        user.username = user_data.username
    
    if user_data.email is not None:
        # Check of nieuwe email al bestaat
        existing = db.query(db_models.User).filter(
            db_models.User.email == user_data.email,
            db_models.User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="E-mailadres is al in gebruik"
            )
        user.email = user_data.email
    
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    if user_data.role_id is not None:
        # Check of rol bestaat
        role = db.query(db_models.Role).filter(
            db_models.Role.id == user_data.role_id
        ).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rol niet gevonden"
            )
        user.role_id = user_data.role_id
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    # Haal rol op voor response
    role = db.query(db_models.Role).filter(
        db_models.Role.id == user.role_id
    ).first()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role_id": user.role_id,
        "role_name": role.name if role else "unknown",
        "role_display_name": role.display_name if role else "Unknown",
        "is_active": user.is_active,
        "last_login": user.last_login,
        "created_at": user.created_at
    }


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: db_models.User = Depends(require_permission("manage_users")),
    db: Session = Depends(get_db)
):
    """
    Verwijder een gebruiker (alleen voor users met manage_users permission)
    """
    user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gebruiker niet gevonden"
        )
    
    # Kan jezelf niet verwijderen
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Je kunt jezelf niet verwijderen"
        )
    
    # Check of er minimaal 1 admin overblijft
    role = db.query(db_models.Role).filter(
        db_models.Role.id == user.role_id
    ).first()
    
    if role and role.name == "admin":
        admin_count = db.query(db_models.User).join(
            db_models.Role
        ).filter(
            db_models.Role.name == "admin"
        ).count()
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kan laatste admin niet verwijderen"
            )
    
    db.delete(user)
    db.commit()
    
    return None


@router.patch("/{user_id}/password")
async def change_password(
    user_id: int,
    password_data: PasswordChange,
    current_user: db_models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Wijzig wachtwoord (eigen account of met manage_users permission)
    """
    # Check of gebruiker zichzelf update of admin is
    if user_id != current_user.id:
        # Check manage_users permission
        role = db.query(db_models.Role).filter(
            db_models.Role.id == current_user.role_id
        ).first()
        
        has_permission = any(
            perm.name == "manage_users" for perm in role.permissions
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Je kunt alleen je eigen wachtwoord wijzigen"
            )
    
    user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gebruiker niet gevonden"
        )
    
    # Verify current password (alleen bij eigen account)
    if user_id == current_user.id:
        from auth import verify_password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Huidig wachtwoord is onjuist"
            )
    
    # Valideer nieuwe password sterkte
    is_valid, error_msg = validate_password_strength(
        password_data.new_password,
        user.username
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Update password
    user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Wachtwoord succesvol gewijzigd"}
