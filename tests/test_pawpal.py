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


# ============================================================================
# SORTING EDGE CASE TESTS
# ============================================================================


def test_sort_none_time_vs_scheduled_time():
    """Verify that tasks with None scheduled_time sort consistently."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task_unscheduled = Task(
        name="Play",
        description="Free play",
        duration=15,
        priority="low",
        scheduled_time=None,
    )
    task_with_time = Task(
        name="Walk",
        description="Morning walk",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(9, 0),
    )
    pet.add_task(task_unscheduled)
    pet.add_task(task_with_time)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.sort_by_scheduled_time()

    # Tasks with None time should sort first (00:00)
    assert len(scheduler.scheduled_tasks) == 2
    assert scheduler.scheduled_tasks[0].scheduled_time is None
    assert scheduler.scheduled_tasks[1].scheduled_time == datetime.time(9, 0)


def test_sort_multiple_none_times():
    """Verify multiple tasks with None time handle secondary sort (pet name)."""
    owner = Owner(name="Kim")
    pet1 = Pet(name="Alpha", species="Dog", age=5)
    pet2 = Pet(name="Beta", species="Cat", age=3)
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    task1 = Task(
        name="Task1",
        description="Task for Alpha",
        duration=10,
        priority="low",
        scheduled_time=None,
    )
    task2 = Task(
        name="Task2",
        description="Task for Beta",
        duration=10,
        priority="low",
        scheduled_time=None,
    )
    pet1.add_task(task1)
    pet2.add_task(task2)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.sort_by_scheduled_time()

    # Both have None time, so secondary sort by pet name should apply
    assert len(scheduler.scheduled_tasks) == 2
    assert scheduler.scheduled_tasks[0].pet.name == "Alpha"
    assert scheduler.scheduled_tasks[1].pet.name == "Beta"


def test_sort_boundary_times():
    """Test sorting with boundary times (00:00 and 23:59)."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task_midnight = Task(
        name="Midnight",
        description="Midnight task",
        duration=5,
        priority="low",
        scheduled_time=datetime.time(0, 0),
    )
    task_late = Task(
        name="Late night",
        description="Late night task",
        duration=5,
        priority="low",
        scheduled_time=datetime.time(23, 59),
    )
    task_morning = Task(
        name="Morning",
        description="Morning task",
        duration=5,
        priority="low",
        scheduled_time=datetime.time(8, 0),
    )
    pet.add_task(task_late)
    pet.add_task(task_morning)
    pet.add_task(task_midnight)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.sort_by_scheduled_time()

    assert scheduler.scheduled_tasks[0].scheduled_time == datetime.time(0, 0)
    assert scheduler.scheduled_tasks[1].scheduled_time == datetime.time(8, 0)
    assert scheduler.scheduled_tasks[2].scheduled_time == datetime.time(23, 59)


def test_sort_all_tasks_with_none_time():
    """Verify schedule handles all tasks with None time without crash."""
    owner = Owner(name="Kim")
    pet1 = Pet(name="Mocha", species="Dog", age=5)
    pet2 = Pet(name="Maple", species="Cat", age=3)
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    task1 = Task(name="Task1", description="Task1", duration=10, priority="low")
    task2 = Task(name="Task2", description="Task2", duration=10, priority="low")
    pet1.add_task(task1)
    pet2.add_task(task2)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.sort_by_scheduled_time()

    assert len(scheduler.scheduled_tasks) == 2
    assert all(t.scheduled_time is None for t in scheduler.scheduled_tasks)


def test_sort_chronological_order():
    """Verify multiple tasks sort in strictly ascending time order."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    times = [
        datetime.time(22, 30),
        datetime.time(8, 0),
        datetime.time(14, 15),
        datetime.time(12, 0),
        datetime.time(6, 30),
    ]
    for i, time in enumerate(times):
        task = Task(
            name=f"Task{i}",
            description=f"Task at {time}",
            duration=10,
            priority="low",
            scheduled_time=time,
        )
        pet.add_task(task)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.sort_by_scheduled_time()

    sorted_times = [t.scheduled_time for t in scheduler.scheduled_tasks]
    assert sorted_times == sorted(times)


def test_sort_same_time_secondary_pet_sort():
    """Verify secondary sort by pet name when times are identical."""
    owner = Owner(name="Kim")
    pet_zebra = Pet(name="Zebra", species="Dog", age=5)
    pet_apple = Pet(name="Apple", species="Cat", age=3)
    owner.add_pet(pet_zebra)
    owner.add_pet(pet_apple)

    task1 = Task(
        name="Task1",
        description="Task for Zebra",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(10, 0),
    )
    task2 = Task(
        name="Task2",
        description="Task for Apple",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(10, 0),
    )
    pet_zebra.add_task(task1)
    pet_apple.add_task(task2)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.sort_by_scheduled_time()

    assert len(scheduler.scheduled_tasks) == 2
    assert scheduler.scheduled_tasks[0].pet.name == "Apple"
    assert scheduler.scheduled_tasks[1].pet.name == "Zebra"


# ============================================================================
# RECURRING TASK EDGE CASE TESTS
# ============================================================================


def test_non_recurring_task_not_rescheduled():
    """Verify non-recurring task (frequency=None) is NOT rescheduled even if completed."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        name="One-time task",
        description="Only once",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(9, 0),
        frequency=None,
        completed=True,
    )
    pet.add_task(task)

    scheduler = Scheduler(owner=owner, date=datetime.date(2026, 3, 31))
    rescheduled = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 3, 31)
    )

    assert len(rescheduled) == 0
    assert task.completed is True  # Should remain completed


