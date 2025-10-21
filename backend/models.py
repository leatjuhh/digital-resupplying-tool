# Importeer Pydantic voor data validatie en type checking
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class Article(BaseModel):
    """
    Article model representing a product with inventory across stores
    """
    # Artikelnummer (unieke identifier, bijv. "ART-001")
    artikelnummer: str = Field(..., description="Article SKU/number")
    
    # Omschrijving of naam van het artikel
    omschrijving: str = Field(..., description="Article description/name")
    
    # Voorraad per winkel als dictionary: {"winkelnaam": aantal}
    voorraad_per_winkel: Dict[str, int] = Field(
        ..., 
        description="Inventory per store location (store_name: quantity)"
    )

    class Config:
        # Voorbeeld data voor API documentatie (Swagger UI)
        json_schema_extra = {
            "example": {
                "artikelnummer": "ART-001",
                "omschrijving": "Winter Jacket - Blue",
                "voorraad_per_winkel": {
                    "Amsterdam": 15,
                    "Rotterdam": 8,
                    "Utrecht": 12
                }
            }
        }


# Batch models
class BatchCreate(BaseModel):
    """Model voor het aanmaken van een nieuwe batch"""
    name: str = Field(..., description="Naam voor deze batch", min_length=1)


class BatchResponse(BaseModel):
    """Model voor batch response"""
    id: int
    name: str
    status: str
    pdf_count: int
    processed_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PDFUploadResponse(BaseModel):
    """Response na PDF upload"""
    batch_id: int
    filename: str
    status: str
    message: str


class BatchDetailResponse(BaseModel):
    """Gedetailleerde batch informatie"""
    id: int
    name: str
    status: str
    pdf_count: int
    processed_count: int
    created_at: datetime
    pdfs: List[Dict]  # Lijst van PDF details
    
    class Config:
        from_attributes = True


# Proposal models
class ProposalResponse(BaseModel):
    """Model voor proposal response"""
    id: int
    batch_id: int
    artikelnummer: str
    article_name: str
    current_distribution: Dict
    proposed_distribution: Dict
    status: str
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Feedback models
class FeedbackCreate(BaseModel):
    """Model voor het aanmaken van feedback"""
    proposal_id: int
    category: str = Field(..., description="quantity, timing, location, other")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    comment: str = Field(..., min_length=1)
