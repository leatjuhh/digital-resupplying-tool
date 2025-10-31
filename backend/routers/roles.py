"""
Roles management router - Beheer rollen en permissies
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

import db_models
from database import get_db
from auth import require_permission

router = APIRouter(prefix="/api/roles", tags=["roles"])


# Pydantic models
class RoleCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None


class RolePermissionsUpdate(BaseModel):
    permission_ids: list[int]


class PermissionResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    category: str
    
    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    is_system_role: bool
    permissions: list[PermissionResponse]
    user_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=list[RoleResponse])
async def get_roles(
    current_user: db_models.User = Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db)
):
    """
    Haal alle rollen op met hun permissions
    """
    roles = db.query(db_models.Role).all()
    
    result = []
    for role in roles:
        # Tel gebruikers met deze rol
        user_count = db.query(db_models.User).filter(
            db_models.User.role_id == role.id
        ).count()
        
        # Converteer permissions naar response format
        permissions = [
            {
                "id": perm.id,
                "name": perm.name,
                "display_name": perm.display_name,
                "description": perm.description,
                "category": perm.category
            }
            for perm in role.permissions
        ]
        
        result.append({
            "id": role.id,
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "is_system_role": role.is_system_role,
            "permissions": permissions,
            "user_count": user_count,
            "created_at": role.created_at
        })
    
    return result


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: db_models.User = Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db)
):
    """
    Haal een specifieke rol op met zijn permissions
    """
    role = db.query(db_models.Role).filter(db_models.Role.id == role_id).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol niet gevonden"
        )
    
    # Tel gebruikers met deze rol
    user_count = db.query(db_models.User).filter(
        db_models.User.role_id == role.id
    ).count()
    
    # Converteer permissions
    permissions = [
        {
            "id": perm.id,
            "name": perm.name,
            "display_name": perm.display_name,
            "description": perm.description,
            "category": perm.category
        }
        for perm in role.permissions
    ]
    
    return {
        "id": role.id,
        "name": role.name,
        "display_name": role.display_name,
        "description": role.description,
        "is_system_role": role.is_system_role,
        "permissions": permissions,
        "user_count": user_count,
        "created_at": role.created_at
    }


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: db_models.User = Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db)
):
    """
    Maak een nieuwe rol aan
    """
    # Check of role name al bestaat
    existing = db.query(db_models.Role).filter(
        db_models.Role.name == role_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol naam bestaat al"
        )
    
    # Maak nieuwe rol
    new_role = db_models.Role(
        name=role_data.name,
        display_name=role_data.display_name,
        description=role_data.description,
        is_system_role=False  # Custom roles zijn nooit system roles
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return {
        "id": new_role.id,
        "name": new_role.name,
        "display_name": new_role.display_name,
        "description": new_role.description,
        "is_system_role": new_role.is_system_role,
        "permissions": [],
        "user_count": 0,
        "created_at": new_role.created_at
    }


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: db_models.User = Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db)
):
    """
    Update een rol (alleen custom roles, geen system roles)
    """
    role = db.query(db_models.Role).filter(db_models.Role.id == role_id).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol niet gevonden"
        )
    
    # System roles kunnen niet aangepast worden (behalve permissions)
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System roles kunnen niet worden aangepast. Gebruik /permissions endpoint voor permission wijzigingen."
        )
    
    # Update velden
    if role_data.name is not None:
        # Check of nieuwe naam al bestaat
        existing = db.query(db_models.Role).filter(
            db_models.Role.name == role_data.name,
            db_models.Role.id != role_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol naam bestaat al"
            )
        role.name = role_data.name
    
    if role_data.display_name is not None:
        role.display_name = role_data.display_name
    
    if role_data.description is not None:
        role.description = role_data.description
    
    db.commit()
    db.refresh(role)
    
    # Tel gebruikers
    user_count = db.query(db_models.User).filter(
        db_models.User.role_id == role.id
    ).count()
    
    # Converteer permissions
    permissions = [
        {
            "id": perm.id,
            "name": perm.name,
            "display_name": perm.display_name,
            "description": perm.description,
            "category": perm.category
        }
        for perm in role.permissions
    ]
    
    return {
        "id": role.id,
        "name": role.name,
        "display_name": role.display_name,
        "description": role.description,
        "is_system_role": role.is_system_role,
        "permissions": permissions,
        "user_count": user_count,
        "created_at": role.created_at
    }


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user: db_models.User = Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db)
):
    """
    Verwijder een rol (alleen custom roles)
    """
    role = db.query(db_models.Role).filter(db_models.Role.id == role_id).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol niet gevonden"
        )
    
    # System roles kunnen niet verwijderd worden
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System roles kunnen niet worden verwijderd"
        )
    
    # Check of er gebruikers met deze rol zijn
    user_count = db.query(db_models.User).filter(
        db_models.User.role_id == role.id
    ).count()
    
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Kan rol niet verwijderen: {user_count} gebruiker(s) hebben deze rol"
        )
    
    db.delete(role)
    db.commit()
    
    return None


@router.get("/{role_id}/permissions", response_model=list[PermissionResponse])
async def get_role_permissions(
    role_id: int,
    current_user: db_models.User = Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db)
):
    """
    Haal alle permissions van een rol op
    """
    role = db.query(db_models.Role).filter(db_models.Role.id == role_id).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol niet gevonden"
        )
    
    return [
        {
            "id": perm.id,
            "name": perm.name,
            "display_name": perm.display_name,
            "description": perm.description,
            "category": perm.category
        }
        for perm in role.permissions
    ]


@router.put("/{role_id}/permissions")
async def update_role_permissions(
    role_id: int,
    permissions_data: RolePermissionsUpdate,
    current_user: db_models.User = Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db)
):
    """
    Update de permissions van een rol
    """
    role = db.query(db_models.Role).filter(db_models.Role.id == role_id).first()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol niet gevonden"
        )
    
    # Verify dat alle permission IDs bestaan
    permissions = db.query(db_models.Permission).filter(
        db_models.Permission.id.in_(permissions_data.permission_ids)
    ).all()
    
    if len(permissions) != len(permissions_data.permission_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Een of meer permission IDs zijn ongeldig"
        )
    
    # Update role permissions
    role.permissions = permissions
    db.commit()
    
    return {
        "message": "Permissions succesvol bijgewerkt",
        "role_id": role.id,
        "permission_count": len(permissions)
    }


@router.get("/permissions/all", response_model=list[PermissionResponse])
async def get_all_permissions(
    current_user: db_models.User = Depends(require_permission("manage_roles")),
    db: Session = Depends(get_db)
):
    """
    Haal alle beschikbare permissions op (gegroepeerd per categorie)
    """
    permissions = db.query(db_models.Permission).order_by(
        db_models.Permission.category,
        db_models.Permission.name
    ).all()
    
    return [
        {
            "id": perm.id,
            "name": perm.name,
            "display_name": perm.display_name,
            "description": perm.description,
            "category": perm.category
        }
        for perm in permissions
    ]
