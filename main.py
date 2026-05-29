import data

def main():
    print("=== University Timetable Data ===")
    
    # Print Courses
    print("\n--- Courses ---")
    for course in data.courses:
        print(f"Code: {course.code} | Short: {course.short_name} | Name: {course.name} | LTPS: {course.ltps} | Total Weekly Classes: {course.total_classes}")
        
    # Print Rooms
    print("\n--- Rooms ---")
    for room in data.rooms:
        print(f"Room No: {room.room_no} | Type: {room.room_type}")
        
    # Print Sections
    print("\n--- Sections ---")
    for section in data.sections:
        print(f"Section Name: {section.name}")
        
    # Print Days
    print("\n--- Days ---")
    print(", ".join(data.days))
    
    # Print Periods
    print("\n--- Period Timings ---")
    for period, timing in data.periods.items():
        print(f"{period}: {timing}")
        
    # Print Scheduling Blocks
    print("\n--- Consecutive Blocks ---")
    for block in data.consecutive_blocks:
        print(f"{block[0]} and {block[1]}")

if __name__ == "__main__":
    main()
