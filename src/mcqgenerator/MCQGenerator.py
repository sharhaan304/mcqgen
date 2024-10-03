import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.logger import logging

# Import necessary packages from langchain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain  # Use LLMChain for chaining prompts

# Load environment variables
load_dotenv()
key = os.getenv("OPENAI_API_KEY")

# Initialize the LLM (OpenAI API)
llm = ChatOpenAI(openai_api_key=key, model_name="gpt-3.5-turbo", temperature=0.7)

# Define the template for quiz generation
quiz_generation_template = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to conform to the text as well.
Make sure to format your response like the RESPONSE_JSON below and use it as a guide. \
Ensure to make {number} MCQs.
### RESPONSE_JSON
{response_json}
"""

# Create the quiz generation prompt
quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],  # Fixed `input_variables`
    template=quiz_generation_template
)

# Define the template for quiz evaluation
quiz_evaluation_template = """
You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students,\
you need to evaluate the complexity of the question and give a complete analysis of the quiz. Use at most 50 words for complexity analysis. 
If the quiz is not up to par with the cognitive and analytical abilities of the students,\
update the quiz questions which need to be changed, and change the tone such that it perfectly fits the student abilities.
Quiz_MCQs:
{quiz}
Check from an expert English writer of the above quiz:
"""

# Create the quiz evaluation prompt
quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],  # Correct `input_variables`
    template=quiz_evaluation_template
)

# Chain the prompts with LLM using LLMChain for sequential operations
quiz_chain = LLMChain(llm=llm, prompt=quiz_generation_prompt)
review_chain = LLMChain(llm=llm, prompt=quiz_evaluation_prompt)

# Overall process chain
def generate_evaluate_chain(text, number, subject, tone, response_json):
    try:
        # First, generate the quiz
        quiz_result = quiz_chain.run({
            "text": text,
            "number": number,
            "subject": subject,
            "tone": tone,
            "response_json": response_json
        })

        # Then, evaluate the generated quiz
        review_result = review_chain.run({
            "subject": subject,
            "quiz": quiz_result
        })

        # Log the results
        logging.info(f"Quiz generated: {quiz_result}")
        logging.info(f"Review generated: {review_result}")

        # Return both results
        return {
            "quiz": quiz_result,
            "review": review_result
        }

    except Exception as e:
        logging.error(f"Error during quiz generation/evaluation: {e}")
        traceback.print_exc()
        return None
