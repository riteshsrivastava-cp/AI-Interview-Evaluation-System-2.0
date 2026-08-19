import re
import time
import nltk
import json

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



from google import genai

from voice_record import record_audio
from test_whisper import speech_to_text
from text_to_speech import speak

lemmatizer=WordNetLemmatizer()
cv=TfidfVectorizer()
client = genai.Client()

stop_words=set(stopwords.words('english'))
def preprocess(text):
    text = str(text).lower()
    text=re.sub(r'[^a-zA-Z]',' ',text)
    words=nltk.word_tokenize(text)
    clean=[]
    
    for word in words:
        if word not in stop_words:
            clean.append(lemmatizer.lemmatize(word))
    
    clean=" ".join(clean)
    return clean  

def calculate_similarity(ideal_answer,candidate_answer):

    ideal_processed=preprocess(ideal_answer)

    candidate_processed=preprocess(candidate_answer)

    texts=[
        ideal_processed,
        candidate_processed
    ]

    vectors=cv.fit_transform(texts)

    similarity=cosine_similarity(
        vectors[0],
        vectors[1]
    )

    score=round(similarity[0][0]*10,2)

    return score

def generate_feedback(question,ideal_answer,candidate_answer):
    prompt = f"""
    You are an expert technical interviewer.

    Evaluate the candidate's technical answer.

    Question:
    {question}

    Ideal Answer:
    {ideal_answer}

    Candidate Answer:
    {candidate_answer}

    Evaluation Rules:

    1. Evaluate based on:
    - Technical correctness
    - Conceptual understanding
    - Completeness
    - Clarity

    2. Ignore minor grammatical and spelling mistakes.
    Focus on evaluating the correctness of the technical concepts.
    Do not ignore major grammatical mistakes that alter the meaning.

    3. Do not compare exact wording.
    Give credit if the concept is correct.

    4. Be strict but fair.

    5. AI Score must be an INTEGER between 0 and 10.

    6. Return ONLY valid JSON.
    Do not write markdown.
    Do not write explanations.
    Do not use ```json.

    Return exactly in this format:

    {{
    "ai_score": 0,
    "status": "",
    "strengths": [
        "",
        ""
    ],
    "weaknesses": [
        "",
        ""
    ],
    "missing_concepts": [
        "",
        ""
    ],
    "feedback": "",
    "next_topics": [
        "",
        ""
    ],
    "detailed_analysis":"The candidate correctly explained... (3-8 paragraphs)"
    }}

    Rules:

    - ai_score: integer only (0-10)

    - status:
    Excellent
    Good
    Average
    Poor

    - strengths:
    Return ONLY 2 concise bullet points suitable for a flashcard.
    

    - weaknesses:
    Maximum 2 concise bullet points.

    - missing_concepts:
    Maximum 2 important missing concepts.

    - feedback:
    Maximum 2 short sentences.

    - next_topics:
    Maximum 2 topics only.

    Return ONLY the JSON object.
        """


    max_retries=6
    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            feedback=response.text.strip()
            print("\n========== GEMINI RESPONSE ==========")
            print(feedback)
            print("=====================================\n")
            feedback = feedback.replace("```json", "")
            feedback = feedback.replace("```", "")
            feedback = feedback.strip()
            try:
               
                feedback=json.loads(feedback)# conveerts it into python dictionsry
                

                

            except Exception:
                   print("Invalid JSON received from Gemini")

                   feedback= {
                        "ai_score": 0,
                        "status": "Error",
                        "strengths": [],
                        "weaknesses": [],
                        "missing_concepts": [],
                        "feedback": "Unable to generate feedback.",
                        "next_topics": [],
                         "detailed_analysis": "Detailed analysis could not be generated."
                    }

            return feedback

        except Exception as e:

            print(f"Attempt {attempt+1} failed")
            print(e)

            if attempt == 5:
                return {
                    "ai_score": 0,
                    "status": "Server Error",
                    "strengths": [],
                    "weaknesses": [],
                    "missing_concepts": [],
                    "feedback": "Gemini server is currently busy.",
                    "next_topics": [],
                    "detailed_analysis": "Server error. Detailed analysis could not be generated."
                }
            time.sleep(15)



