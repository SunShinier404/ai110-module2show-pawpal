from dataclasses import dataclass, field
from typing import List, Optional
import datetime


@dataclass
class Task:
    name: str
    description: str
    duration: int  # in minutes
    priority: str  # e.g., 'low', 'medium', 'high'
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
    warnings: List[str] = field(default_factory=list)

    def retrieve_tasks(self) -> List[Task]:
        return self.owner.get_all_tasks()

    def filter_tasks_by_completion(self, completed: bool) -> List[Task]:
        return [task for task in self.retrieve_tasks() if task.completed is completed]

    def sort_by_scheduled_time(self):
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
        """Prepare the daily schedule, populate conflict warnings, and update summary text."""
        self.sort_by_scheduled_time()
        self.warnings = self.detect_conflicts()
        self.generate_explanation()

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for tasks that share the same non-null scheduled time."""
        warnings: List[str] = []
        tasks_by_time: dict[datetime.time, List[Task]] = {}

        for task in self.scheduled_tasks:
            if task.scheduled_time is None:
                continue
            tasks_by_time.setdefault(task.scheduled_time, []).append(task)

        for conflict_time, tasks in tasks_by_time.items():
            if len(tasks) < 2:
                continue

            task_details = []
            for task in tasks:
                pet_name = task.pet.name if task.pet else "Unknown pet"
                task_details.append(f"{task.name} ({pet_name})")

            warning = f"Conflict at {conflict_time.strftime('%H:%M')}: " + ", ".join(
                task_details
            )
            warnings.append(warning)

        return warnings

    def generate_explanation(self):
        """Build a human-readable summary of the schedule and any detected conflicts."""
        conflict_note = ""
        if self.warnings:
            conflict_note = f" Detected {len(self.warnings)} scheduling conflict(s)."
        self.explanation = (
            f"Scheduled {len(self.scheduled_tasks)} tasks for {self.owner.name} on {self.date}."
            f"{conflict_note}"
        )

    def print_schedule(self):
        """Print the sorted schedule, then print non-fatal conflict warnings and summary."""
        self.manage_tasks()
        print(f"Today's Schedule for {self.owner.name} on {self.date}:")
        for task in self.scheduled_tasks:
            time_str = (
                task.scheduled_time.strftime("%H:%M")
                if task.scheduled_time
                else "No time set"
            )
            pet_name = task.pet.name if task.pet else "No pet"
            status = "Completed" if task.completed else "Pending"
            print(f"- {time_str}: {task.description} (Pet: {pet_name}) [{status}]")
        for warning in self.warnings:
            print(f"Warning: {warning}")
        if self.explanation:
            print(self.explanation)

    def clear_schedule(self):
        """Clear the computed schedule list."""
        self.scheduled_tasks.clear()

    # Reschedule recurring tasks when complete or when the scheduler date advances.
    def reschedule_recurring_tasks(
        self, current_date: Optional[datetime.date] = None
    ) -> List[tuple[Task, datetime.datetime]]:
        """Return next-run datetimes for daily/weekly tasks that should be advanced.

        A task is advanced when it is marked complete, or when the scheduler date has
        moved forward. Rescheduled tasks are marked incomplete so they can appear in
        future schedules.
        """
        effective_date = current_date or datetime.date.today()
        day_changed = effective_date > self.date
        rescheduled: List[tuple[Task, datetime.datetime]] = []

        for task in self.retrieve_tasks():
            if task.frequency not in ("daily", "weekly"):
                continue
            if task.scheduled_time is None:
                continue

            should_reschedule = task.completed or day_changed
            if not should_reschedule:
                continue

            interval_days = 1 if task.frequency == "daily" else 7
            base_date = effective_date if day_changed else self.date
            next_run = datetime.datetime.combine(
                base_date, task.scheduled_time
            ) + datetime.timedelta(days=interval_days)

            task.mark_incomplete()
            rescheduled.append((task, next_run))

        if day_changed:
            self.date = effective_date

        return rescheduled
