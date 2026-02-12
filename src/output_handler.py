import io
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Optional

def detect_output_type(question: str) -> Dict[str, bool]:
    question_lower = question.lower()

    graph_keywords = [
        'plot', 'graph', 'chart', 'visualize', 'visualization', 
        'distribution', 'trend', 'histogram', 'scatter', 'line chart',
        'bar chart', 'pie chart', 'box plot', 'show me', 'display'
    ]
    table_keywords = [
        'table', 'list', 'show all', 'display all', 'top', 'bottom',
        'rows', 'records', 'entries', 'breakdown', 'group by', 'summary'
    ]

    needs_graph = any(keyword in question_lower for keyword in graph_keywords)
    needs_table = any(keyword in question_lower for keyword in table_keywords)  
    
    return {
        'graph': needs_graph,
        'table': needs_table,
        'text' : True
    }
    
def create_prompt(question: str, df: pd.DataFrame, output_types: Dict[str, bool]) -> str:
    schema_info = df.dtypes.to_string()
    sample_data = df.head().to_string()

    column_list = ", ".join(df.columns.tolist())
    output_instructions = []

    if output_types['graph']:
        output_instructions.append("""
## GRAPH REQUIREMENT:
- Import: matplotlib.pyplot as plt (already available)
- Create figure: plt.figure(figsize=(10, 6))
- Create your visualization (bar, line, scatter, etc.)
- Add labels: plt.xlabel(), plt.ylabel(), plt.title()
- Apply layout: plt.tight_layout()
- DO NOT call plt.show()
""")
        
    if output_types['table']:
        output_instructions.append("""
## TABLE REQUIREMENT:
- Create a pandas DataFrame with your results
- Assign it to variable: result_table = your_dataframe
- Limit to maximum 20 rows
- Use descriptive column names
""")
    
    output_instructions.append("""
## TEXT INSIGHTS REQUIREMENT (MANDATORY):
- Use print() statements ONLY for all text output
- Provide clear explanation of findings
- Include specific numbers, percentages, or statistics
- Format: print("Your insight here")
- Example: print(f"The average sales is {avg:.2f} million")
""")

    prompt = f"""
You are a Python code generator for data analysis. Your task is to generate PURE Python code that can be executed directly.

<DATASET_INFO>
Columns available:
{column_list}

Data types:
{schema_info}

Sample rows:
{sample_data}
</DATASET_INFO>

<USER_QUESTION>
{question}
</USER_QUESTION>

<OUTPUT_REQUIREMENTS>
{''.join(output_instructions)}
</OUTPUT_REQUIREMENTS>

<CRITICAL_RULES>
1. OUTPUT ONLY EXECUTABLE PYTHON CODE - Nothing else!
2. NO markdown formatting (no ```, no **bold**, no *italic*)
3. NO explanatory text outside of print() statements
4. NO sentences like "This code does..." or "Here's what..." at the end
5. Use ONLY these available imports: pandas (as pd), matplotlib.pyplot (as plt)
6. The DataFrame is already loaded as variable: df
7. Use EXACT column names from the dataset (case-sensitive)
8. For graphs: DO NOT use plt.show()
9. ALL text must be inside print() statements
10. End your code after the last Python statement - NO additional explanation
</CRITICAL_RULES>

<CODE_STRUCTURE_TEMPLATE>
# Step 1: Import necessary modules (if needed beyond pd, plt)
# Step 2: Filter/process the data
# Step 3: Perform calculations
# Step 4: Print insights using print() statements
# Step 5: Create graph (if required)
# Step 6: Store table in result_table (if required)
</CODE_STRUCTURE_TEMPLATE>

<EXAMPLES_OF_CORRECT_OUTPUT>
Example 1 (Simple analysis):
# Calculate average
avg_sales = df['Global_Sales'].mean()
print(f"Average global sales: {{avg_sales:.2f}} million")
print(f"Total games in dataset: {{len(df)}}")

Example 2 (With graph):
top_5 = df.nlargest(5, 'Global_Sales')
print("Top 5 games by sales:")
for idx, row in top_5.iterrows():
    print(f"  {{row['Name']}}: {{row['Global_Sales']:.2f}}M")

plt.figure(figsize=(10, 6))
plt.bar(top_5['Name'], top_5['Global_Sales'])
plt.xlabel('Game')
plt.ylabel('Sales (Million)')
plt.title('Top 5 Games')
plt.xticks(rotation=45)
plt.tight_layout()
</EXAMPLES_OF_CORRECT_OUTPUT>

Now generate ONLY the Python code to answer the user's question. Start with imports or data processing - NO introductory text:"""
    return prompt

def extract_plot(env: Dict) -> Optional[bytes]:
    try:
        fig = plt.gcf()
        if fig.get_axes():
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            plt.close(fig)
            return buf.getvalue()
    except Exception as e:
        print(f"Error extracting plot: {e}")
    
    return None

def extract_table(env: Dict) -> Optional[pd.DataFrame]:
    if 'result_table' in env and isinstance(env['result_table'], pd.DataFrame):  
        return env.get('result_table')
    return None

def extract_text(output: str) -> str:
    if not output.strip():
        return "No insights generated."
    return output.strip()