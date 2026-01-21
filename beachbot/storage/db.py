"""Persistencia em Postgres via SQLAlchemy (sync)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()
engine = create_engine(DATABASE_URL, future=True) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) if engine else None


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    instance_id = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    conversations = relationship("Conversation", back_populates="client")
    __table_args__ = (UniqueConstraint("instance_id", "phone", name="uix_clients_instance_phone"),)


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(Enum("open", "handoff", "closed", name="conversation_status"), default="open", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    last_activity_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    buffer_text = Column(Text, nullable=True)
    buffer_started_at = Column(DateTime(timezone=True), nullable=True)
    buffer_last_at = Column(DateTime(timezone=True), nullable=True)

    client = relationship("Client", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

    __table_args__ = (
        Index("ix_conversations_client_last", "client_id", "last_activity_at"),
    )


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(Enum("user", "assistant", "system", name="message_role"), nullable=False)
    direction = Column(Enum("in", "out", name="message_direction"), nullable=False)
    text = Column(Text, nullable=False)
    ts = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    wa_message_id = Column(String, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        # unicidade apenas quando wa_message_id nao for nulo (ver migration com index parcial)
        Index("ix_messages_conv_ts", "conversation_id", "ts"),
    )


class AulaExperimental(Base):
    __tablename__ = "aula_experimental"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    status = Column(
        Enum("collecting", "scheduled", "cancelled", "expired", "handoff", name="aula_status"),
        default="collecting",
        nullable=False,
    )
    name = Column(String, nullable=True)
    preferred_day = Column(Date, nullable=True)
    preferred_time = Column(Time, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    client = relationship("Client")
    conversation = relationship("Conversation")


def has_engine() -> bool:
    return engine is not None


def get_session():
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL nao configurado; persistencia desabilitada.")
    return SessionLocal()


def get_or_create_client(session, instance_id: Optional[str], phone: str, *, ts: Optional[datetime] = None) -> Client:
    ts = ts or utcnow()
    client: Optional[Client] = (
        session.query(Client)
        .filter(Client.instance_id == instance_id, Client.phone == phone)
        .one_or_none()
    )
    if client:
        client.last_seen_at = ts
        session.add(client)
        session.commit()
        session.refresh(client)
        return client

    client = Client(instance_id=instance_id, phone=phone, created_at=ts, updated_at=ts, last_seen_at=ts)
    session.add(client)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        client = (
            session.query(Client)
            .filter(Client.instance_id == instance_id, Client.phone == phone)
            .one_or_none()
        )
        if client:
            client.last_seen_at = ts
            session.add(client)
            session.commit()
            session.refresh(client)
            return client
        raise
    session.refresh(client)
    return client


def get_or_create_open_conversation(session, client_id: int, *, ts: Optional[datetime] = None) -> Conversation:
    ts = ts or utcnow()
    convo: Optional[Conversation] = (
        session.query(Conversation)
        .filter(Conversation.client_id == client_id, Conversation.status == "open")
        .order_by(Conversation.last_activity_at.desc())
        .first()
    )
    if convo:
        return convo

    convo = Conversation(
        client_id=client_id,
        status="open",
        created_at=ts,
        updated_at=ts,
        last_activity_at=ts,
    )
    session.add(convo)
    session.commit()
    session.refresh(convo)
    return convo


def save_message(
    session,
    conversation_id: int,
    *,
    role: str,
    direction: str,
    text: str,
    ts: Optional[datetime] = None,
    wa_message_id: Optional[str] = None,
) -> Message:
    ts = ts or utcnow()
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        direction=direction,
        text=text,
        ts=ts,
        wa_message_id=wa_message_id,
    )
    session.add(msg)
    # atualiza ultima atividade
    session.query(Conversation).filter(Conversation.id == conversation_id).update(
        {"last_activity_at": ts, "updated_at": utcnow()}
    )
    session.commit()
    session.refresh(msg)
    return msg


def fetch_last_messages(session, conversation_id: int, limit: int = 20) -> list[dict[str, str]]:
    rows = (
        session.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.ts.desc())
        .limit(limit)
        .all()
    )
    messages = [{"role": m.role, "content": m.text} for m in reversed(rows)]
    return messages


def touch_client_last_seen(session, client_id: int, ts: Optional[datetime] = None) -> None:
    ts = ts or utcnow()
    session.query(Client).filter(Client.id == client_id).update({"last_seen_at": ts, "updated_at": utcnow()})
    session.commit()


def create_aula_experimental(*args: Any, **kwargs: Any) -> None:
    # stub para futuras implementacoes
    return None


def update_aula_experimental_status(*args: Any, **kwargs: Any) -> None:
    # stub para futuras implementacoes
    return None
