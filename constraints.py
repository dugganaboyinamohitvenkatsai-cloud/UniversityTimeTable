"""
University Timetable Generator - Constraints Logic
This file contains ONLY constraint-checking logic for the CSP (Constraint Satisfaction Problem).
It checks whether a proposed timetable assignment is valid according to defined rules.

Beginner-friendly structure designed for easy explanation in viva.
"""

from data import consecutive_blocks

# ==========================================
# HARD CONSTRAINTS (Must Never Break)
# ==========================================

def check_room_clash(current_timetable, day, periods, room_no):
    """
    Hard Constraint 1: No Room Clash
    Same room cannot be assigned to two different classes at the same time.
    """
    for entry in current_timetable:
        if entry["day"] == day and entry["room"] == room_no:
            # If any of the requested periods overlap with already scheduled periods
            if any(p in entry["periods"] for p in periods):
                overlap_periods = "-".join(periods)
                return False, f"Room {room_no} already occupied {day} {overlap_periods}"
    return True, ""


def check_section_clash(current_timetable, day, periods, section_name):
    """
    Hard Constraint 2: No Section Clash
    Same section cannot have multiple classes simultaneously.
    """
    for entry in current_timetable:
        if entry["day"] == day and entry["section"] == section_name:
            # If any of the requested periods overlap
            if any(p in entry["periods"] for p in periods):
                overlap_periods = "-".join(periods)
                return False, f"Section {section_name} already has a class on {day} {overlap_periods}"
    return True, ""


def check_faculty_clash(current_timetable, day, periods, faculty):
    """
    Hard Constraint 6: Faculty Clash
    Same faculty cannot teach two different sections at the same time.
    """
    if not faculty:
        return True, ""
        
    for entry in current_timetable:
        # safely check entry.get("faculty") in case of older formats
        if entry["day"] == day and entry.get("faculty") == faculty:
            # Check if periods overlap
            if any(p in entry["periods"] for p in periods):
                overlap_periods = "-".join(periods)
                return False, f"Faculty {faculty} already occupied {day} {overlap_periods}"
    return True, ""


def check_room_type(class_type, room_type):
    """
    Hard Constraint 3: Room Type Validation
    Practical (P) must use Lab room. Lecture/Tutorial/Skill (L/T/S) must use Theory room.
    """
    if class_type == 'P':
        if room_type != 'Lab':
            return False, "Practical class must use Lab room"
    elif class_type in ['L', 'T', 'S']:
        if room_type != 'Theory':
            # Map type to a readable word for error message
            type_name = {"L": "Lecture", "T": "Tutorial", "S": "Skill"}[class_type]
            return False, f"{type_name} class must use Theory room"
    else:
        return False, f"Unknown class type: {class_type}"
    
    return True, ""


def check_consecutive_rule(periods, remaining_classes):
    """
    Hard Constraint 4: Consecutive Block Rule
    Prefer valid consecutive blocks: (P1,P2), (P3,P4), (P5,P6), (P7,P8)
    Only allow a single period if exactly one required period remains.
    """
    # 1. Handling blocks of 2 periods
    if len(periods) == 2:
        block = (periods[0], periods[1])
        # Check if it matches any predefined valid block from data.py
        if block in consecutive_blocks:
            if remaining_classes >= 2:
                return True, ""
            else:
                return False, "Not enough required classes remaining to schedule a block of 2"
        else:
            return False, f"Periods {periods[0]}-{periods[1]} do not form a valid consecutive block"
            
    # 2. Handling single period
    elif len(periods) == 1:
        if remaining_classes == 1:
            return True, ""
        else:
            return False, "Single period scheduling is only allowed when exactly 1 required period remains"
            
    # 3. Invalid number of periods
    return False, "Invalid period count: Must schedule 1 or 2 periods at a time"


def check_ltps_completion(periods, remaining_classes):
    """
    Hard Constraint 5: LTPS Completion Tracking
    Ensures we do not schedule more periods than required for this specific class type (L/T/P/S).
    """
    if len(periods) > remaining_classes:
        return False, f"Cannot schedule {len(periods)} periods. Only {remaining_classes} remaining for this type."
    return True, ""


# ==========================================
# SOFT CONSTRAINTS (Preferred Rules)
# ==========================================

def check_same_course_same_day(current_timetable, day, course_short_name, section_name):
    """
    Soft Constraint 1: Avoid repeating the same course twice in one day.
    Instead of failing, this returns a warning string if violated.
    """
    for entry in current_timetable:
        if entry["day"] == day and entry["section"] == section_name and entry["course"] == course_short_name:
            return False, f"Warning: Same course {course_short_name} repeated twice on {day}"
    return True, ""


def check_course_spread(current_timetable, day, periods, course_short_name, section_name):
    """
    Soft Constraint 2: Spread course across the week.
    Avoid scheduling too many periods of the same course on the same day.
    """
    scheduled_periods = 0
    for entry in current_timetable:
        if entry["day"] == day and entry["section"] == section_name and entry["course"] == course_short_name:
            scheduled_periods += len(entry["periods"])
            
    if scheduled_periods + len(periods) > 2:
        return False, f"Warning: Too many {course_short_name} periods scheduled on {day}"
    return True, ""


def check_soft_constraints(current_timetable, day, periods, course_short_name, section_name):
    """
    Aggregates all soft constraints and returns a list of warnings or preference remarks.
    """
    warnings = []
    
    # 1. Check if course repeats on same day
    success, msg = check_same_course_same_day(current_timetable, day, course_short_name, section_name)
    if not success:
        warnings.append(msg)
        
    # 2. Check if course is spread across the week
    success, msg = check_course_spread(current_timetable, day, periods, course_short_name, section_name)
    if not success:
        warnings.append(msg)
        
    # NOTE FOR VIVA: 
    # Additional soft constraints can be implemented here, such as:
    # 1. Avoid unnecessary timetable gaps (Too many free periods between classes).
    # These would return preference scores or warnings instead of hard failures.
    
    return warnings


# ==========================================
# MAIN VALIDATION FUNCTION
# ==========================================

def validate_assignment(current_timetable, day, periods, room_obj, section_name, course_short_name, class_type, remaining_classes, faculty=""):
    """
    Combines all Hard Constraints to validate if an assignment is allowed,
    then evaluates Soft Constraints to provide warnings.
    
    Args:
        current_timetable (list): The timetable state so far.
        day (str): The day of the week (e.g., "Monday").
        periods (list): The periods being requested (e.g., ["P1", "P2"]).
        room_obj (Room): The Room object being assigned.
        section_name (str): The name of the section.
        course_short_name (str): The short name of the course.
        class_type (str): The specific class type ('L', 'T', 'P', or 'S').
        remaining_classes (int): Count of remaining classes for this specific class_type.
        faculty (str): The faculty assigned to teach this course.
        
    Returns:
        tuple: (True, "Valid assignment", warnings_list) or (False, "Reason why constraint failed", [])
    """
    
    # 1. LTPS Completion Tracking
    success, msg = check_ltps_completion(periods, remaining_classes)
    if not success: return False, f"Rejected: {msg}", []
    
    # 2. Consecutive Block Rule
    success, msg = check_consecutive_rule(periods, remaining_classes)
    if not success: return False, f"Rejected: {msg}", []
    
    # 3. Room Type Validation
    success, msg = check_room_type(class_type, room_obj.room_type)
    if not success: return False, f"Rejected: {msg}", []
    
    # 4. No Room Clash
    success, msg = check_room_clash(current_timetable, day, periods, room_obj.room_no)
    if not success: return False, f"Rejected: {msg}", []
    
    # 5. Faculty Clash (Called right after room clash per requirements)
    success, msg = check_faculty_clash(current_timetable, day, periods, faculty)
    if not success: return False, f"Rejected: {msg}", []
    
    # 5. No Section Clash
    success, msg = check_section_clash(current_timetable, day, periods, section_name)
    if not success: return False, f"Rejected: {msg}", []
    
    # All hard constraints passed
    # Now evaluate soft constraints
    warnings = check_soft_constraints(current_timetable, day, periods, course_short_name, section_name)
    
    return True, "Valid assignment", warnings
