"""
Settings router - Beheer applicatie instellingen
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

import db_models
from database import get_db
from auth import get_current_active_user, require_permission

router = APIRouter(prefix="/api/settings", tags=["settings"])


# Pydantic models
class SettingResponse(BaseModel):
    key: str
    value: Any
    category: str
    description: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SettingUpdate(BaseModel):
    value: Any


class SettingsUpdate(BaseModel):
    settings: dict[str, Any]


class ApiKeyPayload(BaseModel):
    api_key: str


def _mask_api_key(raw_value: Any) -> dict[str, Any]:
    api_key = None

    if isinstance(raw_value, dict):
        api_key = raw_value.get("key")
    elif isinstance(raw_value, str):
        api_key = raw_value

    if not api_key:
        return {"configured": False, "masked_key": None}

    if len(api_key) <= 11:
        masked_key = "configured"
    else:
        masked_key = f"{api_key[:7]}...{api_key[-4:]}"

    return {
        "configured": True,
        "masked_key": masked_key,
    }


def _serialize_setting(setting: db_models.Settings) -> dict[str, Any]:
    value = setting.value
    if setting.category == "api" or setting.key == "openai_api_key":
        value = _mask_api_key(setting.value)

    return {
        "key": setting.key,
        "value": value,
        "category": setting.category,
        "description": setting.description,
        "updated_at": setting.updated_at,
    }


@router.get("", response_model=list[SettingResponse])
async def get_all_settings(
    category: Optional[str] = None,
    current_user: db_models.User = Depends(require_permission("view_settings")),
    db: Session = Depends(get_db)
):
    """
    Haal alle instellingen op, optioneel gefilterd op categorie
    """
    query = db.query(db_models.Settings)
    
    if category:
        query = query.filter(db_models.Settings.category == category)
    
    settings = query.all()
    
    return [_serialize_setting(setting) for setting in settings]


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    current_user: db_models.User = Depends(require_permission("view_settings")),
    db: Session = Depends(get_db)
):
    """
    Haal een specifieke instelling op
    """
    setting = db.query(db_models.Settings).filter(
        db_models.Settings.key == key
    ).first()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instelling '{key}' niet gevonden"
        )
    
    return _serialize_setting(setting)


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    setting_data: SettingUpdate,
    current_user: db_models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update een specifieke instelling
    """
    setting = db.query(db_models.Settings).filter(
        db_models.Settings.key == key
    ).first()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instelling '{key}' niet gevonden"
        )
    
    # Check permissions based on category
    if setting.category == "api":
        # API settings require manage_api_settings permission
        role = db.query(db_models.Role).filter(
            db_models.Role.id == current_user.role_id
        ).first()
        
        has_permission = any(
            perm.name == "manage_api_settings" for perm in role.permissions
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Je hebt geen toegang tot API instellingen"
            )
    
    elif setting.category == "rules":
        # Rules settings require manage_rules_settings permission
        role = db.query(db_models.Role).filter(
            db_models.Role.id == current_user.role_id
        ).first()
        
        has_permission = any(
            perm.name in ["manage_rules_settings", "manage_general_settings"] 
            for perm in role.permissions
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Je hebt geen toegang tot regel instellingen"
            )
    
    else:  # general
        # General settings require manage_general_settings permission
        role = db.query(db_models.Role).filter(
            db_models.Role.id == current_user.role_id
        ).first()
        
        has_permission = any(
            perm.name == "manage_general_settings" for perm in role.permissions
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Je hebt geen toegang tot algemene instellingen"
            )
    
    # Update setting
    setting.value = setting_data.value
    setting.updated_by = current_user.id
    setting.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(setting)
    
    return _serialize_setting(setting)