def evaluate_answer(question,ideal_answer,candidate_answer):

    # NLP score
    similarity_score=calculate_similarity(ideal_answer,candidate_answer)

    # Gemini Feedback
    feedback=generate_feedback(question,ideal_answer,candidate_answer)

    # combining both
    result={
        "nlp_score":similarity_score,
        "ai_score":feedback["ai_score"],
        "status":feedback["status"],
        "strengths":feedback["strengths"],
        "weaknesses":feedback["weaknesses"],
        "missing_concept":feedback["missing_concepts"],
        "feedback":feedback["feedback"],
        "next_topics":feedback["next_topics"],
        "detailed_analysis":feedback["detailed_analysis"]
    }
    return result


def overall_evaluation(all_results):
    

    interview_summary = ""
    average_ai = sum(
       item["evaluation"]["ai_score"]
        for item in all_results
    ) / len(all_results)

    average_nlp = sum(
        item["evaluation"]["nlp_score"]
        for item in all_results
    ) / len(all_results)

    

    for item in all_results:

        interview_summary += f"""
        Question:
        {item["question"]}

        Candidate Answer:
        {item["candidate_answer"]}

        Ideal Answer:
        {item["ideal_answer"]}

        AI Score:
        {item["evaluation"]["ai_score"]}/10

        NLP Score:
        {item["evaluation"]["nlp_score"]:.2f}%

        Status:
        {item["evaluation"]["status"]}

        Strengths:
        {", ".join(item["evaluation"]["strengths"])}

        Weaknesses:
        {", ".join(item["evaluation"]["weaknesses"])}

        Missing Concepts:
        {", ".join(item["evaluation"]["missing_concept"])}

        Feedback:
        {item["evaluation"]["feedback"]}

        -----------------------------------------
        """

    interview_summary +=f"""
    Overall Average AI Score: {average_ai:.1f}/10
    Overall Average NLP Score: {average_nlp:.2f}%
    """
    
        

    prompt = f"""
        You are an expert technical interviewer.

        Below is the complete interview performance of a candidate.

        {interview_summary}

        Evaluate the candidate's OVERALL interview performance.

        Return ONLY valid JSON.

        Format:

        {{
        "overall_ai_score":0,
        "overall_status":"",
        "overall_strengths":[],
        "overall_weaknesses":[],
        "overall_summary":"",
        "hiring_recommendation":"",
        "learning_roadmap":[]
        }}

        Rules:  

        1. overall_ai_score must be integer (0-10).
        2. overall_status should be one of:
        Excellent
        Good
        Average
        Poor

        3. overall_strengths:
        Maximum 4 concise points.

        4. overall_weaknesses:
        Maximum 4 concise points.

        5. overall_summary:
        Write 4-6 concise sentences summarizing the interview.

        6. hiring_recommendation:
        Choose ONLY one:
        Strong Hire
        Hire
        Borderline
        No Hire

        7. learning_roadmap:
        Return 5 topics that the candidate should study next.

        Return ONLY valid JSON.
    """
    for attempt in range(6):
        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            overall_report = response.text.strip()


            overall_report = overall_report.replace("```json", "")
            overall_report = overall_report.replace("```", "")
            overall_report = overall_report.strip()
            try:
               
                overall_report=json.loads(overall_report)

                overall_report["overall_nlp_score"] = round(average_nlp, 2)
                
                return overall_report

            except Exception:
                 print("Invalid JSON received from Gemini")

                 overall_report = {
                    "overall_ai_score": 0,
                    "overall_nlp_score": round(average_nlp, 2),
                    "overall_status": "Error",
                    "overall_strengths": [],
                    "overall_weaknesses": [],
                    "overall_summary": "Unable to generate overall report.",
                    "hiring_recommendation": "Unknown",
                    "learning_roadmap": []
                }
                 
            print(overall_report)
            print("Fallback Overall Report Returned")
            return overall_report
        except Exception as e:

            print(f"Attempt {attempt+1} failed")
            print(e)

            if attempt == 5:
                return {
                    "overall_ai_score": 0,
                    "overall_nlp_score": round(average_nlp, 2),
                    "overall_status": "Server Error",
                    "overall_strengths": [],
                    "overall_weaknesses": [],
                    "overall_summary": "Gemini server is currently busy.",
                    "hiring_recommendation": "Unknown",
                    "learning_roadmap": []
                }
            time.sleep(15)

        