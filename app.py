import streamlit as st
import pandas as pd
from src.ollama import call_ollama
from src.executor import execute_code, clean_code
from src.preprocessor import preprocess_dates
from src.output_handler import create_prompt
from src.output_handler import detect_output_type
from src.output_handler import extract_plot
from src.output_handler import extract_table
from src.output_handler import extract_text

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
    
        st.dataframe(df.head(100), width='stretch')
        
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
            "Ask a question about the data",
            placeholder="e.g., What is the average sales by region?",
            label_visibility="collapsed"
        )
    with col2:
        ask_button = st.button("Ask", type="primary", width='stretch')

    if ask_button and question:
        output_types = detect_output_type(question)

        prompt = create_prompt(question, df, output_types)
        
        with st.spinner("Analyzing data..."):
            code = call_ollama(prompt)
        
        code = clean_code(code)

        with st.spinner("Executing analysis..."):
            output, env = execute_code(code, df)

        st.markdown("### Result")

        if output_types['text']:
            st.markdown(extract_text(output))
            
        if output_types['graph']:
            plot_bytes = extract_plot(env)
            if plot_bytes:
                st.image(plot_bytes)
            else:
                st.warning("No graph generated.")

        if output_types['table']:
            table = extract_table(env)
            if table is not None:
                st.dataframe(table)
            else:
                st.warning("No table generated.")

        with st.expander("Generated Code", expanded=False):
            st.code(code, language='python')

else:
    st.stop()