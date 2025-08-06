import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def load_dashboard_data():
    return pd.read_excel("data/Mass file - To be used for Dashboard.xlsx")

def show_dashboard(df, prompt):
    if "age" in prompt:
        st.subheader("Age Distribution")
        df['Age'].hist(bins=10)
        st.pyplot(plt.gcf())
        plt.clf()
    elif "nationality" in prompt:
        st.subheader("Employees by Nationality")
        df['Nationality'].value_counts().plot(kind='bar')
        st.pyplot(plt.gcf())
        plt.clf()
    elif "job title" in prompt:
        st.subheader("Employees by Job Title")
        df['Job Title'].value_counts().head(10).plot(kind='barh')
        st.pyplot(plt.gcf())
        plt.clf()
