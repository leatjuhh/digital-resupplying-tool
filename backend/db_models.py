"""
SQLAlchemy database models
"""
# Importeer SQLAlchemy kolom types en de Base class
from sqlalchemy import Column, Integer, String, JSON, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Store(Base):
    """Store/Winkel database model"""
    __tablename__ = "stores"

    # Unieke ID voor elke winkel (primary key, automatisch oplopend)
    id = Column(Integer, primary_key=True, index=True)
    
    # Naam van de winkel (uniek, geïndexeerd voor snelle lookups)
    name = Column(String, unique=True, index=True, nullable=False)
    
    # Stad waar de winkel zich bevindt
    city = Column(String, nullable=False)
    
    # Unieke code voor de winkel (bijv. "AMS" voor Amsterdam)
    code = Column(String, unique=True, nullable=False)


class Article(Base):
    """Article database model"""
    __tablename__ = "articles"

    # Unieke ID voor elk artikel (primary key, automatisch oplopend)
    id = Column(Integer, primary_key=True, index=True)
    
    # Artikelnummer (uniek, geïndexeerd voor snelle lookups, bijv. "ART-001")
    artikelnummer = Column(String, unique=True, index=True, nullable=False)
    
    # Beschrijving/naam van het artikel
    omschrijving = Column(String, nullable=False)
    
    # Voorraad per winkel opgeslagen als JSON object
    # Voorbeeld: {"Amsterdam": 15, "Rotterdam": 8, "Utrecht": 12}
    voorraad_per_winkel = Column(JSON, nullable=False)


class Batch(Base):
    """Batch van PDF uploads - groepeert meerdere PDF's"""
    __tablename__ = "batches"
    
    # Unieke ID voor elke batch
    id = Column(Integer, primary_key=True, index=True)
    
    # Door gebruiker gekozen naam voor deze batch
    name = Column(String, nullable=False)
    
    # Status: 'processing', 'completed', 'failed'
    status = Column(String, default='processing', nullable=False)
    
    # Aantal PDF's in deze batch
    pdf_count = Column(Integer, default=0, nullable=False)
    
    # Aantal verwerkte PDF's
    processed_count = Column(Integer, default=0, nullable=False)
    
    # Aanmaak tijdstip (automatisch ingevuld)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Extra data opgeslagen als JSON (optioneel)
    extra_data = Column(JSON, default={})


class BatchPDF(Base):
    """Individuele PDF binnen een batch"""
    __tablename__ = "batch_pdfs"
    
    # Unieke ID voor elke PDF
    id = Column(Integer, primary_key=True, index=True)
    
    # Verwijzing naar de batch waar deze PDF bij hoort
    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    
    # Originele bestandsnaam
    filename = Column(String, nullable=False)
    
    # Pad waar het bestand is opgeslagen
    file_path = Column(String, nullable=False)
    
    # Status: 'pending', 'processing', 'completed', 'failed'
    status = Column(String, default='pending', nullable=False)
    
    # Geëxtraheerde data als JSON
    parsed_data = Column(JSON)
    
    # Foutmelding indien parsing mislukt
    error_message = Column(Text)
    
    # Upload tijdstip
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Verwerkt op tijdstip
    processed_at = Column(DateTime(timezone=True))


class Proposal(Base):
    """Herverdelingsvoorstel gegenereerd op basis van batch data"""
    __tablename__ = "proposals"
    
    # Unieke ID voor elk voorstel
    id = Column(Integer, primary_key=True, index=True)
    
    # Verwijzing naar de batch (oude systeem, optioneel)
    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=True)
    
    # Verwijzing naar PDF batch (nieuw systeem)
    pdf_batch_id = Column(Integer, ForeignKey('pdf_batches.id'), nullable=True, index=True)
    
    # Artikelnummer waarop dit voorstel betrekking heeft
    artikelnummer = Column(String, nullable=False, index=True)
    
    # Artikel omschrijving
    article_name = Column(String, nullable=False)
    
    # Moves (herverdelingsbewegingen) als JSON
    # [{"size": "M", "from_store": "001", "to_store": "002", "qty": 5, "reason": "..."}]
    moves = Column(JSON, nullable=False)
    
    # Totaal aantal moves
    total_moves = Column(Integer, default=0, nullable=False)
    
    # Totaal aantal stuks
    total_quantity = Column(Integer, default=0, nullable=False)
    
    # Status: 'pending', 'approved', 'rejected', 'edited'
    status = Column(String, default='pending', nullable=False)
    
    # Reden voor voorstel (door systeem gegenereerd)
    reason = Column(Text)
    
    # Toegepaste regels (lijst van regel-namen als JSON)
    applied_rules = Column(JSON, default=[])
    
    # Optimization applied flag
    optimization_applied = Column(String, default='false', nullable=False)
    
    # Betrokken winkels (set van store codes als JSON)
    stores_affected = Column(JSON, default=[])
    
    # Aanmaak tijdstip
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Review tijdstip
    reviewed_at = Column(DateTime(timezone=True))
    
    # Rejection reason (bij afkeur)
    rejection_reason = Column(Text)


