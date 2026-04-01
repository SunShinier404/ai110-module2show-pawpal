from pawpal_system import Task, Pet


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
    task = Task(name="Walk", description="Take Mocha for a walk", duration=20, priority="medium")
    pet.add_task(task)
    assert len(pet.tasks) == initial_count + 1
