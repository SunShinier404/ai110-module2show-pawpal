from dataclasses import dataclass, field
from typing import List, Optional
import datetime


@dataclass
class Task:
    name: str
    description: str
    scheduled_time: Optional[datetime.time] = None
    frequency: Optional[str] = None  # e.g., 'daily', 'weekly'
    completed: bool = False
    pet: Optional["Pet"] = None

    def mark_complete(self):
        self.completed = True

    def mark_incomplete(self):
        self.completed = False


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        task.pet = self
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        return self.tasks


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    preferences: Optional[dict] = field(default_factory=dict)

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


@dataclass
class Scheduler:
    owner: Owner
    date: datetime.date
    scheduled_tasks: List[Task] = field(default_factory=list)
    explanation: Optional[str] = None

    def retrieve_tasks(self) -> List[Task]:
        return self.owner.get_all_tasks()

    def organize_tasks(self):
        # Example: sort by scheduled_time, then by pet name
        tasks = self.retrieve_tasks()
        self.scheduled_tasks = sorted(
            tasks,
            key=lambda t: (
                t.scheduled_time or datetime.time(0, 0),
                t.pet.name if t.pet else "",
            ),
        )

    def manage_tasks(self):
        # Placeholder for more advanced management logic
        self.organize_tasks()
        self.generate_explanation()

    def generate_explanation(self):
        self.explanation = f"Scheduled {len(self.scheduled_tasks)} tasks for {self.owner.name} on {self.date}."

    def print_schedule(self):
        self.manage_tasks()
        print(f"Today's Schedule for {self.owner.name} on {self.date}:")
        for task in self.scheduled_tasks:
            time_str = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "No time set"
            pet_name = task.pet.name if task.pet else "No pet"
            status = "Completed" if task.completed else "Pending"
            print(f"- {time_str}: {task.description} (Pet: {pet_name}) [{status}]")
        if self.explanation:
            print(self.explanation)