def test_recurring_task_without_scheduled_time():
    """Verify recurring task without scheduled_time is safely skipped."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        name="Recurring no time",
        description="Daily but no time set",
        duration=20,
        priority="medium",
        scheduled_time=None,
        frequency="daily",
        completed=True,
    )
    pet.add_task(task)

    scheduler = Scheduler(owner=owner, date=datetime.date(2026, 3, 31))
    rescheduled = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 3, 31)
    )

    assert len(rescheduled) == 0


def test_completed_task_rescheduled_multiple_times():
    """Verify a rescheduled task can be rescheduled again if completed."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        name="Walk",
        description="Daily walk",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(9, 0),
        frequency="daily",
        completed=True,
    )
    pet.add_task(task)

    scheduler = Scheduler(owner=owner, date=datetime.date(2026, 3, 31))

    # First reschedule
    rescheduled1 = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 3, 31)
    )
    assert len(rescheduled1) == 1
    assert rescheduled1[0][1] == datetime.datetime(2026, 4, 1, 9, 0)
    assert task.completed is False

    # Mark complete again and reschedule
    task.mark_complete()
    rescheduled2 = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 4, 1)
    )
    assert len(rescheduled2) == 1
    assert rescheduled2[0][1] == datetime.datetime(2026, 4, 2, 9, 0)


def test_weekly_task_crosses_month_boundary():
    """Verify weekly task correctly crosses month boundary."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        name="Weekly bath",
        description="Weekly grooming",
        duration=30,
        priority="medium",
        scheduled_time=datetime.time(14, 0),
        frequency="weekly",
        completed=False,
    )
    pet.add_task(task)

    # March 30, 2026 -> April 7, 2026 (crosses month, day_changed adds 7 days)
    scheduler = Scheduler(owner=owner, date=datetime.date(2026, 3, 30))
    rescheduled = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 3, 31)
    )

    assert len(rescheduled) == 1
    assert rescheduled[0][1] == datetime.datetime(2026, 4, 7, 14, 0)


def test_weekly_task_crosses_year_boundary():
    """Verify weekly task correctly crosses year boundary."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        name="Weekly task",
        description="Year-crossing task",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(12, 0),
        frequency="weekly",
        completed=False,
    )
    pet.add_task(task)

    # Dec 28, 2025 -> Jan 5, 2026 (crosses year, day_changed adds 7 days)
    scheduler = Scheduler(owner=owner, date=datetime.date(2025, 12, 28))
    rescheduled = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2025, 12, 29)
    )

    assert len(rescheduled) == 1
    assert rescheduled[0][1] == datetime.datetime(2026, 1, 5, 12, 0)


def test_invalid_frequency_not_rescheduled():
    """Verify invalid frequency strings are safely ignored."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        name="Invalid freq",
        description="Task with invalid frequency",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(9, 0),
        frequency="monthly",  # Not supported, only 'daily' and 'weekly'
        completed=True,
    )
    pet.add_task(task)

    scheduler = Scheduler(owner=owner, date=datetime.date(2026, 3, 31))
    rescheduled = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 3, 31)
    )

    assert len(rescheduled) == 0


def test_scheduler_date_does_not_move_backward():
    """Verify recurring task does not reschedule when date moves backward."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task = Task(
        name="Walk",
        description="Daily walk",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(9, 0),
        frequency="daily",
        completed=False,
    )
    pet.add_task(task)

    scheduler = Scheduler(owner=owner, date=datetime.date(2026, 4, 1))
    # Try to move date backward
    rescheduled = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 3, 31)
    )

    # Should not reschedule because date did not move forward
    assert len(rescheduled) == 0
    assert task.completed is False


