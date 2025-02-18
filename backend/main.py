import os
import json
import re
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import google.generativeai as genai

from generate_job_requirement_values import analyze_job_requirements
from file_reader import extract_text_from_file
from vector_keyword_similarity import calculate_scores

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables!")

# Configure the Gemini API 
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

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

def scoreResume(requirement_file_path, resume_file_path):
    # Extract text from the files using your library functions
    extracted_job_requirement = extract_text_from_file(requirement_file_path)
    extracted_applicant_resume = extract_text_from_file(resume_file_path)
    
    # Analyze job requirements and calculate scores
    weight = analyze_job_requirements(extracted_job_requirement)
    scores = calculate_scores(extracted_job_requirement, extracted_applicant_resume)
    keyword_weight = scores['weighted_keyword']
    vector_weight = scores['weighted_vector']
    
    # Define your analysis prompt.
    prompt = f"""
{{
  "task": "Evaluate applicant resume against weighted job requirements and provide a scored analysis in JSON format.",
  "inputs": {{
    "job_requirements": "{extracted_job_requirement}",
    "applicant_resume": "{extracted_applicant_resume}",
    "weights": {weight}
  }},
  "instructions": [
    {{
      "step": 1,
      "action": "Criteria Mapping",
      "details": [
        "Identify at least 5 key criteria from the job requirements.",
        "Map corresponding resume content to each criterion.",
        "Flag criteria that have no matching evidence as 'missing'."
      ]
    }},
    {{
      "step": 2,
      "action": "Criterion Scoring",
      "details": [
        "For each criterion, assign a score between 0 and 100 based on the following rubric:",
        "100 = Fully meets requirement with clear evidence.",
        "75 = Mostly meets requirement with minor gaps.",
        "50 = Partially meets with notable gaps.",
        "25 = Barely meets requirement.",
        "0 = No relevant evidence provided."
      ]
    }},
    {{
      "step": 3,
      "action": "Weight Application",
      "details": [
        "Multiply each criterion's raw score by its corresponding weight.",
        "Sum all weighted scores to compute the overall score.",
        "Ensure the overall score is within the range [0,100]."
      ]
    }}
  ],
  "output_format": {{
    "overall_score": "float (1 decimal place)",
    "score_breakdown": [
      {{
        "criterion": "string",
        "evidence": ["array of resume quotes (at least 2 items)"],
        "missing_elements": ["array of missing elements (at least 2 items)"]
      }}
    ],
    "strengths": ["array of strings"],
    "critical_gaps": ["array of strings"],
    "missing_criteria": ["array of strings"]
  }},
  "example_response": {{
    "overall_score": 78.4,
    "score_breakdown": [
      {{
        "criterion": "Python Experience",
        "evidence": [
          "5 years of Python development mentioned in work history",
          "Experience with Django framework described in project section"
        ],
        "missing_elements": [
          "No mention of AWS Lambda experience",
          "Lacks evidence for automated testing in Python"
        ]
      }}
    ],
    "strengths": [
      "Strong educational background",
      "Relevant industry certifications"
    ],
    "critical_gaps": [
      "Lacks cloud deployment experience",
      "No evidence of team leadership"
    ],
    "missing_criteria": [
      "Team leadership experience",
      "DevOps skills"
    ]
  }},
  "rules": [
    "Return valid JSON only without any markdown formatting or extra commentary.",
    "Maintain mathematical consistency: ∑(weighted_scores) must equal overall_score.",
    "Include specific resume quotes as evidence (minimum 2 items per evidence/missing array).",
    "Do not invent or assume any resume content.",
    "Use professional, clear language throughout."
  ]
}}
"""


    # Generate content from Gemini using the prompt and generation config.
    response = model.generate_content(
        prompt, 
        generation_config={
            "temperature": 0.4,
        }
    )
    
    # Clean the response by removing markdown formatting if any.
    response_text = response.text.replace('```json', '').replace('```', '').strip()
    
    # Use regex to capture the JSON block.
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        json_str = match.group(0)
    else:
        raise ValueError("No valid JSON object found in the response.")
    
    # Attempt to balance the braces and then parse.
    json_str = balance_braces(json_str)
    
    try:
        result = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON: {e}\nExtracted text: {json_str}")
    
    return result, keyword_weight, vector_weight

# Create a FastAPI app
app = FastAPI()

@app.post("/score_resume")
async def score_resume_api(requirement: UploadFile = File(...), resume: UploadFile = File(...)):
    try:
        # Save the uploaded files to temporary files
        temp_dir = tempfile.mkdtemp()
        req_path = os.path.join(temp_dir, requirement.filename)
        res_path = os.path.join(temp_dir, resume.filename)
        
        with open(req_path, "wb") as req_file:
            shutil.copyfileobj(requirement.file, req_file)
        with open(res_path, "wb") as res_file:
            shutil.copyfileobj(resume.file, res_file)
        
        # Process the files with your scoreResume function
        llm_output, keyword_result, vector_result = scoreResume(req_path, res_path)
        llm_result = llm_output['overall_score'] * 0.6
        final_score = llm_result + keyword_result + vector_result
        
        # Clean up the temporary directory and files
        shutil.rmtree(temp_dir)
        
        return JSONResponse(content={
            "final_score": final_score,
            "score_breakdown": llm_output.get("score_breakdown", []),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
