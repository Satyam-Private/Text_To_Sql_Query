# Dynamic SQL Query Generator
# Author: Satyam Patil

from dotenv import load_dotenv
load_dotenv()  # Load environment variables

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Configure Gemini with API key
genai.configure(api_key=os.getenv('API_KEY'))

# Function to extract schema details
def get_db_schema(db_path):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        schema_info = ""
        
        for table in tables:
            table_name = table[0]
            c.execute(f"PRAGMA table_info({table_name});")
            columns = c.fetchall()
            schema_info += f"Table: {table_name}\nColumns: "
            schema_info += ", ".join([col[1] for col in columns]) + "\n"
        
        conn.close()
        return schema_info
    except sqlite3.Error as e:
        return f"Error fetching schema: {str(e)}"

# Function to interact with Gemini
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content([prompt, question])
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

# Streamlit UI
st.set_page_config(page_title="SQL Query Generator", page_icon="📊", layout="wide")
st.title("Dynamic SQL Query Generator with Gemini")

# Sidebar with instructions
st.sidebar.title("📌 Instructions")
st.sidebar.info("""
1. **Upload** an SQLite database file.
2. **Enter** a question in natural language.
3. Click **Generate Query** to see the SQL command.
4. The query is executed, and results are displayed.
""")

# Author Info in Sidebar with styling
st.sidebar.markdown("""
---
### 👨‍💻 Author: Satyam Patil
**[GitHub](https://github.com/Satyam-Private)** | **[LinkedIn](https://www.linkedin.com/in/patilsatyam)**
""", unsafe_allow_html=True)

# File uploader for database
uploaded_file = st.sidebar.file_uploader("Upload your SQLite database", type=["db", "sqlite"], help="Upload a .db or .sqlite file")

db_path = None
if uploaded_file is not None:
    db_path = "uploaded_db.db"  # Temporary storage path
    with open(db_path, "wb") as f:
        f.write(uploaded_file.read())
    
    # Extract schema information
    schema_info = get_db_schema(db_path)
    st.sidebar.text_area("📋 Extracted Database Schema:", schema_info, height=150, disabled=True)
    
    prompt = f"""
    You are an expert in converting English questions into SQL queries! The given database schema is:
    {schema_info}
    Convert the following English questions into SQL queries. Return only the SQL query.
    """

    # User input
    with st.form("query_form"):
        question = st.text_input("🔍 Enter your question here:", help="Type a natural language question about your database")
        submit = st.form_submit_button("🚀 Generate Query")

    if submit and question.strip():
        with st.spinner("Generating SQL query..."):
            sql_query = get_gemini_response(question, prompt)
        
        st.subheader("📝 Generated SQL Query:")
        st.code(sql_query, language="sql")
        
        with st.spinner("Executing SQL query..."):
            data = read_sql_query(sql_query, db_path)
        
        if isinstance(data, str) and "Error" in data:
            st.error(data)
        else:
            st.subheader("📊 Query Results:")
            if data:
                st.write("### 📌 Results Table:")
                st.dataframe(data)
            else:
                st.info("No results found for the query.")
else:
    st.warning("⚠️ Please upload a SQLite database to proceed.")
