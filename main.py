import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# Create an owner
owner = Owner(name="Gree")

# Create 2 pets
pet1 = Pet(name="Mocha", species="Dog", age=5)
pet2 = Pet(name="Maple", species="Cat", age=3)

# Add pets to owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Add tasks with times out of order
task1 = Task(
    name="Groom",
    description="Groom Mocha",
    duration=30,
    priority="high",
    scheduled_time=datetime.time(18, 0),
)
task2 = Task(
    name="Walk",
    description="Take Mocha for a walk",
    duration=20,
    priority="medium",
    scheduled_time=datetime.time(18, 0),
)
task3 = Task(
    name="Feed",
    description="Feed Maple",
    duration=10,
    priority="low",
    scheduled_time=datetime.time(9, 0),
)
task4 = Task(
    name="Medicine", description="Give Maple medicine", duration=5, priority="high"
)

# Mark one task as complete so filtering has both states
task4.mark_complete()

# Assign tasks to pets in a non-chronological insertion order
pet1.add_task(task1)
pet2.add_task(task4)
pet2.add_task(task3)
pet1.add_task(task2)

# Create the scheduler for today
scheduler = Scheduler(owner=owner, date=datetime.date.today())

# Print schedule and include conflict warnings if detected
# print("Today's Schedule (sorted by time):")
scheduler.print_schedule()

# Print filtered views using the new completion filter
print("\nCompleted tasks:")
for task in scheduler.filter_tasks_by_completion(True):
    pet_name = task.pet.name if task.pet else "No pet"
    print(f"- {task.description} ({pet_name})")

print("\nPending tasks:")
for task in scheduler.filter_tasks_by_completion(False):
    pet_name = task.pet.name if task.pet else "No pet"
    print(f"- {task.description} ({pet_name})")
