import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def load_dashboard_data():
    df = pd.read_excel("data/Mass file - To be used for Dashboard.xlsx")
    df.columns = df.columns.str.strip()
    return df

def show_dashboard(df, prompt):
    prompt = prompt.lower()

    if "entity" in prompt:
        st.subheader("Employees by Entity")
        df['Entity'].value_counts().plot(kind='bar')
        st.pyplot(plt.gcf())
        plt.clf()

    if "gender" in prompt:
        st.subheader("Employees by Gender per Entity")
        grouped = df.groupby(['Entity', 'Gender']).size().unstack(fill_value=0)
        st.dataframe(grouped)
        grouped.plot(kind='bar', stacked=True)
        plt.title("Gender Distribution per Entity")
        st.pyplot(plt.gcf())
        plt.clf()

    if "nationalit" in prompt:
        st.subheader("Employees by Nationality per Entity")
        grouped = df.groupby(['Entity', 'Nationality']).size().unstack(fill_value=0)
        st.dataframe(grouped)
        grouped.plot(kind='bar', stacked=True)
        plt.title("Nationality Distribution per Entity")
        st.pyplot(plt.gcf())
        plt.clf()

    if "age" in prompt:
        st.subheader("Age Distribution per Entity")
        df['Age Group'] = pd.cut(df['Age'], bins=[18, 25, 35, 45, 55, 70], labels=["18-25", "26-35", "36-45", "46-55", "56+"])
        grouped = df.groupby(['Entity', 'Age Group']).size().unstack(fill_value=0)
        st.dataframe(grouped)
        grouped.plot(kind='bar', stacked=True)
        plt.title("Age Group Distribution per Entity")
        st.pyplot(plt.gcf())
        plt.clf()

    if "band" in prompt:
        st.subheader("Employees by Band per Entity")
        grouped = df.groupby(['Entity', 'Band']).size().unstack(fill_value=0)
        st.dataframe(grouped)
        grouped.plot(kind='bar', stacked=True)
        plt.title("Bands per Entity")
        st.pyplot(plt.gcf())
        plt.clf()

    if "grade" in prompt:
        st.subheader("Employees by Grade per Entity")
        grouped = df.groupby(['Entity', 'Grade']).size().unstack(fill_value=0)
        st.dataframe(grouped)
        grouped.plot(kind='bar', stacked=True)
        plt.title("Grades per Entity")
        st.pyplot(plt.gcf())
        plt.clf()

    if "job title" in prompt:
        st.subheader("Top Job Titles per Entity")
        grouped = df.groupby(['Entity', 'Job Title']).size().unstack(fill_value=0)
        st.dataframe(grouped)
        grouped.T.head(10).plot(kind='bar', stacked=True)
        plt.title("Top Job Titles per Entity")
        st.pyplot(plt.gcf())
        plt.clf()

def show_employee_details(df, prompt):
    name_matches = df[df['Full Name'].str.lower().str.contains(prompt.lower(), na=False)]
    if not name_matches.empty:
        st.table(name_matches)
    else:
        st.warning("No employee found matching the name.")
