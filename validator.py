"""
University Timetable Generator - Validation System
This file acts as an independent testing suite for generated timetables.
It ensures that all constraints are met and outputs clean reports for viva explainability.
"""

import data
from collections import defaultdict

def flatten_timetable(all_timetables):
    """
    Helper function to convert the section-wise timetable dictionary 
    into a flat list of assignments for easier global checking.
    """
    flat_list = []
    for section_name, entries in all_timetables.items():
        flat_list.extend(entries)
    return flat_list

def validate_room_clashes(all_timetables):
    """
    Check that no room is assigned to multiple sections at the same time globally.
    Returns True if valid, False if a clash is found.
    """
    flat_list = flatten_timetable(all_timetables)
    is_valid = True
    
    # Group by (day, room)
    room_schedule = defaultdict(list)
    for entry in flat_list:
        room_schedule[(entry["day"], entry["room"])].append(entry)
        
    # Check each room's daily schedule for overlaps
    for (day, room), entries in room_schedule.items():
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                entry1 = entries[i]
                entry2 = entries[j]
                
                # Intersect period lists to check for overlaps
                overlap = set(entry1["periods"]).intersection(entry2["periods"])
                if overlap:
                    overlap_str = "-".join(sorted(list(overlap)))
                    print("ROOM CLASH DETECTED:")
                    print(f"{day} | {overlap_str} | Room {room}")
                    print(f"Sections: {entry1['section']} and {entry2['section']}\n")
                    is_valid = False
                    
                    
    return is_valid

def validate_faculty_clashes(all_timetables):
    """
    Check that no faculty is assigned to multiple sections at the same time globally.
    Returns True if valid, False if a clash is found.
    """
    flat_list = flatten_timetable(all_timetables)
    is_valid = True
    
    # Group by (day, faculty)
    faculty_schedule = defaultdict(list)
    for entry in flat_list:
        faculty = entry.get("faculty")
        if faculty:
            faculty_schedule[(entry["day"], faculty)].append(entry)
            
    # Check each faculty's daily schedule for overlaps
    for (day, faculty), entries in faculty_schedule.items():
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                entry1 = entries[i]
                entry2 = entries[j]
                
                # Intersect period lists to check for overlaps
                overlap = set(entry1["periods"]).intersection(entry2["periods"])
                if overlap:
                    overlap_str = "-".join(sorted(list(overlap)))
                    print("FACULTY CLASH FOUND:")
                    print(f"{faculty}")
                    print(f"{day}")
                    print(f"{overlap_str}\n")
                    print(f"Section {entry1['section']} -> {entry1['course']}")
                    print(f"Section {entry2['section']} -> {entry2['course']}\n")
                    is_valid = False
                    
    return is_valid

def validate_section_clashes(all_timetables):
    """
    Ensure a section never has overlapping classes scheduled at the same time.
    Returns True if valid, False if a clash is found.
    """
    is_valid = True
    
    for section_name, entries in all_timetables.items():
        # Group by day
        day_schedule = defaultdict(list)
        for entry in entries:
            day_schedule[entry["day"]].append(entry)
            
        # Check each day for overlapping periods for this section
        for day, day_entries in day_schedule.items():
            for i in range(len(day_entries)):
                for j in range(i + 1, len(day_entries)):
                    entry1 = day_entries[i]
                    entry2 = day_entries[j]
                    
                    overlap = set(entry1["periods"]).intersection(entry2["periods"])
                    if overlap:
                        overlap_str = "-".join(sorted(list(overlap)))
                        print("SECTION CLASH DETECTED:")
                        print(f"Section {section_name}")
                        print(f"{day} | {overlap_str} | {entry1['course']} and {entry2['course']}\n")
                        is_valid = False
                        
    return is_valid

