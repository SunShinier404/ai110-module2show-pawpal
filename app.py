import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler


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


# Only allow adding a task if an owner and pet are selected

if st.button("Add task"):
    if selected_pet:
        new_task = Task(
            name=task_title,
            description=task_description,
            duration=duration,
            priority=priority,
        )
        selected_pet.add_task(new_task)
        st.success(f"Task '{task_title}' added to pet '{selected_pet.name}'.")
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

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )

## The above logic for adding pets and tasks is now handled in the correct UI locations.
