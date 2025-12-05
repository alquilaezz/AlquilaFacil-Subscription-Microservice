from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/api/v1", tags=["Plans"])

@router.get("/plan", response_model=list[schemas.PlanOut])
def list_plans(db: Session = Depends(get_db)):
    return db.query(models.Plan).all()
