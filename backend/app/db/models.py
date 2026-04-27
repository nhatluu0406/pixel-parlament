from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

# Association table for Agent-Skill relationship
agent_skill_association = Table(
    'agent_skill', Base.metadata,
    Column('agent_id', Integer, ForeignKey('agents.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sprite_id = Column(String)  # Identifier for the pixel art sprite sheet
    role = Column(String)       # Role description
    status = Column(String, default="idle")  # Current state (idle, working, thinking)

    skills = relationship("Skill", secondary=agent_skill_association, back_populates="agents")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    agents = relationship("Agent", secondary=agent_skill_association, back_populates="skills")
