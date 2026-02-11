import streamlit as st
import pandas as pd
from src.ollama import call_ollama
from src.executor import execute_code, clean_code
from src.preprocessor import preprocess_dates

st.set_page_config(
    page_title="Autonomous Data Analyst",
    page_icon="🤖",
    layout="wide")

st.markdown('<h1 style="text-align: center;">Autonomous Data Analyst</h1>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], help="Upload a CSV file to start analyze")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding='latin1')
    
    df = preprocess_dates(df)

    with st.expander("Dataset Overview", expanded=False):
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", f"{len(df):,}")
        col2.metric("Total Columns", len(df.columns))
        col3.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:,.2f} MB")
    
        st.dataframe(df.head(100))
        
        st.markdown("**Numeric Columns Summary:**")
        numeric_cols = df.select_dtypes(include="number").columns
        if not numeric_cols.empty:
            st.dataframe(df[numeric_cols].describe(), width='stretch')

        st.markdown("**Categorical Columns Summary:**")
        categorical_cols = df.select_dtypes(include="object").columns
        if not categorical_cols.empty: 
            cat_summary = pd.DataFrame({
                "Unique Values": [df[col].nunique() for col in categorical_cols],
                "Most Frequent": [df[col].mode()[0] for col in categorical_cols],
                "Frequency": [df[col].value_counts().iloc[0] for col in categorical_cols]
            }, index=categorical_cols)
            st.dataframe(cat_summary, width='stretch')

    st.markdown("---")

    col1, col2 = st.columns([4, 1])
    with col1:
        question = st.text_input(
            "Ask a quick question about the data",
            placeholder="e.g., What is the average sales by region?",
            label_visibility="collapsed"
        )
    with col2:
        ask_button = st.button("Ask", type="primary", width='stretch')

    if ask_button and question:
        prompt = f"""
You are a professional data analyst.

Dataset schema:
{df.dtypes}

Sample data:
{df.head().to_string()}

User question:
"{question}"

Your task:
1. Think step by step.
2. Write Python code using pandas.
3. Print the final answer clearly.
4. DO NOT explain the code.
5. ONLY output Python code.

Assume the dataframe is named df.
"""
        with st.spinner("Analyzing data..."):
            code = call_ollama(prompt)
        
        code = clean_code(code)
        output, env = execute_code(code, df)

        st.markdown("### Result")
        st.text(output)
else:
    st.stop()