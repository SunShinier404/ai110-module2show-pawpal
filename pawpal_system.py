from dataclasses import dataclass, field
from typing import List, Optional
import datetime


@dataclass
class Task:
    name: str
    duration: int  # in minutes
    priority: int  # 1 = highest
    description: Optional[str] = None
    scheduled_time: Optional[datetime.time] = None
    pet: Optional["Pet"] = None  # Reference to the pet this task is for
    owner: Optional["Owner"] = None  # Reference to the owner responsible for this task


@dataclass
class Pet:
    name: str
    species: str
    age: int
    owners: List["Owner"] = field(default_factory=list)  # Reference to the owner
    tasks: List[Task] = field(default_factory=list)


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    preferences: Optional[dict] = field(default_factory=dict)

    def add_pet(self, pet: "Pet"):
        pet.owners.append(self)
        self.pets.append(pet)


@dataclass

# Scheduler class to generate daily plans for an owner and their pets
@dataclass
class Scheduler:
    owner: Owner
    date: datetime.date
    scheduled_tasks: List[Task] = field(default_factory=list)
    explanation: Optional[str] = None

    def generate_schedule(self):
        # Placeholder for scheduling logic
        self.scheduled_tasks = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                self.scheduled_tasks.append(task)
        self.generate_explanation()

    def generate_explanation(self):
        # Placeholder for explanation logic
        self.explanation = "Schedule generated based on priorities, owner preferences, and constraints."
