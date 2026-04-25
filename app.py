import streamlit as st
import datetime
from pawpal_system import Owner, Pet, Task, Scheduler


def get_conflict_groups(tasks):
    """Group scheduled tasks by time and return only groups with conflicts."""
    grouped = {}
    for task in tasks:
        if task.scheduled_time is None:
            continue
        grouped.setdefault(task.scheduled_time, []).append(task)
    return {time: grouped[time] for time in grouped if len(grouped[time]) > 1}


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")

# --- MULTI-OWNER & MULTI-PET SUPPORT ---
owner_name = st.text_input("Owner name", value="Jordan", key="owner_name_input")
pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
species = st.selectbox("Species", ["dog", "cat", "other"], key="species_input")
age = st.number_input("Age", min_value=0, max_value=30, value=5, key="age_input")

# Initialize session state for owners
if "owners" not in st.session_state:
    st.session_state.owners = []  # List of Owner objects

if st.button("Add owner and pet"):
    # Check if owner already exists
    owner = next((o for o in st.session_state.owners if o.name == owner_name), None)
    if not owner:
        owner = Owner(name=owner_name)
        st.session_state.owners.append(owner)
    # Check if pet already exists for this owner
    pet = next((p for p in owner.pets if p.name == pet_name), None)
    if not pet:
        pet = Pet(name=pet_name, species=species, age=age)
        owner.add_pet(pet)
    st.success(f"Added/updated owner '{owner_name}' with pet '{pet_name}'.")


st.markdown("### Tasks")
st.caption(
    "Add a few tasks. In your final version, these should feed into your scheduler."
)


# --- OWNER & PET SELECTION ---
owners = st.session_state.get("owners", [])
selected_owner = None
selected_pet = None
if owners:
    owner_names = [o.name for o in owners]
    selected_owner_name = st.selectbox("Select owner", owner_names, key="select_owner")
    selected_owner = next((o for o in owners if o.name == selected_owner_name), None)
    if selected_owner and selected_owner.pets:
        pet_names = [p.name for p in selected_owner.pets]
        selected_pet_name = st.selectbox("Select pet", pet_names, key="select_pet")
        selected_pet = next(
            (p for p in selected_owner.pets if p.name == selected_pet_name), None
        )
    else:
        st.info("No pets for this owner. Add a pet above.")
else:
    st.info("No owners or pets available. Add an owner and pet above.")

# Owner session state
# if "owner" not in st.session_state:
#     st.session_state.owner = Owner(name=owner_name)

# # Pet session state
# if "pet" not in st.session_state:
#     st.session_state.pet = Pet(name=pet_name, species=species, age=age)

# # Add pet to owner if not already added
# if st.session_state.pet not in st.session_state.owner.pets:
#     st.session_state.owner.add_pet(st.session_state.pet)

# # Tasks session state (store tasks for the current pet)
# if "tasks" not in st.session_state:
#     st.session_state.tasks = st.session_state.pet.tasks

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_description = st.text_input("Task description", value="Take Mochi for a walk")
with col3:
    duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=240, value=20
    )
with col4:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col5, col6 = st.columns(2)
with col5:
    task_date = st.date_input(
        "Task date", value=datetime.date.today(), key="task_date_input"
    )
with col6:
    task_time = st.time_input(
        "Task time", value=datetime.time(9, 0), key="task_time_input"
    )


# Only allow adding a task if an owner and pet are selected

if st.button("Add task"):
    if selected_pet:
        new_task = Task(
            name=task_title,
            description=task_description,
            duration=duration,
            priority=priority,
            scheduled_time=task_time,
        )
        selected_pet.add_task(new_task)
        st.success(
            f"Task '{task_title}' added to pet '{selected_pet.name}' at {task_time.strftime('%H:%M')} on {task_date}."
        )
    else:
        st.warning("Please select a pet to add the task.")


# Show tasks for the selected pet

if selected_pet and selected_pet.tasks:
    st.write(f"Current tasks for {selected_pet.name}:")
    st.table(
        [
            {
                "Task": t.name,
                "Description": t.description,
                "Time": (
                    t.scheduled_time.strftime("%H:%M")
                    if t.scheduled_time
                    else "Unscheduled"
                ),
                "Duration (minutes)": getattr(t, "duration", ""),
                "Priority": getattr(t, "priority", ""),
            }
            for t in selected_pet.tasks
        ]
    )
