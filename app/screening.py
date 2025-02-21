import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from generate_job_requirement_values import analyze_job_requirements
from file_reader import extract_text_from_file
from vector_keyword_similarity import calculate_scores
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables!")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")


import json
import re

def balance_braces(json_str):
    """
    Count the number of opening and closing braces.
    If there are missing closing braces, append them to the end of the string.
    """
    open_braces = json_str.count('{')
    close_braces = json_str.count('}')
    if open_braces > close_braces:
        json_str += '}' * (open_braces - close_braces)
    return json_str
# function to score the resume
def scoreResume(requirement_text, resume_file_path):
    # Extract text from the file using appropriate library
    extracted_applicant_resume = extract_text_from_file(resume_file_path)
    weight = analyze_job_requirements(requirement_text)
    scores = calculate_scores(requirement_text, extracted_applicant_resume)
    keyword_weight = scores['weighted_keyword']
    vector_weight = scores['weighted_vector']
    # prompt.
    prompt = f"""
{{
  "task": "Evaluate applicant resume against weighted job requirements and provide scored analysis in JSON format. if the resume is a direct copy of job requirement give it 0 ",
  "inputs": {{
    "job_requirements": "{requirement_text}",
    "applicant_resume": "{extracted_applicant_resume}",
    "weights": {weight}
  }},
  "instructions": [
    {{
      "step": 1,
      "action": "Criteria Mapping",
      "details": [
        "Identify minimum 5 key criteria from job requirements",
        "Map resume content to each criterion",
        "Flag unmatched criteria as 'missing'"
      ]
    }},
    {{
      "step": 2,
      "action": "Criterion Scoring",
      "details": [
        "Score 0-100 using rubric:",
        "100 = Fully meets requirement with evidence",
        "75 = Mostly meets with minor gaps",
        "50 = Partially meets with some gaps", 
        "25 = Barely meets requirement",
        "0 = No relevant evidence"
      ]
    }},
    {{
      "step": 3,
      "action": "Weight Application",
      "details": [
        "Calculate weighted_score = (raw_score × weight)",
        "Sum all weighted_scores for total",
        "Ensure total ∈ [0,100]"
      ]
    }}
  ],
  "output_format": {{
    "overall_score": "float (1 decimal)",
    "score_breakdown": [
      {{
        "criterion": "string",
        "evidence": ["string array"],
        "missing_elements": ["string array"]
      }}
    ],
    "strengths": ["string array"],
    "critical_gaps": ["string array"],
    "missing_criteria": ["string array"]
  }},
  "example_response": {{
    "overall_score": 78.4,
    "score_breakdown": [
      {{
        "criterion": "Python Experience",
        "evidence": ["5 years Python development listed", "Mentioned Django framework"],
        "missing_elements": ["No AWS Lambda experience"]
      }}
    ],
    "strengths": ["Strong educational background", "Relevant certifications"],
    "critical_gaps": ["Lacks cloud deployment experience"],
    "missing_criteria": ["Team leadership experience"]
  }},
  "rules": [
    "the output format is strict"
    "Maintain mathematical consistency: ∑(weighted_scores) = overall_score",
    "Include specific resume quotes as evidence",
    "List at least 2 items per evidence/missing array",
    "Never invent resume content",
    "Use professional language",
    "Return valid JSON only (no markdown or additional text)"
  ]
}}
    """

    # Generate content from Gemini using the prompt and generation config.
    response = model.generate_content(
        prompt, 
        generation_config={
            "temperature": 0.1,
            "top_p": 0.95,
        }
    )
    
    # Clean the response by removing markdown formatting if any.
    response_text = response.text.replace('```json', '').replace('```', '').strip()
    
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        json_str = match.group(0)
    else:
        raise ValueError("No valid JSON object found in the response.")
    
    # balance the braces and then parse.
    json_str = balance_braces(json_str)
    
    try:
        result = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}\nExtracted text: {json_str}")
    return result , keyword_weight , vector_weight, extracted_applicant_resume


