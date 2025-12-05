from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/invoice", tags=["Invoices"])

def _check_subscription_access(
    sub: models.Subscription,
    current_user: CurrentUser,
):
    if sub.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

@router.post("", response_model=schemas.InvoiceOut, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    sub = (
        db.query(models.Subscription)
        .filter(models.Subscription.id == payload.subscription_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    _check_subscription_access(sub, current_user)

    invoice = models.Invoice(
        amount=payload.amount,
        subscription_id=payload.subscription_id,
        date=payload.date,  # si es None, el modelo pone utcnow
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("", response_model=list[schemas.InvoiceOut])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # facturas solo de las subs del usuario actual
    invoices = (
        db.query(models.Invoice)
        .join(models.Subscription)
        .filter(models.Subscription.user_id == current_user.id)
        .all()
    )
    return invoices

@router.get("/{invoice_id}", response_model=schemas.InvoiceOut)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    sub = (
        db.query(models.Subscription)
        .filter(models.Subscription.id == invoice.subscription_id)
        .first()
    )
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    _check_subscription_access(sub, current_user)
    return invoice
