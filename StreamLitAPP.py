import os
import json
import traceback
from numpy import number
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data  # Custom utility functions
import streamlit as st

# Import the updated callback manager from langchain_community
from langchain_community.callbacks.manager import get_openai_callback

# Import custom functions and logger from your project
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

# Ensure you are using the right chain handler for LangChain
from langchain.chains import SequentialChain  # Updated import for chaining prompts (replace SequentialChain)

# Load the response JSON from the file
with open('C:/Users/Asus/mcqgen/Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)
    
st.title("MCQ creator Application with Langchain")

# Create a form to get user inputs
with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload the text file or PDF file", type=["pdf", "txt"])
    
    mcq_count = st.number_input("Enter the number of MCQs to generate", min_value=3, max_value=20)
    
    subject = st.text_input("Enter the subject", max_chars=50, placeholder="e.g., Physics, Math")
    
    tone = st.text_input("Complexity level of Questions", max_chars=20, placeholder="easy, medium, hard")
    
    button = st.form_submit_button("Generate MCQs")
    
    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("Loading..."):
            try:
                # Read the uploaded file (text or PDF)
                text = read_file(uploaded_file)
                
                # Start the OpenAI callback for tracking tokens
                with get_openai_callback() as cb:
                    # Call generate_evaluate_chain with individual arguments
                    response = generate_evaluate_chain(
                        text=text,
                        number=mcq_count,
                        subject=subject,
                        tone=tone,
                        response_json=RESPONSE_JSON
                    )
                    
            except Exception as e:
                # Display the error and print the traceback
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("An error occurred while generating MCQs.")
                
            else:
                # Display token usage and cost
                st.write(f"Total Tokens: {cb.total_tokens}")
                st.write(f"Prompt Tokens: {cb.prompt_tokens}")
                st.write(f"Completion Tokens: {cb.completion_tokens}")
                st.write(f"Total Cost: ${cb.total_cost:.4f}")
                
                # If response is a dict, extract quiz and review data
                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        # Debugging: Display the raw quiz data
                        st.write("Quiz data:", quiz)  
                        
                        # Convert the quiz data to a DataFrame
                        table_data = get_table_data(quiz)

                        if isinstance(table_data, str):
            # If table_data is an error message, display it
                            st.error(table_data)
                        elif table_data:  # Check if table_data is valid and not empty
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            
                            # Display the review section
                            st.text_area(label="Review", value=response.get("review", ""))
                        else:
                            st.error("Error processing the table data.")
                    else:
                        st.error("No quiz data found in the response.")
                else:
                    st.write(response)