def test_multiple_daily_tasks_all_reschedule():
    """Verify multiple daily tasks all reschedule when completed."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task1 = Task(
        name="Morning walk",
        description="Walk",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(7, 0),
        frequency="daily",
        completed=True,
    )
    task2 = Task(
        name="Evening walk",
        description="Walk",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(18, 0),
        frequency="daily",
        completed=True,
    )
    pet.add_task(task1)
    pet.add_task(task2)

    scheduler = Scheduler(owner=owner, date=datetime.date(2026, 3, 31))
    rescheduled = scheduler.reschedule_recurring_tasks(
        current_date=datetime.date(2026, 3, 31)
    )

    assert len(rescheduled) == 2
    assert rescheduled[0][1] == datetime.datetime(2026, 4, 1, 7, 0)
    assert rescheduled[1][1] == datetime.datetime(2026, 4, 1, 18, 0)


# ============================================================================
# CONFLICT DETECTION EDGE CASE TESTS
# ============================================================================


def test_detect_conflicts_three_tasks_same_time():
    """Verify 3+ tasks at same time are all listed in a single warning."""
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
    task3 = Task(
        name="Play",
        description="Play with Mocha",
        duration=15,
        priority="low",
        scheduled_time=datetime.time(9, 0),
    )
    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.manage_tasks()

    # Should be exactly one warning with all three tasks
    assert len(scheduler.warnings) == 1
    assert "Conflict at 09:00" in scheduler.warnings[0]
    assert "Feed (Mocha)" in scheduler.warnings[0]
    assert "Walk (Mocha)" in scheduler.warnings[0]
    assert "Play (Mocha)" in scheduler.warnings[0]


def test_detect_no_conflicts_all_none_times():
    """Verify no conflicts reported when all tasks have None time."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task1 = Task(name="Task1", description="Task1", duration=10, priority="low")
    task2 = Task(name="Task2", description="Task2", duration=10, priority="low")
    task3 = Task(name="Task3", description="Task3", duration=10, priority="low")
    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.manage_tasks()

    assert len(scheduler.warnings) == 0


def test_detect_conflicts_mixed_none_and_times():
    """Verify conflicts detected only for scheduled times, ignoring None times."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task_no_time = Task(
        name="No time",
        description="Flexible task",
        duration=10,
        priority="low",
        scheduled_time=None,
    )
    task1_conflict = Task(
        name="Feed",
        description="Feed Mocha",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(9, 0),
    )
    task2_conflict = Task(
        name="Walk",
        description="Walk Mocha",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(9, 0),
    )
    pet.add_task(task_no_time)
    pet.add_task(task1_conflict)
    pet.add_task(task2_conflict)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.manage_tasks()

    # Only the two scheduled tasks at 9:00 should create a conflict
    assert len(scheduler.warnings) == 1
    assert "Feed (Mocha)" in scheduler.warnings[0]
    assert "Walk (Mocha)" in scheduler.warnings[0]


def test_detect_conflicts_multiple_different_times():
    """Verify multiple conflicts at different times are all reported."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task1 = Task(
        name="Feed1",
        description="Feed Mocha",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(9, 0),
    )
    task2 = Task(
        name="Walk1",
        description="Walk Mocha",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(9, 0),
    )
    task3 = Task(
        name="Feed2",
        description="Feed Mocha again",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(18, 0),
    )
    task4 = Task(
        name="Walk2",
        description="Walk Mocha again",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(18, 0),
    )
    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)
    pet.add_task(task4)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.manage_tasks()

    # Should have two warnings, one for each conflict time
    assert len(scheduler.warnings) == 2
    conflict_times = [
        w for w in scheduler.warnings if "09:00" in w or "18:00" in w
    ]
    assert len(conflict_times) == 2


def test_detect_conflicts_across_multiple_pets():
    """Verify conflicts detected across different pets at same time."""
    owner = Owner(name="Kim")
    pet1 = Pet(name="Mocha", species="Dog", age=5)
    pet2 = Pet(name="Maple", species="Cat", age=3)
    pet3 = Pet(name="Buddy", species="Dog", age=7)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    owner.add_pet(pet3)

    task1 = Task(
        name="Feed1",
        description="Feed Mocha",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(9, 0),
    )
    task2 = Task(
        name="Feed2",
        description="Feed Maple",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(9, 0),
    )
    task3 = Task(
        name="Feed3",
        description="Feed Buddy",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(9, 0),
    )
    pet1.add_task(task1)
    pet2.add_task(task2)
    pet3.add_task(task3)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.manage_tasks()

    assert len(scheduler.warnings) == 1
    assert "Conflict at 09:00" in scheduler.warnings[0]
    assert "Feed1 (Mocha)" in scheduler.warnings[0]
    assert "Feed2 (Maple)" in scheduler.warnings[0]
    assert "Feed3 (Buddy)" in scheduler.warnings[0]


def test_completed_task_does_not_affect_conflict():
    """Verify completed tasks are still included in conflict detection."""
    owner = Owner(name="Kim")
    pet = Pet(name="Mocha", species="Dog", age=5)
    owner.add_pet(pet)

    task_completed = Task(
        name="Feed",
        description="Feed Mocha",
        duration=10,
        priority="low",
        scheduled_time=datetime.time(9, 0),
        completed=True,
    )
    task_pending = Task(
        name="Walk",
        description="Walk Mocha",
        duration=20,
        priority="medium",
        scheduled_time=datetime.time(9, 0),
        completed=False,
    )
    pet.add_task(task_completed)
    pet.add_task(task_pending)

    scheduler = Scheduler(owner=owner, date=datetime.date.today())
    scheduler.manage_tasks()

    # Completed task should still be detected as conflict
    assert len(scheduler.warnings) == 1
    assert "Conflict at 09:00" in scheduler.warnings[0]
