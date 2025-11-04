# Baseline Fase 6: Feedback & Iteratie System

**Status:** ⏸️ Waiting (Blocked by Fase 5)  
**Priority:** 🔴 High Priority (voor learning capability)  
**Tijdsinschatting:** 3-4 dagen  
**Start Datum:** TBD (na Fase 5)  
**Target Datum:** TBD

---

## 🎯 Doel

Implementeer human-in-the-loop feedback systeem voor iteratieve verbetering van het algoritme. Focus op manuele analyse en parameter tuning, minimale AI usage.

---

## 📋 Checklist

### Design & Planning
- [ ] Design database schema voor feedback
- [ ] Design configuratie versioning systeem
- [ ] Plan feedback analyse workflow (manueel)
- [ ] Design parameter adjustment UI mockups

### Database Implementation
- [ ] Update `backend/db_models.py`
  - [ ] `ProposalFeedback` table
  - [ ] `AlgorithmConfig` table
  - [ ] Relaties en constraints
  - [ ] Indexes voor performance

- [ ] Create migration script
  - [ ] `backend/migrate_add_feedback_tables.py`
  - [ ] Test migration
  - [ ] Rollback script

### Backend API Implementation
- [ ] Update `backend/routers/proposals.py`
  - [ ] `POST /api/proposals/{id}/feedback` endpoint
  - [ ] `GET /api/proposals/{id}/feedback` endpoint
  - [ ] `GET /api/feedback/summary` endpoint (admin)
  - [ ] Validation en error handling

- [ ] Implement `backend/routers/algorithm_config.py` (NEW)
  - [ ] `GET /api/config/versions` - List configs
  - [ ] `GET /api/config/active` - Get active config
  - [ ] `POST /api/config` - Create new config version
  - [ ] `PUT /api/config/{id}/activate` - Activate version
  - [ ] Admin-only access control

- [ ] Implement `backend/redistribution/feedback_analyzer.py`
  - [ ] `FeedbackStats` dataclass
  - [ ] `analyze_feedback_patterns()` - Manuele analyse helpers
  - [ ] `generate_feedback_report()` - Summary voor admin
  - [ ] NO automatic parameter tuning
  - [ ] Optional: OpenAI summary (disabled by default)

### Frontend Implementation
- [ ] Create `frontend/components/proposals/feedback-form.tsx`
  - [ ] Feedback type selector (approve/reject/edit/comment)
  - [ ] Text area voor uitleg
  - [ ] Submit functionaliteit
  - [ ] Success/error toast

- [ ] Create `frontend/app/admin/feedback/page.tsx`
  - [ ] Feedback overview table
  - [ ] Filter op type, datum, user
  - [ ] Feedback detail view
  - [ ] Pattern identification tools
  - [ ] Export functionaliteit

- [ ] Create `frontend/app/admin/algorithm-config/page.tsx`
  - [ ] Config versie lijst
  - [ ] Active config display
  - [ ] Create new version form
  - [ ] Parameter editor (JSON/form)
  - [ ] Activate/deactivate buttons
  - [ ] Version diff viewer

### Testing
- [ ] Maak test bestand `backend/test_feedback.py`
  - [ ] Test feedback submission
  - [ ] Test feedback retrieval
  - [ ] Test feedback stats
  - [ ] Test access control

- [ ] Maak test bestand `backend/test_algorithm_config.py`
  - [ ] Test config CRUD
  - [ ] Test versioning
  - [ ] Test activation
  - [ ] Test parameter validation

- [ ] Integration tests
  - [ ] Full feedback workflow
  - [ ] Config update → rerun proposals
  - [ ] Admin UI tests

### Documentation
- [ ] Voeg docstrings toe aan alle functies
- [ ] Update `docs/technical/baseline-implementation-plan.md`
- [ ] Maak `docs/technical/feedback-system.md`
  - [ ] Database schema
  - [ ] API endpoints
  - [ ] Workflow diagram
  - [ ] Parameter tuning guide
- [ ] Maak `docs/guides/feedback-workflow.md` (user guide)
  - [ ] Hoe feedback geven
  - [ ] Admin analyse proces
  - [ ] Config versioning
- [ ] Update `docs/guides/redistribution-algorithm.md`

### Review & Refinement
- [ ] Code review (security, access control)
- [ ] Test feedback workflow met user
- [ ] Validate parameter editor werkt
- [ ] Test versioning systeem
- [ ] Final security review
- [ ] Performance testing

