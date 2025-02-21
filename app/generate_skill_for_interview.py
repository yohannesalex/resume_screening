import json
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from screening import balance_braces


load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables!")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# function to identify the weights
import re
import json

def analyse_job_skills(job_requirement_text):
    prompt = (
        '{'
        '"You are a helpful assistant that extracts and categorizes skills from a given job_requirement_text. '
        'Your task is to analyze the job_requirement_text and identify the top 5 most relevant skills. '
        'For each skill, determine the required proficiency level as either "beginner", "intermediate", or "expert" '
        'based on the context. Return the response in JSON format, with each skill as a key and its required level as '
        'a value in a nested dictionary. Use the following structure:'
        '\n\n'
        '{'
        '  "skill_name": {'
        '    "required_level": "beginner/intermediate/expert"'
        '  }'
        '}'
        '\n\n'
        f'Here is the job_requirement_text to analyze:\n{job_requirement_text}\n\n'
        'Provide only the JSON output. Do not include any additional explanations or text.'
        '}'
    )

    # Generate content from the model
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.95,
        }
    )

    # Extract JSON response
    response_text = response.text.replace('```json', '').replace('```', '').strip()

    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        json_str = match.group(0)
    else:
        raise ValueError("No valid JSON object found in the response.")

    json_str = balance_braces(json_str)

    try:
        result = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}\nExtracted text: {json_str}")

    return result