@router.put("", response_model=dict)
async def update_multiple_settings(
    settings_data: SettingsUpdate,
    current_user: db_models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update meerdere instellingen tegelijk
    """
    updated_count = 0
    errors = []
    
    for key, value in settings_data.settings.items():
        setting = db.query(db_models.Settings).filter(
            db_models.Settings.key == key
        ).first()
        
        if not setting:
            errors.append(f"Instelling '{key}' niet gevonden")
            continue
        
        # Check permissions (simplified - checks general permission)
        role = db.query(db_models.Role).filter(
            db_models.Role.id == current_user.role_id
        ).first()
        
        required_perms = {
            "api": "manage_api_settings",
            "rules": "manage_rules_settings",
            "general": "manage_general_settings"
        }
        
        required_perm = required_perms.get(setting.category, "manage_general_settings")
        
        has_permission = any(
            perm.name == required_perm for perm in role.permissions
        )
        
        if not has_permission:
            errors.append(f"Geen toegang tot instelling '{key}'")
            continue
        
        # Update setting
        setting.value = value
        setting.updated_by = current_user.id
        setting.updated_at = datetime.utcnow()
        updated_count += 1
    
    db.commit()
    
    return {
        "message": f"{updated_count} instellingen bijgewerkt",
        "updated_count": updated_count,
        "errors": errors if errors else None
    }


@router.get("/general/all", response_model=dict)
async def get_general_settings(
    current_user: db_models.User = Depends(require_permission("view_settings")),
    db: Session = Depends(get_db)
):
    """
    Haal alle algemene instellingen op als dict
    """
    settings = db.query(db_models.Settings).filter(
        db_models.Settings.category == "general"
    ).all()
    
    result = {}
    for setting in settings:
        result[setting.key] = setting.value
    
    return result


@router.get("/rules/all", response_model=dict)
async def get_rules_settings(
    current_user: db_models.User = Depends(require_permission("view_settings")),
    db: Session = Depends(get_db)
):
    """
    Haal alle regel instellingen op als dict
    """
    settings = db.query(db_models.Settings).filter(
        db_models.Settings.category == "rules"
    ).all()
    
    result = {}
    for setting in settings:
        result[setting.key] = setting.value
    
    return result


@router.get("/api/openai-key/status")
async def get_openai_key_status(
    current_user: db_models.User = Depends(require_permission("manage_api_settings")),
    db: Session = Depends(get_db)
):
    """
    Geef alleen masked metadata terug voor de OpenAI API key.
    """
    setting = db.query(db_models.Settings).filter(
        db_models.Settings.key == "openai_api_key"
    ).first()

    if not setting:
        return {
            "configured": False,
            "masked_key": None,
            "updated_at": None,
        }

    return {
        **_mask_api_key(setting.value),
        "updated_at": setting.updated_at,
    }


@router.post("/validate-api-key")
async def validate_api_key(
    payload: ApiKeyPayload,
    current_user: db_models.User = Depends(require_permission("manage_api_settings")),
):
    """
    Valideer een OpenAI API key
    
    TODO: Implementeer echte OpenAI API validatie
    """
    # Basic validation
    api_key = payload.api_key.strip()

    if not api_key.startswith("sk-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key moet beginnen met 'sk-'"
        )
    
    if len(api_key) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key is te kort"
        )
    
    # TODO: Maak echte API call naar OpenAI om key te valideren
    # Voor nu: simuleer validatie
    is_valid = len(api_key) > 40  # Simpele mock validatie
    
    if is_valid:
        return {
            "valid": True,
            "message": "API key is geldig"
        }
    else:
        return {
            "valid": False,
            "message": "API key lijkt ongeldig te zijn"
        }


@router.put("/api/openai-key")
async def update_openai_key(
    payload: ApiKeyPayload,
    current_user: db_models.User = Depends(require_permission("manage_api_settings")),
    db: Session = Depends(get_db)
):
    """
    Update de OpenAI API key
    """
    # Valideer eerst de key
    api_key = payload.api_key.strip()

    if not api_key.startswith("sk-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key moet beginnen met 'sk-'"
        )
    
    # Haal of creëer de setting
    setting = db.query(db_models.Settings).filter(
        db_models.Settings.key == "openai_api_key"
    ).first()
    
    if not setting:
        # Creëer nieuwe setting
        setting = db_models.Settings(
            key="openai_api_key",
            value={"key": api_key},  # Store as JSON for encryption later
            category="api",
            description="OpenAI API Key voor AI functies"
        )
        db.add(setting)
    else:
        # Update bestaande setting
        setting.value = {"key": api_key}
        setting.updated_at = datetime.utcnow()
    
    setting.updated_by = current_user.id
    
    db.commit()
    
    return {
        "message": "OpenAI API key succesvol opgeslagen",
        "masked_key": f"{api_key[:7]}...{api_key[-4:]}"
    }
