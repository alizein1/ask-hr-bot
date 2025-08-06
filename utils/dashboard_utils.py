import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def load_dashboard_data():
    return pd.read_excel("data/Mass file - To be used for Dashboard.xlsx")

def show_dashboard(df, prompt):
    prompt = prompt.lower()
    if "age" in prompt:
        st.subheader("Age Distribution")
        df['Age'].dropna().astype(int).hist(bins=10)
        st.pyplot(plt.gcf())
        plt.clf()
elif "nationalit" in prompt:
    st.subheader("Employees by Nationality")

    if 'Nationality' in df.columns:
        df['Nationality'] = df['Nationality'].astype(str).str.strip().str.upper()
        nationality_counts = df['Nationality'].value_counts()

        st.write(nationality_counts)
        nationality_counts.plot(kind='bar')
        st.pyplot(plt.gcf())
        plt.clf()
    else:
        st.error("❌ 'Nationality' column not found in the file.")

        st.pyplot(plt.gcf())
        plt.clf()
    elif "gender" in prompt:
        st.subheader("Employees by Gender")
        df['Gender'].value_counts().plot(kind='bar')
        st.pyplot(plt.gcf())
        plt.clf()
    elif "job title" in prompt:
        st.subheader("Top 10 Job Titles")
        df['Job Title'].value_counts().head(10).plot(kind='barh')
        st.pyplot(plt.gcf())
        plt.clf()
    elif "band" in prompt:
        st.subheader("Employees by Band")
        df['Band'].value_counts().plot(kind='bar')
        st.pyplot(plt.gcf())
        plt.clf()
    elif "grade" in prompt:
        st.subheader("Employees by Grade")
        df['Grade'].value_counts().plot(kind='bar')
        st.pyplot(plt.gcf())
        plt.clf()
