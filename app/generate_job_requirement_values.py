import os
from dotenv import load_dotenv
import google.generativeai as genai

from file_reader import extract_text_from_file


load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables!")

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# function to identify the weights
def analyze_job_requirements(file_path):
    extracted_text = extract_text_from_file(file_path)

    prompt = f"""
Analyze this job requirement file carefully. The file named "{file_path}" may be in any format 
(text-based such as plain text, PDF, DOCX or image-based such as a scanned document). 
The extracted text is provided below 

Follow these steps:

1. File Processing and Text Extraction:
   - Use the provided text directly for text-based files.
   - For image-based files, if any OCR errors exist (e.g., confusing '1' with 'l' or '0' with 'O'), correct them.

2. Identify Key Components:
   - Locate explicit requirements using phrases like "must have", "required", or "essential".
   - Identify any repeated terms or concepts.
   - Highlight emotionally charged adjectives (e.g., "critical", "strong", "proven").

3. Categorize Components:
   - Organize the findings into these categories: [Education], [Technical Skills], [Experience], [Certifications], [Soft Skills], [Other].

4. Weight Assignment:
   - For each category, assign a percentage weight based on frequency, language strength, document position, and emphasis.
   - Ensure the total percentage equals 100%.
   - the percentage values can be any number not only divisible by 10 or 5

5. if the content is completelly something unrelated or like
6. Output Format (JSON only):
   For example:
   {{
       "Technical Skills": 10,
       "Education": 40,
       "Experience":35 ,
       "Soft Skills": 10,
       "Other": 5
   }}

Extracted File Text:
{extracted_text}
    """

    response = model.generate_content(
        prompt, 
    )

    

    return response.text

