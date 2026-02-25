import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# ================= FILE CONFIG =================
FILE_NAME = "attendance_data.csv"
STUDENTS_FILE = "students.csv"

st.set_page_config(page_title="Smart Attendance Tracker", layout="wide")

# ================= INIT FILES SAFELY =================
if not os.path.exists(FILE_NAME):
    pd.DataFrame(
        columns=["Date", "Student Name", "Subject", "Period", "Status"]
    ).to_csv(FILE_NAME, index=False)

if not os.path.exists(STUDENTS_FILE):
    pd.DataFrame(columns=["Student Name"]).to_csv(STUDENTS_FILE, index=False)


def load_attendance():
    df = pd.read_csv(FILE_NAME)
    df.columns = df.columns.str.strip()

    required_cols = ["Date", "Student Name", "Subject", "Period", "Status"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    df = df[required_cols]
    return df


def save_attendance(df):
    df.to_csv(FILE_NAME, index=False)


# ================= SUBJECTS & PERIODS =================
SUBJECTS = [
    "Mathematics", "Physics", "Chemistry", "English",
    "Computer Science", "Electronics",
    "Civil Engineering", "Mechanical Engineering", "Other"
]

PERIODS = [f"Period {i}" for i in range(1, 9)]

# ================= SIDEBAR =================
st.sidebar.title("Navigation")
menu = st.sidebar.selectbox("Select Page", [
    "➕ Add Student",
    "📝 Mark Attendance",
    "📊 View Records",
    "✏️ Modify Record",
    "🗑️ Delete Record"
])

# ================= ADD STUDENT =================
if menu == "➕ Add Student":
    st.title("➕ Add Student")

    student_name = st.text_input("Enter Student Name")

    if st.button("Save Student"):
        if student_name.strip():
            students_df = pd.read_csv(STUDENTS_FILE)
            if student_name.strip() in students_df["Student Name"].values:
                st.warning("Student already exists!")
            else:
                new_student = pd.DataFrame([[student_name.strip()]],
                                           columns=["Student Name"])
                new_student.to_csv(STUDENTS_FILE,
                                   mode='a', header=False, index=False)
                st.success("Student added successfully!")
                st.rerun()
        else:
            st.error("Please enter student name")

    st.subheader("Registered Students")
    students_df = pd.read_csv(STUDENTS_FILE)
    st.dataframe(students_df, use_container_width=True)


# ================= MARK ATTENDANCE =================
elif menu == "📝 Mark Attendance":
    st.title("📝 Mark Attendance")

    students_df = pd.read_csv(STUDENTS_FILE)
    students_list = students_df["Student Name"].tolist()

    if not students_list:
        st.warning("No students found. Add students first.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            student_name = st.selectbox("Select Student", students_list)
            subject = st.selectbox("Select Subject", SUBJECTS)

        with col2:
            period = st.selectbox("Select Period", PERIODS)
            att_date = st.date_input("Select Date", value=date.today())

        status = st.radio("Attendance Status",
                          ["Present", "Absent"],
                          horizontal=True)

        if st.button("Submit Attendance"):
            df = load_attendance()

            new_row = pd.DataFrame(
                [[str(att_date), student_name,
                  subject, period, status]],
                columns=df.columns
            )

            df = pd.concat([df, new_row], ignore_index=True)
            save_attendance(df)

            st.success("Attendance marked successfully!")


# ================= VIEW RECORDS =================
elif menu == "📊 View Records":
    st.title("📊 Attendance Records")

    df = load_attendance()

    if df.empty:
        st.warning("No attendance records available.")
    else:
        st.dataframe(df, use_container_width=True)

        st.subheader("Attendance Percentage")

        student_list = df["Student Name"].unique().tolist()
        student_filter = st.selectbox("Select Student", [""] + student_list)

        subject_filter = st.selectbox(
            "Select Subject (Optional)",
            ["All"] + SUBJECTS
        )

        if student_filter:
            filtered = df[df["Student Name"] == student_filter]

            if subject_filter != "All":
                filtered = filtered[
                    filtered["Subject"] == subject_filter
                ]

            if not filtered.empty:
                total = len(filtered)
                present = len(filtered[
                    filtered["Status"] == "Present"
                ])
                percentage = (present / total) * 100

                st.info(
                    f"Classes Attended: {present}/{total} | "
                    f"Attendance: {percentage:.2f}%"
                )
            else:
                st.warning("No records found for selection.")


# ================= MODIFY RECORD =================
elif menu == "✏️ Modify Record":
    st.title("✏️ Modify Record")

    df = load_attendance()

    if df.empty:
        st.warning("No records to modify.")
    else:
        st.dataframe(df, use_container_width=True)

        row_index = st.number_input(
            "Enter Row Number (starts from 0)",
            min_value=0,
            max_value=len(df) - 1,
            step=1
        )

        selected = df.iloc[int(row_index)]

        st.info(
            f"Editing: {selected['Student Name']} | "
            f"{selected['Subject']} | "
            f"{selected['Period']} | "
            f"{selected['Date']} | "
            f"{selected['Status']}"
        )

        col1, col2 = st.columns(2)

        with col1:
            new_student = st.text_input(
                "Student Name",
                value=selected["Student Name"]
            )

            new_subject = st.selectbox(
                "Subject",
                SUBJECTS,
                index=SUBJECTS.index(selected["Subject"])
                if selected["Subject"] in SUBJECTS else 0
            )

        with col2:
            new_period = st.selectbox(
                "Period",
                PERIODS,
                index=PERIODS.index(selected["Period"])
                if selected["Period"] in PERIODS else 0
            )

            try:
                new_date = st.date_input(
                    "Date",
                    value=datetime.strptime(
                        selected["Date"], "%Y-%m-%d"
                    ).date()
                )
            except:
                new_date = st.date_input("Date")

        new_status = st.radio(
            "Status",
            ["Present", "Absent"],
            index=0 if selected["Status"] == "Present" else 1,
            horizontal=True
        )

        if st.button("Save Changes"):
            df.at[int(row_index), "Student Name"] = new_student
            df.at[int(row_index), "Subject"] = new_subject
            df.at[int(row_index), "Period"] = new_period
            df.at[int(row_index), "Date"] = str(new_date)
            df.at[int(row_index), "Status"] = new_status

            save_attendance(df)
            st.success("Record updated successfully!")
            st.rerun()


# ================= DELETE RECORD =================
elif menu == "🗑️ Delete Record":
    st.title("🗑️ Delete Record")

    df = load_attendance()

    if df.empty:
        st.warning("No records to delete.")
    else:
        st.dataframe(df, use_container_width=True)

        row_index = st.number_input(
            "Enter Row Number (starts from 0)",
            min_value=0,
            max_value=len(df) - 1,
            step=1
        )

        selected = df.iloc[int(row_index)]

        st.error(
            f"Deleting: {selected['Student Name']} | "
            f"{selected['Subject']} | "
            f"{selected['Period']} | "
            f"{selected['Date']} | "
            f"{selected['Status']}"
        )

        if st.button("Confirm Delete"):
            df = df.drop(index=int(row_index)).reset_index(drop=True)
            save_attendance(df)
            st.success("Record deleted successfully!")
            st.rerun()
