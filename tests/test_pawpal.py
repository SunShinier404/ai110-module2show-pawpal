import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion():
    """Test that mark_complete() sets task as completed."""
    task = Task(name="Feed", description="Feed the pet", duration=10, priority="low")
    assert not task.completed
    task.mark_complete()
    assert task.completed


def test_task_addition():
    """Test that adding a task increases pet's task count."""
    pet = Pet(name="Mocha", species="Dog", age=5)
    initial_count = len(pet.tasks)
    task = Task(
        name="Walk", description="Take Mocha for a walk", duration=20, priority="medium"
    )
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1


def test_filter_tasks_by_completion_status():
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    completed_task = Task(
        name="Feed",
        description="Feed Mocha",
        duration=10,
        priority="low",
        completed=True,
    )
    pending_task = Task(
        name="Walk",
        description="Walk Mocha",
        duration=20,
        priority="medium",
        completed=False,
    )
    pet.add_task(completed_task)
    pet.add_task(pending_task)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())

    completed_tasks = scheduler.filter_tasks_by_completion(True)
    pending_tasks = scheduler.filter_tasks_by_completion(False)

    assert completed_tasks == [completed_task]
    assert pending_tasks == [pending_task]


def test_reschedule_daily_completed_task():
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        name="Walk",
        description="Morning walk",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(9, 0),
        frequency="daily",
        completed=True,
    )
    pet.add_task(task)

    scheduler = Scheduler(owner=owner, date=datetime.date(2026, 3, 31))
    rescheduled = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 3, 31)
    )

    assert len(rescheduled) == 1
    assert rescheduled[0][0] is task
    assert rescheduled[0][1] == datetime.datetime(2026, 4, 1, 9, 0)
    assert task.completed is False


def test_reschedule_weekly_when_day_changes():
    owner = Owner(name="Kim")
    pet = Pet(name="Maple", species="Cat", age=3)
    owner.add_pet(pet)

    task = Task(
        name="Weekly check",
        description="Weekly health check",
        duration=15,
        priority="low",
        scheduled_time=datetime.time(12, 0),
        frequency="weekly",
        completed=False,
    )
    pet.add_task(task)

    scheduler = Scheduler(owner=owner, date=datetime.date(2026, 3, 30))
    rescheduled = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 3, 31)
    )

    assert len(rescheduled) == 1
    assert rescheduled[0][0] is task
    assert rescheduled[0][1] == datetime.datetime(2026, 4, 7, 12, 0)
    assert scheduler.date == datetime.date(2026, 3, 31)


def test_detect_conflicts_same_pet_same_time():
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task1 = Task(
        name="Feed",
        description="Feed Mocha",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(9, 0),
    )
    task2 = Task(
        name="Walk",
        description="Walk Mocha",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(9, 0),
    )
    pet.add_task(task1)
    pet.add_task(task2)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.manage_tasks()

    assert len(scheduler.warnings) == 1
    assert "Conflict at 09:00" in scheduler.warnings[0]
    assert "Feed (Mocha)" in scheduler.warnings[0]
    assert "Walk (Mocha)" in scheduler.warnings[0]


def test_detect_conflicts_different_pets_same_time():
    owner = Owner(name="Kim")
    pet1 = Pet(name="Mocha", species="Dog", age=5)
    pet2 = Pet(name="Maple", species="Cat", age=3)
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    task1 = Task(
        name="Feed",
        description="Feed Mocha",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(12, 0),
    )
    task2 = Task(
        name="Medicine",
        description="Give Maple medicine",
        duration=5,
        priority="high",
        scheduled_time=datetime.time(12, 0),
    )
    pet1.add_task(task1)
    pet2.add_task(task2)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.manage_tasks()

    assert len(scheduler.warnings) == 1
    assert "Conflict at 12:00" in scheduler.warnings[0]
    assert "Feed (Mocha)" in scheduler.warnings[0]
    assert "Medicine (Maple)" in scheduler.warnings[0]