### Git & Documentation
- [ ] Git commit met message: "feat: implement feedback & iteration system (Baseline Phase 6)"
- [ ] Update `CHANGELOG.md` met Fase 6 changes
- [ ] Update session log
- [ ] Mark todo as complete

---

## 📐 Technical Design

### Database Schema

#### ProposalFeedback Table
```python
class ProposalFeedback(Base):
    __tablename__ = "proposal_feedback"
    
    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    feedback_type = Column(String(20), nullable=False)
    # "approve", "reject", "edit", "comment"
    
    feedback_text = Column(Text, nullable=False)
    # Vrije tekst uitleg van gebruiker
    
    changes_made = Column(JSON, nullable=True)
    # Bij "edit": {"size": "M", "from": "001", "to": "002", "qty_before": 5, "qty_after": 3}
    
    algorithm_version = Column(String(20), nullable=False)
    # Welke config versie gebruikte proposal
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    proposal = relationship("Proposal", backref="feedback")
    user = relationship("User", backref="feedback")
```

#### AlgorithmConfig Table
```python
class AlgorithmConfig(Base):
    __tablename__ = "algorithm_configs"
    
    id = Column(Integer, primary_key=True)
    version = Column(String(20), unique=True, nullable=False)
    # "1.0", "1.1", "2.0", etc.
    
    name = Column(String(100), nullable=False)
    # Beschrijvende naam: "Baseline V1", "Winter Tuning", etc.
    
    description = Column(Text)
    # Wat is er veranderd t.o.v. vorige versie
    
    parameters = Column(JSON, nullable=False)
    # Complete RedistributionParams als JSON
    
    category_policies = Column(JSON, nullable=True)
    # CATEGORY_POLICIES als JSON
    
    situation_thresholds = Column(JSON, nullable=True)
    # SituationThresholds als JSON
    
    is_active = Column(Boolean, default=False)
    # Slechts 1 config kan active zijn
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)
    
    notes = Column(Text)
    # Admin notes
    
    # Relationships
    creator = relationship("User")
```

### API Endpoints

#### Feedback Endpoints
```python
# backend/routers/proposals.py (UPDATE)

@router.post("/api/proposals/{id}/feedback")
def submit_feedback(
    id: int,
    feedback: ProposalFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback voor een proposal.
    
    Feedback types:
    - approve: Voorstel goedgekeurd
    - reject: Voorstel afgekeurd (met reden)
    - edit: Voorstel aangepast (met wijzigingen)
    - comment: Algemeen commentaar
    """
    # Validate proposal exists
    # Get active algorithm version
    # Save feedback
    # Return success

@router.get("/api/proposals/{id}/feedback")
def get_proposal_feedback(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alle feedback voor een proposal"""
    pass

@router.get("/api/feedback/summary")
def get_feedback_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get feedback summary voor admin analyse.
    Toont patronen, veelvoorkomende feedback, statistieken.
    """
    pass
```

#### Config Endpoints
```python
# backend/routers/algorithm_config.py (NEW)

@router.get("/api/config/versions")
def list_config_versions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List alle config versies"""
    pass

@router.get("/api/config/active")
def get_active_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get currently active config"""
    pass

@router.post("/api/config")
def create_config_version(
    config: AlgorithmConfigCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create nieuwe config versie.
    Admin past parameters aan op basis van feedback analyse.
    """
    pass

@router.put("/api/config/{id}/activate")
def activate_config(
    id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Activeer een config versie.
    Deactiveert automatisch de huidige active config.
    """
    pass

@router.get("/api/config/{id}/diff")
def get_config_diff(
    id: int,
    compare_to: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Toon verschil tussen twee configs.
    Handig om te zien wat er veranderd is.
    """
    pass
```

### Feedback Analysis (Manueel)

