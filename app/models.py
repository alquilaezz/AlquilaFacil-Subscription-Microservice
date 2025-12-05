from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from .database import Base

class SubscriptionStatus(Base):
    __tablename__ = "subscription_statuses"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Text, nullable=False, unique=True)

    subscriptions = relationship("Subscription", back_populates="status")

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    service = Column(Text, nullable=False)
    price = Column(Float, nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # referencia a users del IAM (sin FK real)
    subscription_status_id = Column(
        Integer,
        ForeignKey("subscription_statuses.id"),
        nullable=False,
    )
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    voucher_image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    status = relationship("SubscriptionStatus", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
        nullable=False,
    )

    subscription = relationship("Subscription", back_populates="invoices")
