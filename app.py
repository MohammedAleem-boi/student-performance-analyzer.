import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Student Performance Analyzer",
    page_icon="🎓",
    layout="wide"
)

# ---------- Dark purple styling ----------
st.markdown("""
<style>
.stApp { background: #0b1120; color: #f8fafc; }
[data-testid="stSidebar"] { background: #111827; }
.block-container { padding-top: 2rem; }
div[data-testid="stMetric"] {
    background: #1f2937; padding: 18px 20px;
    border-radius: 14px; border-left: 4px solid #8b5cf6;
}
div[data-testid="stMetric"] label { color: #cbd5e1 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #c4b5fd !important;
}
h1, h2, h3 { color: #c4b5fd !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Student Performance Analyzer")
st.caption("Academic data analytics | Python • Pandas • Plotly")

# ---------- Sample data ----------
sample_data = pd.DataFrame({
    "Name": ["Aleem", "Rahul", "Sam", "John", "Arun"],
    "Python": [85, 65, 90, 75, 80],
    "Maths": [70, 80, 95, 60, 85],
    "AI": [90, 75, 88, 85, 95]
})

# ---------- Sidebar: data source ----------
st.sidebar.header("📂 Data input")
source = st.sidebar.radio(
    "Choose your data source",
    ["Use sample data", "Upload CSV or Excel"]
)

if source == "Upload CSV or Excel":
    uploaded_file = st.sidebar.file_uploader(
        "Upload a CSV or Excel file",
        type=["csv", "xlsx"]
    )
    if uploaded_file is None:
        st.info("Upload a CSV or Excel file in the sidebar, or choose 'Use sample data'.")
        st.stop()
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"Could not read the file: {exc}")
        st.stop()
else:
    raw_df = sample_data.copy()

# ---------- Validate and clean data ----------
required_columns = ["Name", "Python", "Maths", "AI"]
missing_columns = [col for col in required_columns if col not in raw_df.columns]

if missing_columns:
    st.error(
        "Your file is missing these required columns: "
        + ", ".join(missing_columns)
        + ". Required column names: Name, Python, Maths, AI."
    )
    st.stop()

df = raw_df[required_columns].copy()
df["Name"] = df["Name"].astype("string").str.strip()

for subject in ["Python", "Maths", "AI"]:
    df[subject] = pd.to_numeric(df[subject], errors="coerce")

df = df.dropna(subset=required_columns)
df = df[df["Name"].str.len() > 0]

if df.empty:
    st.error("There are no valid student rows to analyze.")
    st.stop()

if ((df[["Python", "Maths", "AI"]] < 0) |
    (df[["Python", "Maths", "AI"]] > 100)).any().any():
    st.warning("Some marks are outside the expected 0–100 range. Please check your data.")

df["Total"] = df[["Python", "Maths", "AI"]].sum(axis=1)
df["Average"] = (df["Total"] / 3).round(2)

subject_avg = df[["Python", "Maths", "AI"]].mean()
class_average = round(df["Average"].mean(), 2)
topper_row = df.loc[df["Total"].idxmax()]
lowest_row = df.loc[df["Total"].idxmin()]

# ---------- Top summary cards ----------
st.subheader("📊 Class overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total students", len(df))
c2.metric("Class average", f"{class_average}%")
c3.metric("Class topper", str(topper_row["Name"]))
c4.metric("Highest total", f'{int(topper_row["Total"])}/300')

# ---------- Graphs ----------
st.subheader("📈 Performance analytics")
left, right = st.columns(2)

with left:
    subject_chart = px.bar(
        x=subject_avg.index,
        y=subject_avg.values,
        text=subject_avg.round(1).values,
        color=subject_avg.index,
        color_discrete_sequence=["#8b5cf6", "#06b6d4", "#a78bfa"],
        labels={"x": "Subject", "y": "Average marks"},
        title="Subject-wise average"
    )
    subject_chart.update_traces(textposition="outside")
    subject_chart.update_layout(
        template="plotly_dark", paper_bgcolor="#1f2937",
        plot_bgcolor="#1f2937", font_color="#f8fafc",
        showlegend=False, yaxis_range=[0, 110],
        margin=dict(l=15, r=15, t=55, b=15), height=360
    )
    st.plotly_chart(subject_chart, use_container_width=True)

with right:
    student_chart = px.bar(
        df, x="Name", y="Total", text="Total",
        color="Total", color_continuous_scale=["#4338ca", "#a78bfa"],
        title="Student-wise total marks",
        labels={"Name": "Student", "Total": "Total marks"}
    )
    student_chart.update_traces(textposition="outside")
    student_chart.update_layout(
        template="plotly_dark", paper_bgcolor="#1f2937",
        plot_bgcolor="#1f2937", font_color="#f8fafc",
        coloraxis_showscale=False,
        margin=dict(l=15, r=15, t=55, b=15), height=360
    )
    st.plotly_chart(student_chart, use_container_width=True)

# ---------- Subject insights ----------
st.subheader("💡 Performance insights")
best_subject = subject_avg.idxmax()
weak_subject = subject_avg.idxmin()
i1, i2, i3 = st.columns(3)
i1.info(f"🏆 Strongest subject: **{best_subject}** ({subject_avg[best_subject]:.1f})")
i2.warning(f"📌 Subject to review: **{weak_subject}** ({subject_avg[weak_subject]:.1f})")
i3.success(f"⭐ Top student: **{topper_row['Name']}** ({int(topper_row['Total'])}/300)")

# ---------- Student selector ----------
st.subheader("👤 Individual student report")
student_names = df["Name"].astype(str).tolist()
selected_name = st.selectbox("Choose a student", student_names)
student = df[df["Name"].astype(str) == selected_name].iloc[0]

s1, s2, s3 = st.columns(3)
s1.metric("Total marks", f'{int(student["Total"])}/300')
s2.metric("Average", f'{student["Average"]:.2f}%')
s3.metric("Class position", f'{int(df["Total"].rank(ascending=False, method="min").loc[student.name])} of {len(df)}')

student_subjects = pd.DataFrame({
    "Subject": ["Python", "Maths", "AI"],
    "Marks": [student["Python"], student["Maths"], student["AI"]]
})
individual_chart = px.bar(
    student_subjects, x="Subject", y="Marks",
    color="Subject", text="Marks",
    color_discrete_sequence=["#8b5cf6", "#06b6d4", "#a78bfa"],
    title=f"{selected_name}'s subject marks"
)
individual_chart.update_traces(textposition="outside")
individual_chart.update_layout(
    template="plotly_dark", paper_bgcolor="#0b1120",
    plot_bgcolor="#1f2937", font_color="#f8fafc",
    showlegend=False, yaxis_range=[0, 110], height=320
)
st.plotly_chart(individual_chart, use_container_width=True)

# ---------- Data table and download ----------
st.subheader("📋 Analyzed student records")
st.dataframe(df, use_container_width=True, hide_index=True)

csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download analyzed results (CSV)",
    data=csv_data,
    file_name="student_performance_results.csv",
    mime="text/csv"
)

st.caption("Student Performance Analyzer • Built with Streamlit, Pandas and Plotly")
