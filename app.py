from dotenv import load_dotenv
load_dotenv()  # Load environment variables

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

genai.configure(api_key=os.getenv('API_KEY'))

# Function to interact with Gemini
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content([prompt[0], question])
    sql_query = response.text.strip()  # Extract text properly
    return sql_query.strip("```").strip("sql")

# Function to execute SQL queries
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute(sql)
        rows = c.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        return f"Error: {str(e)}"

prompt = [
    """
    You are an expert in converting English questions to SQL query! The SQL database is named STUDENT and has the following columns: NAME, CLASS, MARKS. 
    
    Examples: 
    - "How many entries are present?" → `SELECT COUNT(*) FROM STUDENT;`
    - "Students in class X?" → `SELECT * FROM STUDENT WHERE CLASS = 'X';`
    - "Top scorer?" → `SELECT NAME FROM STUDENT WHERE MARKS = (SELECT MAX(MARKS) FROM STUDENT);`
    
    Convert the following English questions into SQL queries. Return only the SQL query.
    """
]

# Enhanced frontend using Streamlit
st.set_page_config(page_title="SQL Query Generator", page_icon="📊", layout="centered")

# Sidebar with instructions
st.sidebar.title("Instructions")
st.sidebar.info("""
1. **Enter** an English question related to SQL queries.
2. Click on **Generate Query** to see the generated SQL command.
3. The query will be executed on the **STUDENT** database.
4. View the output below for query results.
""")

# Main app title and description
st.title("Gemini-Powered SQL Query Generator")
st.markdown("""
This application uses Google's Gemini model to convert natural language questions into SQL queries.  
It then executes the generated query on a local **STUDENT** database with columns **NAME**, **CLASS**, and **MARKS**.
""")

# Input form container
with st.form("query_form"):
    question = st.text_input("Enter your question here:")
    submit = st.form_submit_button("Generate Query")

if submit:
    if question.strip():
        with st.spinner("Generating SQL query..."):
            sql_query = get_gemini_response(question, prompt)
        st.subheader("Generated SQL Query:")
        st.code(sql_query, language="sql")
        
        with st.spinner("Executing SQL query..."):
            data = read_sql_query(sql_query, "data.db")
        
        if isinstance(data, str) and "Error" in data:
            st.error(data)  # Show error message if SQL fails
        else:
            st.subheader("Query Results:")
            if data:
                for row in data:
                    st.write(row)
            else:
                st.info("No results found for the query.")
    else:
        st.warning("Please enter a valid question.")
