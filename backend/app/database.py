import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sound_machina.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Preset(Base):
    __tablename__ = "presets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    bank = Column(String, default="BANK_A", index=True)
    blueprint_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class BlueprintSnapshot(Base):
    __tablename__ = "blueprint_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(String, unique=True, index=True)
    lineage_name = Column(String, index=True)
    version = Column(Integer, nullable=False)
    parent_preset_id = Column(Integer, nullable=True)
    blueprint_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(String, index=True)
    prompts_json = Column(Text, nullable=False)
    scores_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
