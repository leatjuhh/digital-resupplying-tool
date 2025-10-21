# Importeer FastAPI componenten en database dependencies
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Importeer Pydantic models (voor API) en database models (voor ORM)
from models import Article
from database import get_db
import db_models

# Maak een router aan voor alle article-gerelateerde endpoints
router = APIRouter()


@router.get("/articles", response_model=List[Article])
async def get_articles(db: Session = Depends(get_db)):
    """
    Get all articles from database
    """
    # Haal alle artikelen op uit de database
    db_articles = db.query(db_models.Article).all()
    
    # Converteer database models naar Pydantic models voor de API response
    articles = [
        Article(
            artikelnummer=art.artikelnummer,
            omschrijving=art.omschrijving,
            voorraad_per_winkel=art.voorraad_per_winkel
        )
        for art in db_articles
    ]
    
    return articles


@router.get("/articles/{artikelnummer}", response_model=Article)
async def get_article(artikelnummer: str, db: Session = Depends(get_db)):
    """
    Get a specific article by artikelnummer
    """
    # Zoek artikel op basis van artikelnummer
    db_article = db.query(db_models.Article).filter(
        db_models.Article.artikelnummer == artikelnummer
    ).first()
    
    # Als artikel niet bestaat, geef 404 error
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Converteer database model naar Pydantic model
    return Article(
        artikelnummer=db_article.artikelnummer,
        omschrijving=db_article.omschrijving,
        voorraad_per_winkel=db_article.voorraad_per_winkel
    )


@router.post("/articles", response_model=Article, status_code=201)
async def create_article(article: Article, db: Session = Depends(get_db)):
    """
    Create a new article
    """
    # Controleer of artikel al bestaat in de database
    existing = db.query(db_models.Article).filter(
        db_models.Article.artikelnummer == article.artikelnummer
    ).first()
    
    # Als artikel al bestaat, geef 400 error
    if existing:
        raise HTTPException(status_code=400, detail="Article already exists")
    
    # Maak nieuw artikel aan in de database
    db_article = db_models.Article(
        artikelnummer=article.artikelnummer,
        omschrijving=article.omschrijving,
        voorraad_per_winkel=article.voorraad_per_winkel
    )
    
    # Voeg artikel toe aan database sessie
    db.add(db_article)
    # Sla wijzigingen op in de database
    db.commit()
    # Haal de nieuwste versie op (met ID etc.)
    db.refresh(db_article)
    
    # Converteer en retourneer het nieuwe artikel
    return Article(
        artikelnummer=db_article.artikelnummer,
        omschrijving=db_article.omschrijving,
        voorraad_per_winkel=db_article.voorraad_per_winkel
    )


@router.put("/articles/{artikelnummer}", response_model=Article)
async def update_article(
    artikelnummer: str,
    article: Article,
    db: Session = Depends(get_db)
):
    """
    Update an existing article
    """
    # Zoek het bestaande artikel in de database
    db_article = db.query(db_models.Article).filter(
        db_models.Article.artikelnummer == artikelnummer
    ).first()
    
    # Als artikel niet bestaat, geef 404 error
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Update de velden (artikelnummer blijft ongewijzigd)
    db_article.omschrijving = article.omschrijving
    db_article.voorraad_per_winkel = article.voorraad_per_winkel
    
    # Sla wijzigingen op in de database
    db.commit()
    # Haal de nieuwste versie op
    db.refresh(db_article)
    
    # Converteer en retourneer het bijgewerkte artikel
    return Article(
        artikelnummer=db_article.artikelnummer,
        omschrijving=db_article.omschrijving,
        voorraad_per_winkel=db_article.voorraad_per_winkel
    )


@router.delete("/articles/{artikelnummer}", status_code=204)
async def delete_article(artikelnummer: str, db: Session = Depends(get_db)):
    """
    Delete an article
    """
    # Zoek het artikel dat verwijderd moet worden
    db_article = db.query(db_models.Article).filter(
        db_models.Article.artikelnummer == artikelnummer
    ).first()
    
    # Als artikel niet bestaat, geef 404 error
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Verwijder artikel uit de database
    db.delete(db_article)
    # Sla wijzigingen op
    db.commit()
    
    # Return None (status code 204 = No Content)
    return None
