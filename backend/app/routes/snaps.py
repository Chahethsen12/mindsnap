from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.snap import Snap
from app.services.auth_service import decode_access_token
from app.services.ai_service import analyze_content

router = APIRouter(prefix="/snaps", tags=["Snaps"])


# --- Helper: Get current user from JWT ---

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract user ID from Bearer token"""
    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return int(payload["sub"])

# --- Request/Response Schemas ---

class CreateSnapRequest(BaseModel):
    source_url: Optional[str] = None
    raw_text: Optional[str] = None  # user can paste raw text instead of URL

class SnapResponse(BaseModel):
    id: int
    title: Optional[str]
    summary: Optional[str]
    content_type: Optional[str]
    source_url: Optional[str]
    tags: Optional[str]

    class Config:
        from_attributes = True


# --- Endpoints ---

@router.post("/", response_model=SnapResponse, status_code=status.HTTP_201_CREATED)
def create_snap(
    body: CreateSnapRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Create a new snap. Accepts a URL or raw pasted text."""
    if not body.source_url and not body.raw_text:
        raise HTTPException(status_code=400, detail="Provide either source_url or raw_text")

    # Use raw text if provided, otherwise use URL as text (URL fetching comes later)
    content_to_analyze = body.raw_text or body.source_url

    # Send to AI for analysis
    try:
        ai_result = analyze_content(content_to_analyze)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    # Save to database
    snap = Snap(
        user_id=user_id,
        title=ai_result.get("title"),
        summary=ai_result.get("summary"),
        content_type=ai_result.get("content_type"),
        source_url=body.source_url,
        tags=", ".join(ai_result.get("tags", []))
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)

    return snap


@router.get("/", response_model=list[SnapResponse])
def get_all_snaps(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Get all snaps for the current user"""
    snaps = db.query(Snap).filter(Snap.user_id == user_id).order_by(Snap.created_at.desc()).all()
    return snaps


@router.get("/search", response_model=list[SnapResponse])
def search_snaps(
    q: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Basic keyword search across title, summary and tags.
    (Semantic/vector search will be added in a later iteration)
    """
    keyword = f"%{q}%"
    snaps = db.query(Snap).filter(
        Snap.user_id == user_id,
        (Snap.title.ilike(keyword)) |
        (Snap.summary.ilike(keyword)) |
        (Snap.tags.ilike(keyword))
    ).all()
    return snaps


@router.delete("/{snap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snap(
    snap_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Delete a snap by ID (only if it belongs to current user)"""
    snap = db.query(Snap).filter(Snap.id == snap_id, Snap.user_id == user_id).first()
    if not snap:
        raise HTTPException(status_code=404, detail="Snap not found")

    db.delete(snap)
    db.commit()
    return