class Feedback(Base):
    """Gebruiker feedback op voorstellen"""
    __tablename__ = "feedback"
    
    # Unieke ID
    id = Column(Integer, primary_key=True, index=True)
    
    # Verwijzing naar het voorstel
    proposal_id = Column(Integer, ForeignKey('proposals.id'), nullable=False)
    
    # Categorie: 'quantity', 'timing', 'location', 'other'
    category = Column(String, nullable=False)
    
    # Rating 1-5
    rating = Column(Integer, nullable=False)
    
    # Feedback tekst
    comment = Column(Text, nullable=False)
    
    # Sentiment: 'positive', 'negative', 'neutral' (door AI bepaald, optioneel)
    sentiment = Column(String)
    
    # Aanmaak tijdstip
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PDFBatch(Base):
    """Batch van PDF extracties - groepeert meerdere PDF extractions"""
    __tablename__ = "pdf_batches"
    
    # Unieke ID voor elke batch
    id = Column(Integer, primary_key=True, index=True)
    
    # Door gebruiker gekozen naam voor deze batch
    naam = Column(String, nullable=False)
    
    # Status: 'PENDING', 'SUCCESS', 'FAILED', 'PARTIAL_SUCCESS'
    status = Column(String, default='PENDING', nullable=False)
    
    # Aantal PDF's in deze batch
    pdf_count = Column(Integer, default=0, nullable=False)
    
    # Aantal succesvol verwerkte PDF's
    processed_count = Column(Integer, default=0, nullable=False)
    
    # Aanmaak tijdstip (automatisch ingevuld)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ArtikelVoorraad(Base):
    """Voorraad data geëxtraheerd uit PDF's"""
    __tablename__ = "artikel_voorraad"
    
    # Unieke ID
    id = Column(Integer, primary_key=True, index=True)
    
    # Verwijzing naar PDF batch
    batch_id = Column(Integer, ForeignKey('pdf_batches.id'), nullable=False, index=True)
    
    # Volgnummer (artikelnummer uit PDF)
    volgnummer = Column(String, nullable=False, index=True)
    
    # Artikel omschrijving
    omschrijving = Column(String, nullable=False)
    
    # Filiaal code
    filiaal_code = Column(String, nullable=False)
    
    # Filiaal naam
    filiaal_naam = Column(String, nullable=False)
    
    # Maat
    maat = Column(String, nullable=False)
    
    # Voorraad aantal
    voorraad = Column(Integer, nullable=False, default=0)
    
    # Verkocht aantal
    verkocht = Column(Integer, nullable=False, default=0)
    
    # Metadata uit PDF (leverancier, kleur, etc.) als JSON
    pdf_metadata = Column(JSON)
    
    # Aanmaak tijdstip
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PDFParseLog(Base):
    """Log van PDF parsing events voor debugging"""
    __tablename__ = "pdf_parse_logs"
    
    # Unieke ID
    id = Column(Integer, primary_key=True, index=True)
    
    # Verwijzing naar batch
    batch_id = Column(Integer, ForeignKey('pdf_batches.id'), nullable=False, index=True)
    
    # Fase van parsing: 'HEADER_PARSE', 'ROW_PARSE', 'VALIDATION', etc.
    phase = Column(String, nullable=False)
    
    # Level: 'INFO', 'WARNING', 'ERROR'
    level = Column(String, default='INFO', nullable=False)
    
    # Log bericht
    message = Column(Text, nullable=False)
    
    # Extra data als JSON
    extra_data = Column(JSON)
    
    # Tijdstip
    created_at = Column(DateTime(timezone=True), server_default=func.now())
