from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    body_part = Column(String, nullable=True)

    workout_sets = relationship("WorkoutSet", back_populates="exercise")


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    trained_at = Column(DateTime, default=datetime.utcnow)
    note = Column(String, nullable=True)

    sets = relationship(
        "WorkoutSet",
        back_populates="workout",
        cascade="all, delete-orphan",
    )


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)

    weight = Column(Float, nullable=False)
    reps = Column(Integer, nullable=False)
    set_order = Column(Integer, nullable=False)

    workout = relationship("Workout", back_populates="sets")
    exercise = relationship("Exercise", back_populates="workout_sets")
