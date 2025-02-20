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
def analyse_job_skills(job_requirement_text):
    prompt = f"""
Analyze this job requirement and output a JSON dictionary of required skills categorized by importance (High/Medium/Low). Follow these rules:  
1. High = Explicitly required or repeated  
2. Medium = Mentioned as "preferred" or "nice-to-have"  
3. Low = Implied by context but not directly stated  
4. Use simple skill names (e.g., "Python" not "Python programming")  
5. Exclude generic terms like "communication skills"  
6. Output only raw JSON without formatting  
7. Return valid JSON only (no markdown or additional text)

Example Input:  
"Looking for a developer with Python expertise, basic SQL knowledge, and REST API experience. Docker experience preferred."  

Example Output:  
{{"Python": "High", "SQL": "Medium", "REST APIs": "High", "Docker": "Medium"}}  

Job Requirement to Analyze:  
{job_requirement_text}
"""

    # Rest of your code remains the same
    response = model.generate_content(
        prompt, 
        generation_config={
            "temperature": 0.1,
            "top_p": 0.95,
        }
    )
    
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