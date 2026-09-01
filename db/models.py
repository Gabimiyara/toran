from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Duty(Base):
    __tablename__ = "duties"

    id = Column(String(100), primary_key=True)
    name = Column(String(100), nullable=False)


class SystemState(Base):
    __tablename__ = "system_state"

    id = Column(String(100), primary_key=True)
    current_duty_id = Column(
        String(100),
        ForeignKey("duties.id"),
        nullable=True
    )

    current_duty = relationship("Duty")