import streamlit as st
import pandas as pd
import sys
import io
import scheduler
import generate_timetable

# Page Configuration
st.set_page_config(layout="wide", page_title="University Timetable Generator")
st.title("University Timetable Generator")
st.markdown("Automated constraints-based timetable generation system.")

# Capture stdout to show logs
old_stdout = sys.stdout
log_capture = io.StringIO()
sys.stdout = log_capture

timetable = None
try:
    with st.spinner("Generating optimal schedule..."):
        timetable = scheduler.generate_timetable()
        if timetable:
            generate_timetable.validate_before_print(timetable)
except Exception as e:
    st.error(f"Error during generation: {e}")
finally:
    # Restore stdout
    sys.stdout = old_stdout

logs = log_capture.getvalue()

if timetable:
    st.success("✅ Timetable generated and validated successfully!")
    
    tabs = st.tabs([f"Section {name}" for name in timetable.keys()])
    
    time_mapping = {
        "P1": "8:10-9:00",
        "P2": "9:00-9:50",
        "P3": "10:00-10:50",
        "P4": "10:50-11:40",
        "P5": "12:20-1:10",
        "P6": "1:10-2:00",
        "P7": "2:10-3:00",
        "P8": "3:00-3:50"
    }

    for idx, (section_name, section_timetable) in enumerate(timetable.items()):
        with tabs[idx]:
            st.header(f"Section {section_name}")
            
            table, columns = generate_timetable.build_section_table(section_timetable)
            df = pd.DataFrame.from_dict(table, orient='index')
            
            df.rename(columns=time_mapping, inplace=True)
            df.insert(2, 'Morning Break', '☕ BREAK')
            df.insert(5, 'Lunch', '🍔 LUNCH')
            df.insert(8, 'Afternoon Break', '☕ BREAK')
            
            # Helper function to style cells
            def color_free(val):
                if val == 'FREE':
                    return 'background-color: #f0f2f6; color: #a0aab2'
                elif 'BREAK' in val or 'LUNCH' in val:
                    return 'background-color: #fff3cd; color: #856404; font-weight: bold'
                else:
                    return 'background-color: #e6f4ea; color: #1e8e3e; font-weight: bold'
            
            styled_df = df.style.map(color_free) if hasattr(df.style, 'map') else df.style.applymap(color_free)
            st.dataframe(styled_df, use_container_width=True)

    with st.expander("Show Logs"):
        st.code(logs, language="text")

else:
    st.error("Failed to generate timetable. Check the constraints or data inputs.")