```python
# backend/redistribution/feedback_analyzer.py

@dataclass
class FeedbackStats:
    """Stats voor feedback analyse"""
    total_feedback: int
    by_type: Dict[str, int]  # {feedback_type: count}
    by_algorithm_version: Dict[str, int]
    approval_rate: float
    rejection_rate: float
    common_rejection_reasons: List[Tuple[str, int]]  # [(reason, count)]
    articles_with_most_feedback: List[Tuple[str, int]]
    
def analyze_feedback_patterns(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> FeedbackStats:
    """
    Analyseer feedback patronen voor admin.
    
    GEEN automatische parameter tuning!
    Alleen statistieken en patronen identificeren.
    
    Admin gebruikt deze info om handmatig parameters aan te passen.
    """
    pass

def generate_feedback_report(
    stats: FeedbackStats,
    use_ai_summary: bool = False
) -> str:
    """
    Genereer rapport voor admin.
    
    Args:
        stats: Feedback statistieken
        use_ai_summary: Optioneel, gebruik OpenAI voor summary
        
    Returns:
        Markdown rapport met analyse en suggesties
    """
    if use_ai_summary:
        # OPTIONEEL: gebruik OpenAI om patronen samen te vatten
        # Maar GEEN automatische parameter aanpassingen!
        pass
    else:
        # Generate manueel rapport
        pass
```

### Frontend Components

#### Feedback Form Component
```typescript
// frontend/components/proposals/feedback-form.tsx

interface FeedbackFormProps {
  proposalId: number;
  onSubmit: () => void;
}

export function FeedbackForm({ proposalId, onSubmit }: FeedbackFormProps) {
  const [feedbackType, setFeedbackType] = useState<string>("approve");
  const [feedbackText, setFeedbackText] = useState<string>("");
  
  const handleSubmit = async () => {
    // API call to submit feedback
    // Show toast on success/error
    // Call onSubmit callback
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Feedback Geven</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Feedback type selector */}
          <RadioGroup value={feedbackType} onValueChange={setFeedbackType}>
            <RadioGroupItem value="approve">Goedkeuren</RadioGroupItem>
            <RadioGroupItem value="reject">Afkeuren</RadioGroupItem>
            <RadioGroupItem value="comment">Commentaar</RadioGroupItem>
          </RadioGroup>
          
          {/* Feedback tekst */}
          <Textarea
            placeholder="Leg uit waarom..."
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
          />
          
          {/* Submit button */}
          <Button onClick={handleSubmit}>
            Feedback Versturen
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## 🧪 Test Cases

### Test 1: Feedback Submission
**Input:** Reject feedback met reden
**Expected:** Opgeslagen in database, zichtbaar in admin

### Test 2: Config Versioning
**Input:** Maak nieuwe config "1.1" met aangepaste thresholds
**Expected:** Versie opgeslagen, oude versie blijft beschikbaar

### Test 3: Config Activation
**Input:** Activeer config "1.1"
**Expected:** "1.1" is active, oude config gedeactiveerd

### Test 4: Feedback Analysis
**Input:** 100 feedback items over 1 week
**Expected:** Stats rapport gegenereerd met patronen

### Test 5: Access Control
**Input:** Regular user probeert config te wijzigen
**Expected:** 403 Forbidden error

---

## 📊 Success Criteria

### Functional
✅ Feedback wordt opgeslagen in database  
✅ Admin kan feedback reviewen  
✅ Config versioning werkt  
✅ Parameter wijzigingen traceerbaar  
✅ Proposals gebruiken active config  

### Technical
✅ Type hints en docstrings  
✅ Database migrations werken  
✅ API endpoints secured (admin only)  
✅ Unit tests >80% coverage  

### Quality
✅ Workflow is intuïtief voor users  
✅ Admin kan effectief patronen zien  
✅ Versioning voorkomt verlies van oude configs  
✅ Performance geen issues  

---

## 🔗 Dependencies

### Blocked By:
- Fase 5: Compensatie (laatste feature voor complete baseline)

### Blocks:
- Niets (laatste fase!)

---

## 📝 Notes

### Minimale AI Usage
Focus op HUMAN expertise:
- Admin analyseert feedback manueel
- Admin past parameters handmatig aan
- OpenAI ALLEEN voor optionele summary (disabled by default)
- Geen automatische parameter tuning

### Iteratie Proces
1. Users gebruiken tool, geven feedback
2. Admin bekijkt feedback dashboard
3. Admin identificeert patronen (bijv. "jassen altijd te geconcentreerd")
4. Admin maakt nieuwe config versie met aangepaste parameters
5. Admin activeert nieuwe versie
6. Test nieuwe versie met rerun
7. Herhaal

### Future: A/B Testing
Later kun je multiple configs activeren voor verschillende batches om te vergelijken.

### Security
Config wijzigingen zijn ADMIN-ONLY. Dit voorkomt ongewenste wijzigingen.

---

**Last Updated:** 2025-11-05  
**Assigned To:** Cline AI  
**Reviewer:** User
