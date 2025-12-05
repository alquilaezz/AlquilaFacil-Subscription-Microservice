from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_current_user, CurrentUser

router = APIRouter(prefix="/api/v1/subscriptions", tags=["Subscriptions"])

def get_default_status_id(db: Session) -> int:
    """Obtiene (o crea) el status 'PENDING'."""
    status_obj = (
        db.query(models.SubscriptionStatus)
        .filter(models.SubscriptionStatus.status == "PENDING")
        .first()
    )
    if not status_obj:
        status_obj = models.SubscriptionStatus(status="PENDING")
        db.add(status_obj)
        db.flush()
    return status_obj.id

@router.post("", response_model=schemas.SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription(
    payload: schemas.SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    status_id = payload.subscription_status_id or get_default_status_id(db)

    subscription = models.Subscription(
        user_id=current_user.id,
        plan_id=payload.plan_id,
        subscription_status_id=status_id,
        voucher_image_url=payload.voucher_image_url,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription

@router.get("", response_model=list[schemas.SubscriptionOut])
def list_subscriptions(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    user_id: Optional[int] = None,
):
    query = db.query(models.Subscription)

    # si envían user_id, solo admin puede ver otros
    if user_id is not None:
        if current_user.role != "ADMIN" and user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        query = query.filter(models.Subscription.user_id == user_id)
    else:
        query = query.filter(models.Subscription.user_id == current_user.id)

    return query.all()

@router.get("/{subscription_id}", response_model=schemas.SubscriptionOut)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    sub = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return sub

@router.put("/{subscription_id}", response_model=schemas.SubscriptionOut)
def update_subscription(
    subscription_id: int,
    payload: schemas.SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    sub = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if sub.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if payload.plan_id is not None:
        sub.plan_id = payload.plan_id
    if payload.voucher_image_url is not None:
        sub.voucher_image_url = payload.voucher_image_url
    if payload.subscription_status_id is not None:
        sub.subscription_status_id = payload.subscription_status_id

    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub
