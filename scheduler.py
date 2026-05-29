"""
Timetable Scheduler Module
Implements a constraint satisfaction scheduler for the university timetable.
"""

import sys
import random
import data
from constraints import validate_assignment

# Fixed seed for reproducibility
random.seed(42)

_total_attempts = 0
_total_assigned = 0
_total_rejected = 0


def _reset_counters():
    """Reset global attempt counters at the start of each scheduling attempt."""
    global _total_attempts, _total_assigned, _total_rejected
    _total_attempts = 0
    _total_assigned = 0
    _total_rejected = 0


def get_day_load(current_timetable, day, section_name):
    """
    Returns the number of periods already scheduled on a given day for a section.
    Used to prefer least-loaded days for balanced distribution.
    """
    load = 0
    for entry in current_timetable:
        if entry["day"] == day and entry["section"] == section_name:
            load += len(entry["periods"])
    return load


def course_exists_same_day(current_timetable, day, course_short_name, section_name):
    """
    Returns True if the given course is already scheduled on the given day.
    Used to spread courses across different days of the week.
    """
    for entry in current_timetable:
        if entry["day"] == day and entry["section"] == section_name and entry["course"] == course_short_name:
            return True
    return False


def get_block_usage_count(current_timetable, periods, section_name):
    """
    Returns how many times a specific block of periods has been used for this section.
    Used to distribute classes across different time blocks.
    """
    count = 0
    for entry in current_timetable:
        if entry["periods"] == periods and entry["section"] == section_name:
            count += 1
    return count


def get_block_index(periods):
    """
    Returns the numerical index of a period block.
    P1-P2 = 0, P3-P4 = 1, P5-P6 = 2, P7-P8 = 3.
    """
    if "P1" in periods: return 0
    if "P3" in periods: return 1
    if "P5" in periods: return 2
    if "P7" in periods: return 3
    if "P2" in periods: return 0
    if "P4" in periods: return 1
    if "P6" in periods: return 2
    if "P8" in periods: return 3
    return 99


def calculate_gap_score(current_timetable, day, periods, section_name):
    """
    Prefers scheduling classes near already occupied blocks to avoid isolated empty gaps.
    Includes Lunch Break Rule: penalizes scheduling isolated afternoon classes if morning is empty.
    Returns a lower score (better) if the proposed periods are adjacent to existing classes.
    """
    occupied_indices = []
    for entry in current_timetable:
        if entry["day"] == day and entry["section"] == section_name:
            occupied_indices.append(get_block_index(entry["periods"]))

    target_idx = get_block_index(periods)

    if not occupied_indices:
        # If day is empty, penalize afternoon blocks so morning slots are preferred
        if target_idx >= 2:
            return 2
        return 0

    min_dist = min(abs(target_idx - occ_idx) for occ_idx in occupied_indices)
    return min_dist


def filter_rooms_by_class_type(class_type):
    """
    Returns only rooms that are valid for the given class type.
    P → Lab rooms, L/T/S → Theory rooms.
    """
    if class_type == 'P':
        return [r for r in data.rooms if r.room_type == 'Lab']
    else:
        return [r for r in data.rooms if r.room_type == 'Theory']


def is_faculty_free(current_timetable, day, periods, faculty):
    """
    Returns True if the faculty has no classes during the proposed periods on the given day.
    """
    if not faculty:
        return True
    for entry in current_timetable:
        if entry["day"] == day and entry.get("faculty") == faculty:
            if any(p in entry["periods"] for p in periods):
                return False
    return True


def is_section_free(current_timetable, day, periods, section_name):
    """
    Returns True if the section has no classes during the proposed periods on the given day.
    """
    for entry in current_timetable:
        if entry["day"] == day and entry["section"] == section_name:
            if any(p in entry["periods"] for p in periods):
                return False
    return True


def is_room_free(current_timetable, day, periods, room_no):
    """
    Returns True if the room has no classes during the proposed periods on the given day.
    """
    for entry in current_timetable:
        if entry["day"] == day and entry["room"] == room_no:
            if any(p in entry["periods"] for p in periods):
                return False
    return True


def get_course_scheduling_units(course):
    """
    Expands a course's LTPS structure into a sorted list of (class_type, count) units.
    Practicals come first (hardest to schedule due to limited Lab rooms).
    """
    ltps_dict = {
        'L': course.ltps[0],
        'T': course.ltps[1],
        'P': course.ltps[2],
        'S': course.ltps[3]
    }
    # Sort by: Practicals first (P), then by descending count (most classes first)
    # This is the "hardest-first" heuristic for constraint satisfaction
    priority_order = {'P': 0, 'L': 1, 'S': 2, 'T': 3}
    units = []
    for class_type, count in ltps_dict.items():
        if count > 0:
            units.append((class_type, count))
    units.sort(key=lambda x: (priority_order.get(x[0], 99), -x[1]))
    return units


def score_timetable(timetable_dict):
    """
    Scores a complete timetable. Lower is better.
    Factors:
      - Day load variance (penalize uneven days)
      - Free gaps between classes (penalize fragmentation)
      - Course spread across week (penalize same-day duplicates)
    """
    score = 0.0

    for section_name, entries in timetable_dict.items():
        # --- Factor 1: Day load variance ---
        day_loads = []
        for day in data.days:
            load = sum(len(e["periods"]) for e in entries if e["day"] == day)
            day_loads.append(load)

        if day_loads:
            avg_load = sum(day_loads) / len(day_loads)
            variance = sum((l - avg_load) ** 2 for l in day_loads) / len(day_loads)
            score += variance * 10  # Weight: 10x

        # --- Factor 2: Free gap penalty ---
        for day in data.days:
            day_entries = [e for e in entries if e["day"] == day]
            if not day_entries:
                continue
            occupied_blocks = sorted(set(get_block_index(e["periods"]) for e in day_entries))
            if len(occupied_blocks) >= 2:
                # Count internal gaps (unoccupied blocks between first and last class)
                first_block = occupied_blocks[0]
                last_block = occupied_blocks[-1]
                for b in range(first_block + 1, last_block):
                    if b not in occupied_blocks:
                        score += 5  # Penalty per gap

        # --- Factor 3: Same-course-same-day duplicates ---
        for day in data.days:
            day_entries = [e for e in entries if e["day"] == day]
            courses_on_day = [e["course"] for e in day_entries]
            duplicates = len(courses_on_day) - len(set(courses_on_day))
            score += duplicates * 8  # Penalty per duplicate

    return score


def _generate_timetable_attempt():
    """
    Core scheduling logic for a single attempt.
    Uses deterministic sorting (not random shuffling) for reproducibility.
    Pre-filters rooms by type, pre-checks faculty/section availability.
    """
    global _total_attempts, _total_assigned, _total_rejected
    current_timetable = []

    # Step 1: Loop through all sections
    for section in data.sections:
        section_name = section.name
        print(f"\n--- Scheduling Section {section_name} ---")
        sys.stdout.flush()

        # Step 2: Sort courses by scheduling difficulty (hardest first)
        sorted_courses = sorted(
            data.courses,
            key=lambda c: (
                -c.ltps[2],   # Practicals first (most constrained)
                -c.total_classes,  # Then most classes
            )
        )

        # Step 3: For each course, expand into scheduling units
        for course in sorted_courses:
            units = get_course_scheduling_units(course)

            for class_type, total_periods_needed in units:
                remaining_classes = total_periods_needed

                # Pre-filter valid rooms for this class type (eliminates room-type spam)
                valid_rooms = filter_rooms_by_class_type(class_type)

                while remaining_classes > 0:
                    assigned = False

                    # Decide block size: 2 periods if possible, else 1
                    if remaining_classes >= 2:
                        periods_to_assign = 2
                    else:
                        periods_to_assign = 1

                    # ------------------------------------------------
                    # Prepare Candidate Days (sorted deterministically)
                    # ------------------------------------------------
                    preferred_days = []
                    fallback_days = []

                    for day in data.days:
                        if course_exists_same_day(current_timetable, day, course.short_name, section_name):
                            fallback_days.append(day)
                        else:
                            preferred_days.append(day)

                    # Sort by load (least loaded first) — deterministic, no shuffle
                    preferred_days.sort(key=lambda d: get_day_load(current_timetable, d, section_name))
                    fallback_days.sort(key=lambda d: get_day_load(current_timetable, d, section_name))

                    candidate_days = preferred_days + fallback_days

                    for day in candidate_days:
                        if assigned:
                            break

                        # ------------------------------------------------
                        # Prepare Candidate Blocks (sorted deterministically)
                        # ------------------------------------------------
                        if periods_to_assign == 2:
                            blocks_to_try = [list(b) for b in data.consecutive_blocks]
                        else:
                            blocks_to_try = [[p] for p in data.periods.keys()]

                        # Sort by gap score then usage count (deterministic, no shuffle)
                        blocks_to_try.sort(key=lambda b: (
                            calculate_gap_score(current_timetable, day, b, section_name),
                            get_block_usage_count(current_timetable, b, section_name)
                        ))

                        for periods in blocks_to_try:
                            if assigned:
                                break

                            # =============================================
                            # PRE-CHECK 1: Section availability
                            # Skip immediately if section is busy
                            # =============================================
                            if not is_section_free(current_timetable, day, periods, section_name):
                                continue

                            # =============================================
                            # PRE-CHECK 2: Faculty availability
                            # Skip entire block if faculty is occupied
                            # (eliminates faculty-clash spam)
                            # =============================================
                            if not is_faculty_free(current_timetable, day, periods, course.faculty):
                                continue

                            # =============================================
                            # PRE-CHECK 3: Sort valid rooms by availability
                            # Only try rooms that are actually free
                            # =============================================
                            available_rooms = [
                                r for r in valid_rooms
                                if is_room_free(current_timetable, day, periods, r.room_no)
                            ]
                            # Sort rooms deterministically by room number
                            available_rooms.sort(key=lambda r: r.room_no)

                            for room in available_rooms:
                                _total_attempts += 1

                                # Full constraint validation (catches any edge cases)
                                is_valid, msg, warnings = validate_assignment(
                                    current_timetable, day, periods, room,
                                    section_name, course.short_name, class_type,
                                    remaining_classes, faculty=course.faculty
                                )

                                if is_valid:
                                    assignment = {
                                        "day": day,
                                        "periods": periods,
                                        "room": room.room_no,
                                        "section": section_name,
                                        "course": course.short_name,
                                        "faculty": course.faculty,
                                        "class_type": class_type
                                    }
                                    current_timetable.append(assignment)
                                    remaining_classes -= len(periods)
                                    assigned = True
                                    _total_assigned += 1

                                    # Compact one-line log: [ASSIGNED]
                                    print(f"  [ASSIGNED] Sec {section_name} | {course.short_name}({class_type}) | {day} {'-'.join(periods)} | Room {room.room_no}")

                                    for warning in warnings:
                                        print(f"    ⚠ {warning}")
                                    break
                                else:
                                    _total_rejected += 1

                                    # Only log rejections (useful for debugging)
                                    print(f"  [REJECT] Sec {section_name} | {course.short_name}({class_type}) | {day} {'-'.join(periods)} | Room {room.room_no} -> {msg}")

                    # If we exhausted all days, blocks, and rooms but couldn't assign
                    if not assigned:
                        print(f"\n⚠ Scheduling failed for Section {section_name} "
                              f"(Course: {course.short_name} {class_type})")
                        return None

    # Structure into section-wise dictionary
    timetable_dict = {section.name: [] for section in data.sections}
    for entry in current_timetable:
        timetable_dict[entry["section"]].append(entry)

    return timetable_dict


