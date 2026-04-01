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

# Add at least three Tasks with different times to those pets
task1 = Task(
    name="Walk", description="Take Mocha for a walk", scheduled_time=datetime.time(9, 0)
)
task2 = Task(name="Feed", description="Feed Maple", scheduled_time=datetime.time(12, 0))
task3 = Task(
    name="Groom", description="Groom Mocha", scheduled_time=datetime.time(18, 0)
)

# Assign tasks to pets
pet1.add_task(task1)
pet2.add_task(task2)
pet1.add_task(task3)

# Create the scheduler for today
scheduler = Scheduler(owner=owner, date=datetime.date.today())

# Print today's schedule
print("Today's Schedule:")
scheduler.print_schedule()