elif selected_pet:
    st.info(f"No tasks yet for {selected_pet.name}. Add one above.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if "show_schedule" not in st.session_state:
    st.session_state.show_schedule = False

if st.button("Generate schedule"):
    st.session_state.show_schedule = True

if st.session_state.show_schedule:
    if not selected_owner:
        st.warning("Please select an owner to generate a schedule.")
    elif not selected_owner.pets or sum(len(p.tasks) for p in selected_owner.pets) == 0:
        st.warning("Please add at least one pet with tasks to generate a schedule.")
    else:
        # Create scheduler and manage tasks
        scheduler = Scheduler(owner=selected_owner, date=datetime.date.today())
        scheduler.manage_tasks()

        # Display summary
        st.success(scheduler.explanation)

        # Display warnings if any
        if scheduler.warnings:
            st.warning("⚠️ **Scheduling Conflicts Detected**")
            for warning in scheduler.warnings:
                st.write(f"- {warning}")

            st.markdown("### Resolve Conflicts")
            st.caption(
                "Edit or remove conflicting tasks below. After saving/removing, the page will refresh with an updated schedule."
            )

            conflict_groups = get_conflict_groups(scheduler.scheduled_tasks)
            priority_options = ["low", "medium", "high"]

            for conflict_time in sorted(conflict_groups):
                conflict_tasks = conflict_groups[conflict_time]
                time_label = conflict_time.strftime("%H:%M")
                with st.expander(
                    f"Conflict at {time_label} ({len(conflict_tasks)} tasks)",
                    expanded=True,
                ):
                    for task in conflict_tasks:
                        pet_name = task.pet.name if task.pet else "Unknown"
                        st.markdown(f"**{task.name} ({pet_name})**")

                        current_priority = (
                            task.priority
                            if task.priority in priority_options
                            else "low"
                        )

                        with st.form(key=f"conflict_form_{id(task)}"):
                            edited_name = st.text_input(
                                "Task title",
                                value=task.name,
                                key=f"edit_name_{id(task)}",
                            )
                            edited_description = st.text_input(
                                "Task description",
                                value=task.description,
                                key=f"edit_description_{id(task)}",
                            )

                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                edited_duration = st.number_input(
                                    "Duration (minutes)",
                                    min_value=1,
                                    max_value=240,
                                    value=int(task.duration),
                                    key=f"edit_duration_{id(task)}",
                                )
                            with col_b:
                                edited_priority = st.selectbox(
                                    "Priority",
                                    priority_options,
                                    index=priority_options.index(current_priority),
                                    key=f"edit_priority_{id(task)}",
                                )
                            with col_c:
                                edited_time = st.time_input(
                                    "Task time",
                                    value=task.scheduled_time,
                                    key=f"edit_time_{id(task)}",
                                )

                            save_clicked = st.form_submit_button("Save edits")
                            remove_clicked = st.form_submit_button("Remove task")

                        if save_clicked:
                            task.name = edited_name.strip() or task.name
                            task.description = edited_description.strip()
                            task.duration = int(edited_duration)
                            task.priority = edited_priority
                            task.scheduled_time = edited_time
                            st.success(
                                f"Updated '{task.name}' for {pet_name}. Rebuilding schedule..."
                            )
                            st.rerun()

                        if remove_clicked:
                            if task.pet and task in task.pet.tasks:
                                task.pet.tasks.remove(task)
                                st.success(
                                    f"Removed '{task.name}' for {pet_name}. Rebuilding schedule..."
                                )
                                st.rerun()
                            else:
                                st.error(
                                    "Could not remove task: task no longer exists."
                                )

        # Display the scheduled tasks
        st.subheader("📅 Daily Schedule")
        if scheduler.scheduled_tasks:
            schedule_data = []
            for task in scheduler.scheduled_tasks:
                pet_name = task.pet.name if task.pet else "Unknown"
                time_str = (
                    task.scheduled_time.strftime("%H:%M")
                    if task.scheduled_time
                    else "Unscheduled"
                )
                status = "✓ Done" if task.completed else "⏳ Pending"
                schedule_data.append(
                    {
                        "Time": time_str,
                        "Task": task.name,
                        "Pet": pet_name,
                        "Duration": f"{task.duration} min",
                        "Priority": task.priority.capitalize(),
                        "Status": status,
                    }
                )
            st.table(schedule_data)
        else:
            st.info("No tasks to schedule.")

## The above logic for adding pets and tasks is now handled in the correct UI locations.
