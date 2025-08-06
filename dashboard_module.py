
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show_hr_dashboard():
    df = pd.read_excel("Mass file - To be used for Dashboard.xlsx")
    df.columns = df.columns.str.strip().str.upper()

    st.title("📊 HR Insights Dashboard")
    question = st.selectbox("Select a question to explore:", [
        "Employee count by age group",
        "Employee count by nationality",
        "Employee count by job title",
        "Employee count by company (entity)",
        "Employee count by band",
        "Employee count by grade",
        "Employee count by contract type"
    ])

    if question == "Employee count by age group":
        bins = [18, 25, 35, 45, 55, 65, 100]
        labels = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
        df['AGE GROUP'] = pd.cut(df['AGE'], bins=bins, labels=labels, right=False)
        counts = df['AGE GROUP'].value_counts().sort_index()
        counts.plot(kind='bar')
        plt.title("Employee Count by Age Group")
        plt.xlabel("Age Group")
        plt.ylabel("Count")
        st.pyplot(plt)

    elif question == "Employee count by nationality":
        counts = df['NATIONALITY'].value_counts().head(20)
        counts.plot(kind='bar')
        plt.title("Top 20 Nationalities")
        plt.xlabel("Nationality")
        plt.ylabel("Count")
        st.pyplot(plt)

    elif question == "Employee count by job title":
        counts = df['JOB TITLE'].value_counts().head(20)
        counts.plot(kind='bar')
        plt.title("Top 20 Job Titles")
        plt.xlabel("Job Title")
        plt.ylabel("Count")
        st.pyplot(plt)

    elif question == "Employee count by company (entity)":
        counts = df['ENTITY'].value_counts()
        counts.plot(kind='bar')
        plt.title("Employees by Company (Entity)")
        plt.xlabel("Company")
        plt.ylabel("Count")
        st.pyplot(plt)

    elif question == "Employee count by band":
        counts = df['BAND'].value_counts().sort_index()
        counts.plot(kind='bar')
        plt.title("Employee Count by Band")
        plt.xlabel("Band")
        plt.ylabel("Count")
        st.pyplot(plt)

    elif question == "Employee count by grade":
        counts = df['GRADE'].value_counts().sort_index()
        counts.plot(kind='bar')
        plt.title("Employee Count by Grade")
        plt.xlabel("Grade")
        plt.ylabel("Count")
        st.pyplot(plt)

    elif question == "Employee count by contract type":
        counts = df['CONTRACT TYPE'].value_counts()
        counts.plot(kind='bar')
        plt.title("Employees by Contract Type")
        plt.xlabel("Contract Type")
        plt.ylabel("Count")
        st.pyplot(plt)
