from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Integer


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Поля для работы с темами в супергруппе
    topic_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pinned_message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Реферальная система
    referrer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    referral_code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)  # Уникальный реферальный код
    
    # UTM метки
    utm_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Источник трафика

    payments: Mapped[list["Payment"]] = relationship(back_populates="user")


class PaymentPlan(Base):
    __tablename__ = "payment_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    price_total: Mapped[int] = mapped_column(Integer, nullable=False)
    months: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 = единовременная оплата

    payments: Mapped[list["Payment"]] = relationship(back_populates="plan")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("payment_plans.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, paid, cancelled
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # Дата когда нужно платить

    user: Mapped["User"] = relationship(back_populates="payments")
    plan: Mapped["PaymentPlan"] = relationship(back_populates="payments")