def generate_timetable():
    """
    Generates a valid timetable for ALL SECTIONS.
    Fully deterministic: same input → same output every run.
    Single attempt since sorting-based candidate selection has no randomness.
    """
    print("=== STARTING SCHEDULING PROCESS ===")
    sys.stdout.flush()
    _reset_counters()

    # Fixed seed for any residual random usage
    random.seed(42)

    timetable_dict = _generate_timetable_attempt()

    if timetable_dict is not None:
        score = score_timetable(timetable_dict)
        print(f"\n--- Scheduling Stats ---")
        print(f"Total Attempts:  {_total_attempts}")
        print(f"Assigned:        {_total_assigned}")
        print(f"Rejected:        {_total_rejected}")
        print(f"Schedule Score:  {score:.1f} (lower is better)")
        print(f"\n=== SCHEDULING PROCESS COMPLETED ===\n")
        sys.stdout.flush()
        return timetable_dict

    print("Scheduling failed.")
    sys.stdout.flush()
    return None


def print_timetable(timetable_dict):
    """
    Prints the generated timetable clearly, grouped by section and day.
    (Legacy debug printer — the formatter.py version is used for final output.)
    """
    for section_name, section_timetable in timetable_dict.items():
        print("=" * 40)
        print(f" FINAL TIMETABLE FOR SECTION {section_name}")
        print("=" * 40)

        for day in data.days:
            print(f"\n{day.upper()}")

            day_entries = [entry for entry in section_timetable if entry["day"] == day]

            if not day_entries:
                print("  No classes scheduled.")
                continue

            day_entries.sort(key=lambda x: x["periods"][0])

            for entry in day_entries:
                period_str = "-".join(entry["periods"])
                print(f"{period_str} -> {entry['course']} ({entry['class_type']}) -> Room {entry['room']}")
        print("\n")


if __name__ == "__main__":
    # Test block to run scheduler.py independently
    timetable_dict = generate_timetable()
    if timetable_dict is not None:
        print_timetable(timetable_dict)
    else:
        print("\nFailed to generate timetable.")
