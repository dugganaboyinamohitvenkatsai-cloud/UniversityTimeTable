from models import Course, Room, Section

# Actual Semester Courses
courses = [
    Course(code="25MT1306E", name="MATHEMATICS FOR DATA SCIENCE AND ANALYTICS", short_name="MDSA", ltps=(2, 0, 4, 0), faculty="Dr Rao"),
    Course(code="25SC1305E", name="DATA STRUCTURES AND ALGORITHMS - 2", short_name="DSA2", ltps=(4, 0, 2, 4), faculty="Dr Sharma"),
    Course(code="25SC1306E", name="COMPUTATIONAL FOUNDATIONS FOR ARTIFICIAL INTELLIGENCE", short_name="CFAI", ltps=(4, 0, 0, 4), faculty="Dr Kumar"),
    Course(code="25CS1201E", name="FRONT END DEVELOPMENT FRAMEWORKS AND UI ENGINEERING", short_name="FEDF", ltps=(0, 0, 4, 4), faculty="Dr Priya"),
    Course(code="25FL1301E", name="GERMAN LANGUAGE PROFICIENCY", short_name="FL", ltps=(0, 0, 4, 0), faculty="Dr Ramesh"),
    Course(code="25UC0036", name="GLOBAL LOGIC BUILDING CONTEST PRACTICUM", short_name="GLB", ltps=(0, 0, 0, 4), faculty="Dr Anitha")
]

# Theory + Lab Rooms
rooms = [
    Room(room_no="101", room_type="Theory"),
    Room(room_no="102", room_type="Theory"),
    Room(room_no="103", room_type="Theory"),
    Room(room_no="104", room_type="Theory"),
    Room(room_no="L1", room_type="Lab"),
    Room(room_no="L2", room_type="Lab"),
    Room(room_no="L3", room_type="Lab"),
    Room(room_no="L4", room_type="Lab")
]

# Sections
sections = [
    Section(name="1"),
    Section(name="2"),
    Section(name="3"),
    Section(name="4")
]

# Working days: Monday to Saturday
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Period timings
periods = {
    "P1": "8:10–9:00",
    "P2": "9:00–9:50",
    "P3": "10:00–10:50",
    "P4": "10:50–11:40",
    "P5": "12:20–1:10",
    "P6": "1:10–2:00",
    "P7": "2:10–3:00",
    "P8": "3:00–3:50"
}

# Valid consecutive scheduling blocks
consecutive_blocks = [
    ("P1", "P2"),
    ("P3", "P4"),
    ("P5", "P6"),
    ("P7", "P8")
]
