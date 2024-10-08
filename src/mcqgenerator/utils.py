import os
import PyPDF2
import json
import traceback

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            return text
            
        except Exception as e:
            raise Exception("error reading the PDF file")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception(
            "unsupported file format only pdf and text file suppoted"
            )

def get_table_data(quiz_data):
    try:
        # Check if input is a string and convert to dictionary if needed
        if isinstance(quiz_data, str):
            quiz_data = json.loads(quiz_data)
        
        quiz_table_data = []
        
        # Iterate over the quiz dictionary and extract the required information
        for key, value in quiz_data.items():
            if isinstance(value, dict) and "mcq" in value:  # Process only valid MCQs
                mcq = value.get("mcq", "")
                options = " || ".join(
                    [f"{option} -> {option_value}" for option, option_value in value.get("options", {}).items()]
                )
                correct = value.get("correct", "")
                
                quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})
            else:
                print(f"Skipping invalid entry for key {key}: value is not a dictionary or missing 'mcq'.")
        
        return quiz_table_data
        
    except json.JSONDecodeError:
        # Return an error message instead of using st.error()
        return "Invalid JSON format."
    except KeyError as e:
        # Return an error message
        return f"Missing expected key in quiz data: {e}"
    except Exception as e:
        # Return a general error message
        return f"An unexpected error occurred: {e}"