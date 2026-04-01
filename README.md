# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Smarter Scheduling

1. Conflict detection for same start-time tasks with warning system to alert user
2. Automatic conflict checks during scheduling
3. Automatically reschedule daily and weekly reoccuring tasks

### Testing PawPal+

`python -m pytest tests/test_pawpal.py -v`
My test cases check for conflict handling for 3+ tasks with the same time, tasks with no times, conflict tasks across different pets, etc. Recurring tasks are also tested to ensure they are rescheduled for valid times and only when they are marked completed. They also check that task sorting order is correct.

### Features

#### 🐾 Task Management

- **Create & Track Tasks** - Define pet care tasks with name, description, duration (in minutes), and priority level (low, medium, high)
- **Task Scheduling** - Assign specific date and time to each task for precise planning
- **Task Completion Tracking** - Mark tasks as completed or pending to maintain task status

#### 📅 Smart Scheduling Algorithm

- **Time-Based Sorting** - Automatically sorts all tasks chronologically by scheduled time, then by pet name
- **Multi-Pet Support** - Handles schedules for multiple pets under one owner with proper organization
- **Schedule Generation** - Creates a comprehensive daily schedule for an owner and their pets

#### ⚠️ Conflict Detection & Warnings

- **Automatic Conflict Detection** - Identifies when multiple tasks are scheduled for the same time across different pets
- **Detailed Conflict Reporting** - Displays specific warnings showing which tasks conflict and which pets are affected
  - Example: "Conflict at 18:00: Groom (Mocha), Walk (Mocha)"
- **Lightweight Conflict Handling** - Detects 2+ simultaneous tasks and alerts user without blocking schedule generation

#### 🔄 Recurring Task Management

- **Frequency Support** - Tasks can be marked as "daily" or "weekly" for automatic rescheduling
- **Smart Rescheduling** - Recurring tasks advance to the next scheduled time when:
  - Task is marked as completed
  - Scheduler date advances (new day)
- **Automatic Completion Reset** - Recurring tasks are automatically marked incomplete when rescheduled so they appear in future schedules

#### 📊 Schedule Intelligence

- **Task Filtering** - Filter tasks by completion status (completed vs. pending)
- **Human-Readable Explanations** - Generates summary text explaining:
  - Total number of scheduled tasks
  - Number and details of conflicts detected
  - Owner name and date context
- **Detailed Schedule Display** - Shows each task with time, pet, description, duration, priority, and status

#### 🎯 UI Integration

- **Interactive Streamlit Interface** - Add owners and pets, manage tasks with date/time selection
- **Real-Time Schedule Preview** - See current tasks for selected pet with scheduled times
- **Visual Conflict Alerts** - Color-coded warnings for scheduling conflicts
- **Comprehensive Schedule Table** - View all scheduled tasks in an organized, sortable format

### Demo

<a href="/course_images/ai110/demo.png" target="_blank"><img src='/course_images/ai110/demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.
