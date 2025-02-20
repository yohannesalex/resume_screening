import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from file_reader import extract_text_from_file
import os
from dotenv import load_dotenv
import google.generativeai as genai
from nltk.stem import WordNetLemmatizer

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Load environment variables
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in the environment variables!")

# Configure Gemini API
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Download NLTK resources
nltk.download(['punkt', 'stopwords', 'wordnet', 'omw-1.4'])
STOPWORDS = set(stopwords.words('english'))

def preprocess_text(text):
    """Cleans and tokenizes text."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in STOPWORDS and len(word) > 2]
    return " ".join(tokens)

def extract_key_words(resume_text, job_text):
    """Extracts keywords using Gemini with improved prompt and error handling"""
    prompt = f"""
    Extract technical keywords from the resume and job description. Follow these rules:
    1. Return JSON with "resume_keywords" and "job_keywords" arrays
    2. Include only technical terms, tools, and skills
    3. Use lowercase and singular form
    4. Remove generic terms like 'communication'
    5. Example output:
    {{
        "resume_keywords": ["python", "machine learning", "sql"],
        "job_keywords": ["python", "data analysis", "aws"]
    }}

    Resume Text:
    {resume_text}

    Job Text:
    {job_text}
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
            }
        )
        # Clean and parse response
        response_text = response.text.replace('```json', '').replace('```', '').strip()
        keywords = json.loads(response_text)
        
        # Normalize keywords
        keywords['resume_keywords'] = list(set([lemmatizer.lemmatize(kw.lower()) for kw in keywords['resume_keywords']]))
        keywords['job_keywords'] = list(set([lemmatizer.lemmatize(kw.lower()) for kw in keywords['job_keywords']]))
        
        return keywords
    except Exception as e:
        print(f"Keyword extraction failed: {str(e)}")
        return {"resume_keywords": [], "job_keywords": []}

def calculate_keyword_match(resume_kws, job_kws):
    """Calculates keyword matching percentage"""
    if not job_kws:
        return 0.0
    
    matched = len(set(resume_kws) & set(job_kws))
    return (matched / len(job_kws)) * 100

def calculate_vector_similarity(job_text, resume_text):
    """Calculates TF-IDF cosine similarity"""
    preprocessed = [preprocess_text(job_text), preprocess_text(resume_text)]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(preprocessed)
    
    similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    return similarity * 100  # Convert to percentage

def calculate_scores(job_text, resume_text):
    """Main function to calculate both scores"""
    # Get keywords
    keywords = extract_key_words(resume_text, job_text)
    
    # Calculate keyword match
    keyword_score = calculate_keyword_match(
        keywords['resume_keywords'],
        keywords['job_keywords']
    )
    
    # Calculate vector similarity
    vector_score = calculate_vector_similarity(job_text, resume_text)
    
    # Apply weights
    weighted_keyword = (keyword_score * 0.3)  # 30% weight
    weighted_vector = (vector_score * 0.1)    # 10% weight
    
    return {
        "raw_keyword_score": keyword_score,
        "raw_vector_score": vector_score,
        "weighted_keyword": weighted_keyword,
        "weighted_vector": weighted_vector,
        "total_score": weighted_keyword + weighted_vector,
        "matched_keywords": list(set(keywords['resume_keywords']) & set(keywords['job_keywords']))
    }

