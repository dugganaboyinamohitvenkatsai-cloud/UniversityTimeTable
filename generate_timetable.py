"""
Timetable Formatter
"""

import sys
import data

def build_section_table(section_timetable):
    """Builds a structured dictionary for a section's timetable."""
    # Columns are the exact period keys like 'P1', 'P2', etc.
    columns = list(data.periods.keys())
    table = {}
    
    # Initialize every day with FREE slots
    for day in data.days:
        table[day] = {col: "FREE" for col in columns}
        
    # Populate table with scheduled classes
    for entry in section_timetable:
        day = entry["day"]
        periods = entry["periods"]
        
        # Format course info without room
        course = str(entry['course']).strip().replace('\n', '').replace('\r', '')
        c_type = str(entry['class_type']).strip().replace('\n', '').replace('\r', '')
        course_info = f"{course}({c_type})"
        
        # Populate each individual period in the block
        for p in periods:
            if table[day][p] == "FREE":
                table[day][p] = course_info
            else:
                # Append if another class is already in this period (fallback for errors)
                table[day][p] += f" & {course_info}"
                        
    return table, columns


def print_section_timetable(section_name, section_timetable):
    """
    Prints the beautifully formatted timetable for a specific section.
    Also calculates and prints summary statistics.
    """
    table, columns = build_section_table(section_timetable)
    
    # Set fixed column widths for perfect alignment
    day_col = 12
    col = 14
    brk = 10
    
    # Calculate exact line length for the separator
    sep_length = day_col + (col * 8) + (brk * 3)

    print("\n" + "=" * sep_length)
    print(f"FINAL TIMETABLE FOR SECTION {section_name}")
    print("=" * sep_length + "\n")
    
    # Print Table Header
    # Timings for headers
    t = [
        "8:10-9:00", "9:00-9:50", 
        "10:00-10:50", "10:50-11:40", 
        "12:20-1:10", "1:10-2:00", 
        "2:10-3:00", "3:00-3:50"
    ]
    
    header = f"{'DAY':<{day_col}}"
    header += f"{t[0]:<{col}}{t[1]:<{col}}{'BREAK':<{brk}}{t[2]:<{col}}{t[3]:<{col}}{'LUNCH':<{brk}}{t[4]:<{col}}{t[5]:<{col}}{'BREAK':<{brk}}{t[6]:<{col}}{t[7]:<{col}}"
    print(header)
    print("-" * sep_length)
    
    # Track statistics
    total_scheduled_periods = 0
    days_used_set = set()
    
    # Print Table Rows
    for day in data.days:
        # Clean day string just in case to prevent newlines
        clean_day = str(day).strip().replace('\n', '').replace('\r', '')
        row_str = f"{clean_day:<{day_col}}"
        day_has_class = False
        
        # Build the visual row injecting breaks
        vals = []
        for c in columns:
            val = str(table[day][c]).strip().replace('\n', ' ').replace('\r', '')
            if len(val) >= col:
                val = val[:col-1]
            vals.append(val)
        
        for val in vals:
            if val != "FREE": day_has_class = True
            
        row_str += f"{vals[0]:<{col}}{vals[1]:<{col}}{'BREAK':<{brk}}{vals[2]:<{col}}{vals[3]:<{col}}{'LUNCH':<{brk}}{vals[4]:<{col}}{vals[5]:<{col}}{'BREAK':<{brk}}{vals[6]:<{col}}{vals[7]:<{col}}"
                
        print(row_str)
        if day_has_class:
            days_used_set.add(day)
            
    # Calculate statistics based on actual periods
    for entry in section_timetable:
        total_scheduled_periods += len(entry["periods"])
        
    # Total periods mathematically available (8 periods * 6 days = 48)
    total_possible_periods = len(data.days) * len(data.periods)
    free_periods = total_possible_periods - total_scheduled_periods
    days_used = len(days_used_set)
    
    # Print Summary block
    print("\nSUMMARY:")
    print("-" * 8)
    print(f"Total Scheduled Periods: {total_scheduled_periods}")
    print(f"Free Periods: {free_periods}")
    print(f"Days Used: {days_used}\n")
    sys.stdout.flush()


def validate_before_print(all_timetables):
    """Runs constraint validation on the final timetable before printing."""
    import validator
    print("\n" + "=" * 50)
    print("RUNNING PRE-PRINT VALIDATION...")
    print("=" * 50)
    is_valid = validator.run_all_validations(all_timetables)
    sys.stdout.flush()
    if is_valid:
        print("Pre-print validation PASSED. Rendering timetables.\n")
    else:
        print("Pre-print validation found issues (see above).")
        print("Rendering best available timetable anyway.\n")
    sys.stdout.flush()
    return is_valid


def format_all_timetables(all_timetables):
    """
    Validates then prints formatted timetables for all sections.
    Each section is printed independently with its own header and summary.
    """
    # Step 1: Validate the timetable before rendering
    validate_before_print(all_timetables)

    # Step 2: Print each section independently
    for section_name, section_timetable in all_timetables.items():
        print_section_timetable(section_name, section_timetable)


if __name__ == "__main__":
    # Test block to run formatter independently
    import scheduler
    
    print("Generating timetable...\n")
    timetable = scheduler.generate_timetable()
    
    if timetable:
        print("Printing formatted timetable...\n")
        format_all_timetables(timetable)
    else:
        print("Could not format because scheduling failed.")
