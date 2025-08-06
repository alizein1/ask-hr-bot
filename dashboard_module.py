
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ace_tools as tools

def show_hr_dashboard(data, prompt):
    if "age" in prompt:
        data["Age Group"] = pd.cut(data["Age"], bins=[18, 25, 35, 45, 55, 65], labels=["18-25", "26-35", "36-45", "46-55", "56-65"])
        chart = data["Age Group"].value_counts().sort_index().plot(kind='bar', title="Employee Count by Age Group")
        st.pyplot(chart.get_figure())

    elif "nationality" in prompt:
        chart = data["Nationality"].value_counts().plot(kind='barh', title="Employees by Nationality")
        st.pyplot(chart.get_figure())

    elif "gender" in prompt:
        chart = data["Gender"].value_counts().plot(kind='pie', title="Gender Distribution", autopct='%1.1f%%')
        st.pyplot(chart.get_figure())

    elif "grade" in prompt:
        chart = data["Grade"].value_counts().plot(kind='bar', title="Employees by Grade")
        st.pyplot(chart.get_figure())

    elif "band" in prompt:
        chart = data["Band"].value_counts().plot(kind='bar', title="Employees by Band")
        st.pyplot(chart.get_figure())

    elif "title" in prompt:
        chart = data["Job Title"].value_counts().nlargest(15).plot(kind='barh', title="Top 15 Job Titles")
        st.pyplot(chart.get_figure())

    elif "company" in prompt:
        chart = data["Company"].value_counts().plot(kind='bar', title="Employees by Company")
        st.pyplot(chart.get_figure())

    else:
        st.warning("Dashboard category not recognized. Try asking about age, nationality, gender, title, grade, band, or company.")