def validate_ltps_completion(all_timetables):
    """
    Verify every course satisfies its LTPS requirements exactly according to data.courses.
    Returns True if valid, False if a mismatch is found.
    """
    is_valid = True
    
    # Pre-calculate expected periods from data.courses (Source of truth)
    expected_ltps = {}
    for course in data.courses:
        expected_ltps[course.short_name] = {
            'L': course.ltps[0],
            'T': course.ltps[1],
            'P': course.ltps[2],
            'S': course.ltps[3]
        }
        
    for section_name, entries in all_timetables.items():
        # Count scheduled periods per course and class type for this section
        found_ltps = defaultdict(lambda: defaultdict(int))
        for entry in entries:
            course = entry["course"]
            c_type = entry["class_type"]
            found_ltps[course][c_type] += len(entry["periods"])
            
        # Check counts against expected numbers
        for course in data.courses:
            c_name = course.short_name
            course_passed = True
            
            for c_type in ['L', 'T', 'P', 'S']:
                expected = expected_ltps[c_name][c_type]
                found = found_ltps[c_name][c_type]
                
                if expected != found:
                    print("LTPS MISMATCH:")
                    print(f"Section {section_name} | {c_name} ({c_type})")
                    print(f"Expected: {expected}")
                    print(f"Found: {found}\n")
                    is_valid = False
                    course_passed = False
                    
            if course_passed:
                # Print confirmation if all LTPS constraints for this course are met perfectly
                print(f"LTPS CHECK PASSED:\nSection {section_name} | {c_name}\n")
                
    return is_valid

def validate_room_types(all_timetables):
    """
    Ensure practicals (P) are only in Lab rooms, and L/T/S are only in Theory rooms.
    Returns True if valid, False if a mismatch is found.
    """
    is_valid = True
    
    # Create room type mapping dynamically from data
    room_types = {room.room_no: room.room_type for room in data.rooms}
    
    flat_list = flatten_timetable(all_timetables)
    for entry in flat_list:
        r_type = room_types[entry["room"]]
        c_type = entry["class_type"]
        
        if c_type == 'P' and r_type != 'Lab':
            print("ROOM TYPE MISMATCH:")
            print(f"Section {entry['section']} | {entry['course']} ({c_type}) in Room {entry['room']} (Theory)")
            print("Practical classes must be in a Lab room.\n")
            is_valid = False
        elif c_type in ['L', 'T', 'S'] and r_type != 'Theory':
            print("ROOM TYPE MISMATCH:")
            print(f"Section {entry['section']} | {entry['course']} ({c_type}) in Room {entry['room']} (Lab)")
            print("Theory/Tutorial/Skill classes must be in a Theory room.\n")
            is_valid = False
            
    return is_valid

def generate_daily_load_report(all_timetables):
    """
    Generates a visual report of the daily period load for each section.
    Extremely useful for analyzing the success of timetable balancing heuristics.
    """
    print("=" * 32)
    print("DAILY LOAD REPORT")
    print("=" * 17)
    
    for section_name, entries in all_timetables.items():
        print(f"\nSECTION {section_name}")
        
        # Count periods per day
        day_counts = defaultdict(int)
        for entry in entries:
            day_counts[entry["day"]] += len(entry["periods"])
            
        for day in data.days:
            count = day_counts[day]
            print(f"{day} -> {count} periods")
    print("")

def run_all_validations(all_timetables):
    """
    Runs all independent constraint checkers and prints a unified master report.
    """
    print("\n" + "=" * 32)
    print("TIMETABLE VALIDATION REPORT")
    print("=" * 27 + "\n")
    
    r1 = validate_room_clashes(all_timetables)
    r2 = validate_section_clashes(all_timetables)
    r3 = validate_ltps_completion(all_timetables)
    r4 = validate_room_types(all_timetables)
    r5 = validate_faculty_clashes(all_timetables)
    
    print("-" * 32)
    print(f"Room Clash Check:    {'PASSED' if r1 else 'FAILED'}")
    print(f"Section Clash Check: {'PASSED' if r2 else 'FAILED'}")
    print(f"Faculty Clash Check: {'PASSED' if r5 else 'FAILED'}")
    print(f"LTPS Check:          {'PASSED' if r3 else 'FAILED'}")
    print(f"Room Type Check:     {'PASSED' if r4 else 'FAILED'}")
    print("-" * 32)
    
    if r1 and r2 and r3 and r4 and r5:
        print("\nALL VALIDATIONS PASSED\n")
        return True
    else:
        print("\nTIMETABLE CONTAINS ERRORS\n")
        return False

if __name__ == "__main__":
    import scheduler
    
    print("Generating timetable...\n")
    # Run the scheduler
    timetable = scheduler.generate_timetable()
    
    if timetable:
        print("\nRunning validator...\n")
        # Run validations
        run_all_validations(timetable)
        
        # Print load distribution
        generate_daily_load_report(timetable)
    else:
        print("Could not run validator because scheduling failed.")
