from dataclasses import dataclass

# Dataclass for Course
@dataclass
class Course:
    code: str
    name: str
    short_name: str
    ltps: tuple[int, int, int, int]  # Tuple for (Lecture, Tutorial, Practical, Skill)
    faculty: str = ""

    @property
    def total_classes(self) -> int:
        """Calculate required weekly periods from LTPS structure."""
        return sum(self.ltps)

# Dataclass for Room
@dataclass
class Room:
    room_no: str
    room_type: str  # e.g., 'Theory' or 'Lab'

# Dataclass for Section
@dataclass
class Section:
    name: str
