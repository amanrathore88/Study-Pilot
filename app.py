import streamlit as st
import json,os,tempfile
from extract import extract_syllabus, extract_text_from_pdf
from planner import allocate_hours, generate_weekly_plan, clean_json_response
from pdf_exprt import generate_pdf, load_timetable
from remainder import send_daily_nudge
from scheduler import save_schedule


st.set_page_config(
    page_title="Study Pilot",
    page_icon="📚",
    layout="wide"
)
st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.study-card {
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    background-color: #e8f5e9;
    border-left: 6px solid #2e7d32;
}

.big-title {
    font-size: 40px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

st.title(("📚 Study Pilot"))
st.caption("Stop guessing what to study, ask your agent instead")
st.header("Your study profile")

with st.sidebar:

    st.header("⚙ Study Profile")

    uploaded_file = st.file_uploader(
        "Upload Syllabus PDF",
        type=["pdf"]
    )

    email = st.text_input(
        "Your Email"
    )

    hours = st.slider(
        "Daily Study Hours",
        min_value=1,
        max_value=8,
        value=4
    )

    exam_date = st.date_input(
        "📅 Exam Date"
    )

    send_time = st.time_input(
    "Daily Reminder Time"
    )

    generate_btn = st.button(
        "🚀 Generate Plan",
        use_container_width=True
    )

if generate_btn:
    if not uploaded_file:
        st.error("Please upload a syllabus pdf file")
        st.stop()
        
    with st.spinner("Reading your syllabus..."):
        # Save the uploaded file to a temporary file so that pdfplumber can use it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        raw_text = extract_text_from_pdf(tmp_path)
        raw_syllabus = extract_syllabus(raw_text)

        cleaned = raw_syllabus.strip()
        if "```" in cleaned:
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]

        syllabus = json.loads(cleaned.strip())

    with st.spinner("Building your 7 days plan..."):
        allocated_hours = allocate_hours(syllabus, daily_hours=hours)
        raw_timetable = generate_weekly_plan(allocated_hours, daily_hours=hours)

        cleaned_timetable = raw_timetable.strip()
        if "```" in cleaned_timetable:
            cleaned_timetable = cleaned_timetable.split("```")[1]
            if cleaned_timetable.startswith("json"):
                cleaned_timetable = cleaned_timetable[4:]

        # find the json object
        start = cleaned_timetable.find("{")
        end = cleaned_timetable.rfind("}")
        cleaned_timetable = cleaned_timetable[start : end + 1]

        timetable_data = json.loads(cleaned_timetable)
        st.session_state["timetable_data"] = timetable_data

        with open("timetable.json", "w") as f:
            json.dump(timetable_data, f, indent=2)

    with st.spinner("Generating the PDF..."):
        rows, summary = load_timetable("timetable.json")
        generate_pdf(rows, summary, output_path="timetable.pdf")
            
    st.success("✅ Plan Completed")

    from datetime import date

    days_left = (
        exam_date - date.today()
    ).days

    st.metric(
        "Days Until Exam",
        days_left
    )

    col1,col2,col3 = st.columns(3)

    with col1:
        st.button("📋 Study Plan")

    with col2:
        st.button("📄 PDF Export")

    with col3:
        st.button("📧 Email")
        
    st.header("📋 Your weekly Timetable")
    for day in timetable_data["timetable"]:

        for slot in day["slots"]:

            chapters = ", ".join(
                slot["chapters_to_cover"]
            )

            st.markdown(
                f"""
                <div class='study-card'>
                    <h4>📅 Day {day['day']} - {day['date']}</h4>
                    <b>{slot['subject']}</b><br>
                    {chapters}<br><br>
                    ⏰ {slot['duration_minutes']} minutes
                </div>
                """,
                unsafe_allow_html=True
            )
            
    with open("timetable.pdf", "rb") as f:
        st.download_button(
            label = "📄 Download timetable pdf",
            data = f,
            file_name="my_study_plan.pdf",
            mime="application/pdf"
        )

# EMAIL SECTION

if "timetable_data" in st.session_state:

    st.divider()

    st.subheader("📧 Daily Email Reminder")

    if st.button("📧 Start Daily Emails"):

        save_schedule(
            email,
            str(send_time)
        )

        st.success(
            "✅ schedule.json created successfully."
        )        