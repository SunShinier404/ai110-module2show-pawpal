from dataclasses import dataclass, field
from typing import List, Optional
import datetime

@dataclass
class Task:
	name: str
	duration: int  # in minutes
	priority: int  # 1 = highest
	description: Optional[str] = None
	scheduled_time: Optional[datetime.time] = None

@dataclass
class Pet:
	name: str
	species: str
	age: int
	tasks: List[Task] = field(default_factory=list)

@dataclass
class Owner:
	name: str
	pets: List[Pet] = field(default_factory=list)
	preferences: Optional[dict] = field(default_factory=dict)

@dataclass
class Plan:
	date: datetime.date
	tasks: List[Task] = field(default_factory=list)
	explanation: Optional[str] = None

	def generate_explanation(self):
		# Placeholder for explanation logic
		self.explanation = "Plan generated based on priorities and constraints."
