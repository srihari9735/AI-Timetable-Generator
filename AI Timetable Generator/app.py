import streamlit as st
import json
import pandas as pd
from scheduler import TTRScheduler
from docx import Document
from docx.shared import Inches
from io import BytesIO

st.set_page_config(page_title="🧠 AI Timetable Generator", layout="wide")

st.title("🧠 AI Timetable Generator")

# Custom CSS for Premium Look and Expanded Columns
st.markdown("""
<style>
    /* Expand table to full width and set column sizes */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
    }
    th {
        background-color: #2c3e50 !important;
        color: white !important;
        padding: 10px !important;
        text-align: center !important;
        font-size: 1rem !important;
    }
    td {
        padding: 12px !important;
        text-align: center !important;
        border-bottom: 1px solid #ddd !important;
        min-width: 120px !important; /* Slightly reduced column width */
        font-size: 0.95rem !important;
        white-space: pre-wrap !important; /* Handle multiline text */
    }
    tr:hover {background-color: #f5f5f5 !important;}
    
    /* Make the app container wider */
    .stApp {
        max-width: 95%;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Load default data
    try:
        with open('data/input.json', 'r') as f:
            default_data = json.load(f)
    except FileNotFoundError:
        default_data = {
            "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "periods_per_day": 6,
            "subjects": ["Math", "Physics", "Chemistry"],
            "teachers": {"Math": "Mr. A", "Physics": "Mr. B", "Chemistry": "Ms. C"},
            "rooms": ["Room1", "Room2"],
            "max_classes_per_day": 2,
            "break_periods": [3, 5]
        }

    subjects_input = st.text_area("Subjects (comma separated)", ", ".join(default_data['subjects']))
    rooms_input = st.text_area("Rooms (comma separated)", ", ".join(default_data['rooms']))
    
    col1, col2 = st.columns(2)
    periods = col1.number_input("Periods/Day", min_value=1, max_value=10, value=default_data.get('periods_per_day', 6))
    
    # Handle multiple breaks
    default_breaks = default_data.get('break_periods', [3])
    breaks_input = col2.text_input("Break Periods (comma separated)", value=", ".join(map(str, default_breaks)))
    try:
        break_periods = [int(b.strip()) for b in breaks_input.split(",") if b.strip()]
    except ValueError:
        st.error("Invalid break periods. Use numbers separated by commas.")
        break_periods = [3]

# Process Inputs
subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]
rooms = [r.strip() for r in rooms_input.split(",") if r.strip()]

# Teacher assignment (simplified for UI)
st.subheader("👨‍🏫 Teacher Assignment")
teachers = {}
cols = st.columns(3)
for i, sub in enumerate(subjects):
    teachers[sub] = cols[i % 3].text_input(f"Teacher for {sub}", value=default_data['teachers'].get(sub, "TBD"))

data = {
    "days": default_data['days'],
    "periods_per_day": periods,
    "subjects": subjects,
    "teachers": teachers,
    "rooms": rooms,
    "max_classes_per_day": 2,
    "break_periods": break_periods
}

if st.button("🚀 Generate Timetable"):
    scheduler = TTRScheduler(data)
    timetable = scheduler.generate()
    
    if not timetable:
        st.error("Could not generate a valid timetable. Check constraints or add more rooms/slots.")
    else:
        st.success("✅ Timetable Generated Successfully!")
        
        # Transform for display
        df_list = []
        for day in data['days']:
            row = {'Day': day}
            for p in range(1, periods + 1):
                if p in break_periods:
                    row[f'P{p}'] = "☕ BREAK"
                    continue
                    
                slot_data = [t for t in timetable if t['day'] == day and t['period'] == p]
                if slot_data:
                    # In this simple version, we might have multiple classes in same period if rooms/teachers allow
                    # For display let's just show the first one or a summary
                    row[f'P{p}'] = f"{slot_data[0]['subject']}\n({slot_data[0]['teacher']})\n[{slot_data[0]['room']}]"
                else:
                    row[f'P{p}'] = "-"
            df_list.append(row)
            
        df = pd.DataFrame(df_list)
        st.table(df)
        
        # Word Download Option
        def to_docx(df):
            doc = Document()
            doc.add_heading('AI Generated Timetable', 0)
            
            # Create Table
            table = doc.add_table(rows=1, cols=len(df.columns))
            table.style = 'Table Grid'
            
            # Add Headers
            hdr_cells = table.rows[0].cells
            for i, col in enumerate(df.columns):
                hdr_cells[i].text = col
            
            # Add Rows
            for index, row in df.iterrows():
                row_cells = table.add_row().cells
                for i, value in enumerate(row):
                    row_cells[i].text = str(value)
            
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer

        docx_file = to_docx(df)
        st.download_button(
            "📥 Download as Word (.docx)",
            docx_file,
            "timetable.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key='download-docx'
        )

        # Download options
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download as CSV",
            csv,
            "timetable.csv",
            "text/csv",
            key='download-csv'
        )
