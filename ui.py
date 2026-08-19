import streamlit as st
import pandas as pd

from interview_engine import load_dataset, filter_questions
from voice_record import record_audio
from test_whisper import speech_to_text
from text_to_speech import speak
from evaluation import evaluate_answer,overall_evaluation
from charts import ai_score_chart,performance_trend,status_ditribution
from pdf_generator import generate_pdf

# Load Data
df = load_dataset()
topics = sorted(df['topic'].unique())

# Page Configuration -------------------------------
st.set_page_config(
    page_title="AI Interview Evaluation System",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS ---------------------------------
st.markdown("""
<style>
.main {
    background: #f5f7fb;
}
.title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
    color: #0f62fe;
}
.subtitle {
    text-align: center;
    color: gray;
    font-size: 18px;
}
.card {
    background: rgba(255,255,255,0.25);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 8px 25px rgba(0,0,0,.15);
    margin-top: 20px;
}
.score {
    font-size: 30px;
    color: green;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Session State --------------------------------------

if "started" not in st.session_state:
    st.session_state.started = False

if "current_question" not in st.session_state:
    st.session_state.current_question = 1

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "questions" not in st.session_state:
    st.session_state.questions = None

if "result" not in st.session_state:
    st.session_state.result = None

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 5

if "recognized_text" not in st.session_state:
    st.session_state.recognized_text = ""

if "all_results" not in st.session_state:
    st.session_state.all_results = []


if "interview_completed" not in st.session_state:
    st.session_state.interview_completed = False

if "question_states" not in st.session_state:
    st.session_state.question_states = {}



# if st.session_state.get("overall_report") is not None:
    # st.write(st.session_state.get("overall_report"))


# Sidebar -------------------------------------------
with st.sidebar:
    st.title("⚙ Interview Settings")

    candidate_name = st.text_input(
        "👤 Candidate Name",
        placeholder="Enter your name",
        value=st.session_state.candidate_name
    )

    total_question_input = st.slider(
        "Number of Questions",
        1, 10, 5
    )

    answer_mode = st.radio("Answer Mode", ["Text", "Voice"])
    feedback_mode = st.radio("Feedback Mode", ["Text", "Text + Audio"])
    
    topic = st.selectbox(
        "📘 Select Topic",
        ["Mixed (All topics)"] + topics
    )

    difficulty = st.selectbox(
        "🎯 Select Difficulty",
        ["All levels", "Easy", "Medium", "Hard"]
    )

    st.divider()

    if st.button("🚀 Start Interview", use_container_width=True):
        questions = filter_questions(df, topic, difficulty, total_question_input)
        if questions.empty:
            st.error("No questions found for the selected filters.")
            st.stop()

        if candidate_name.strip() == "":
            st.warning("Please enter the candidate name.")
        else:
            st.session_state.started = True
            st.session_state.questions = questions
            st.session_state.candidate_name = candidate_name
            st.session_state.current_question = 1
            st.session_state.result = None
            # st.session_state.submitted = False

            st.session_state.question_states = {}
            st.session_state.all_results = []
            st.session_state.recognized_text = ""
            st.session_state.interview_completed = False
            
            # Lock in the selected number of questions for this session
            st.session_state.total_questions = min(total_question_input, len(questions))
            st.rerun()

# Home Page ------------------------------------
if not st.session_state.started:
    st.markdown(
        "<div class='title'>🤖 AI Interview Evaluation System</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Practice Technical Interviews using Artificial Intelligence</div>",
        unsafe_allow_html=True
    )
    # Ensure you have an 'ai.png' in your working directory!
    try:
        st.image("ai.png")
    except Exception:
        pass # Silently pass if image is missing during testing

    st.info("Select settings from the left sidebar and click Start Interview.")

# Interview Page -----------------------------------
else:
    if st.session_state.interview_completed:
        st.balloons()
        st.markdown("<div class='title'>🎉 Interview Completed!</div>", unsafe_allow_html=True)
        st.markdown("<div class='subtitle'>Here is your detailed performance report</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        report = st.session_state.overall_report
        
        # --- 1. Top Level Metrics ---
        st.markdown("### 📊 Performance Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="🏆 AI Score", value=f"{report.get('overall_ai_score', 0)}/10")
        with col2:
            st.metric(label="🤖 NLP Score", value=f"{report.get('overall_nlp_score', 0)}%")
        with col3:
            st.metric(label="🎯 Status", value=report.get("overall_status", "N/A"))
        with col4:
            st.metric(label="💼 Recommendation", value=report.get("hiring_recommendation", "N/A"))

        st.divider()

        # --- 2. Interactive Tabs ---
        tab1, tab2, tab3 = st.tabs(["📝 Executive Summary", "⚖️ Strengths & Weaknesses", "🔍 Q&A Breakdown"])

        # TAB 1: Summary & Roadmap
        with tab1:
            st.subheader("💡 AI Interview Summary")
            st.info(report.get("overall_summary", "No summary provided by the AI."))
            
            st.subheader("🗺️ Learning Roadmap (Next Steps)")
            roadmap = report.get("learning_roadmap", [])
            if roadmap:
                for idx, topic in enumerate(roadmap):
                    st.markdown(f"**{idx + 1}.** {topic}")
            else:
                st.write("No topics suggested.")

        # TAB 2: Strengths & Weaknesses
        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div style="background:#e6fffa; padding:20px; border-radius:15px; border-left: 5px solid #00b5ad;">
                    <h3 style="color:#00b5ad;">💪 Core Strengths</h3>
                """, unsafe_allow_html=True)
                for strength in report.get("overall_strengths", []):
                    st.markdown(f"- {strength}")
                st.markdown("</div>", unsafe_allow_html=True)
                    
            with c2:
                st.markdown(f"""
                <div style="background:#fff5f5; padding:20px; border-radius:15px; border-left: 5px solid #e53e3e;">
                    <h3 style="color:#e53e3e;">📉 Areas to Improve</h3>
                """, unsafe_allow_html=True)
                for weakness in report.get("overall_weaknesses", []):
                    st.markdown(f"- {weakness}")
                st.markdown("</div>", unsafe_allow_html=True)

        # TAB 3: Question Breakdown (Using Expanders)
        with tab3:
            st.subheader("🔄 Detailed Answer Review")
            for i, res in enumerate(st.session_state.all_results):
                with st.expander(f"Q{i+1}: {res['question']}"):
                    st.markdown(f"**🗣️ Your Answer:**\n> {res['candidate_answer']}")
                    st.markdown(f"**🎯 Ideal Answer:**\n> {res['ideal_answer']}")
                    
                    st.markdown("---")
                    st.markdown("**🤖 AI Feedback:**")
                    st.write(res['evaluation'].get('feedback', 'No detailed feedback.'))
                    
                    # Individual Question Metrics
                    mc1, mc2, mc3 = st.columns(3)
                    mc1.metric("Q-AI Score", f"{res['evaluation'].get('ai_score', 0)}/10")
                    mc2.metric("Q-NLP Score", f"{res['evaluation'].get('nlp_score', 0):.2f}%")
                    mc3.metric("Q-Status", res['evaluation'].get('status', 'N/A'))
                    
                    # Missing Concepts for this specific question
                    missing = res['evaluation'].get('missing_concept', [])
                    if missing:
                        st.caption("🧩 **Missing Concepts:** " + ", ".join(missing))

        st.divider()

        with st.expander("📊 Analytics Dashboard", expanded=False):
            question_ids=[]
            ai_scores=[]
            nlp_scores=[]
            statuses=[]
            difficulties = []

            for  item in st.session_state.all_results:
                question_ids.append(item["question_id"])
                ai_scores.append(item["evaluation"]["ai_score"])
                nlp_scores.append(item["evaluation"]["nlp_score"])
                statuses.append(item["evaluation"]["status"])
                difficulties.append(item["difficulty"])


            chart_df=pd.DataFrame({
                "Question":question_ids,
                "Difficulty": difficulties,
                "AI Score":ai_scores,
                "NLP Score":nlp_scores,
                "Status":statuses,
                
            })
            ai_score_chart(chart_df)

           

            performance_trend(chart_df)

            status_ditribution(chart_df)

            st.subheader("📋 Question-wise Performance")         
            
            st.dataframe(chart_df,use_container_width=True)

            pass


        

        generate_pdf(
            st.session_state.candidate_name,
            topic,
            st.session_state.overall_report,
            st.session_state.all_results
        )

        
        with open("Interview_Report.pdf", "rb") as pdf_file:
            st.download_button(
                label="⬇ Download PDF Report",
                data=pdf_file,
                file_name=f"{st.session_state.candidate_name}_Interview_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        # --- Restart Button ---
        if st.button("🔄 Start a New Interview", use_container_width=True):
            # Resetting the session state properly so the app doesn't crash on restart
            keys_to_clear = [
                'started', 'current_question', 'all_results', 
                'question_states', 'interview_completed', 'overall_report', 'result'
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        st.stop() # Prevents the rest of the UI (like the next question layout) from rendering

    
    st.title("🧠 Technical Interview")

    # Safe progress calculation
    progress = min(st.session_state.current_question / st.session_state.total_questions, 1.0)
    st.progress(progress)

    st.write(
        f"### Question {st.session_state.current_question} / {st.session_state.total_questions}"
    )

    current_index = st.session_state.current_question - 1
    current_row = st.session_state.questions.iloc[current_index]

    question = current_row["question"]
    question_id = current_row["question_id"]
    ideal_answer = current_row["ideal_answer"]

    saved_state = st.session_state.question_states.get(question_id, {})

    if saved_state.get("submitted", False):
        st.session_state.result = saved_state["evaluation"]
    else:
        st.session_state.result = None

    st.caption(f"Question ID: {question_id}")
    st.info(question)

    if answer_mode == "Text":
        candidate_answer = st.text_area("Your Answer",value=saved_state.get("candidate_answer", ""), height=180)
    else:
        st.write("### 🎤 Record your answer")
        
        audio_value = st.audio_input("Record Answer", label_visibility="collapsed",key=f"audio_{question_id}")
        
        if audio_value is not None:
           
            if st.session_state.get("last_audio") != audio_value:
                st.session_state.last_audio = audio_value
                
                # Use .getvalue() for safe byte extraction in Streamlit
                with open("recording.wav", "wb") as f:
                    f.write(audio_value.getvalue())
                    
                with st.spinner("Converting speech to text..."):
                    text = speech_to_text("recording.wav")
                    st.session_state.recognized_text = text

        # Allow user to edit the transcribed text before submitting
        candidate_answer = st.text_area(
            "Recognized Text (You can edit this before submitting)",
            value=saved_state.get("candidate_answer",st.session_state.recognized_text),
            height=180
        )

    # --- SUBMIT BUTTON LOGIC ---
    col_prev, col_submit, col_next = st.columns(3)

    with col_prev:

        if st.session_state.current_question > 1:

            if st.button("⬅ Previous", use_container_width=True):

                st.session_state.current_question -= 1

                st.session_state.recognized_text = ""

                st.session_state.last_audio = None


                st.rerun()

    with col_submit:
        
        if st.button("✅ Submit Answer", use_container_width=True):
            
            if not candidate_answer.strip():
                st.warning("Please provide an answer before submitting.")
            else:

                if saved_state.get("submitted") and saved_state.get("candidate_answer") == candidate_answer:
                    st.info("Already evaluated!")
                else:
                    with st.spinner("Evaluating your answer..."):
                        # Evaluate the text 
                        result = evaluate_answer(question, ideal_answer, candidate_answer)    
                        st.session_state.result = result
                    
                        new_entry = {
                            "question_id": question_id,
                            "question": question,
                            "difficulty": current_row["difficulty"],
                            "ideal_answer": ideal_answer,
                            "candidate_answer": candidate_answer,
                            "evaluation": result
                        }

                        # 1. Purana result remove karein agar pehle se list me hai (Duplicate rokne ke liye)
                        st.session_state.all_results = [
                            res for res in st.session_state.all_results 
                            if res["question_id"] != question_id
                        ]   
                    
                        # 2. Naya result append karein
                        st.session_state.all_results.append(new_entry)

                        # 3. Question state update karein
                        st.session_state.question_states[question_id] = {
                            "candidate_answer": candidate_answer,
                            "evaluation": result,
                            "submitted": True
                        }

                        if feedback_mode == "Text + Audio":
                            speak(result["detailed_analysis"])

                        st.success("Answer evaluated successfully!")                        # st.session_state.submitted = True

                # Optional: Add audio feedback if selected
                # if feedback_mode == "Text + Audio" and st.session_state.result:
                #     speak(st.session_state.result["feedback"])

    with col_next:
        if st.session_state.current_question < st.session_state.total_questions:
            if st.button("➡ Next Question", use_container_width=True):
                st.session_state.current_question += 1
                st.session_state.recognized_text = ""
                st.session_state.last_audio = None
                st.rerun()
        else:

            if st.button("🏁 Finish Interview", use_container_width=True):

                if not st.session_state.get("interview_finalized", False):

                    with st.spinner("Generating Overall Report..."):

                        overall_report = overall_evaluation(
                            st.session_state.all_results
                        )

                        st.session_state.overall_report = overall_report

                        st.session_state.interview_completed = True

                        st.session_state.interview_finalized = True

                        st.rerun()

                

    st.divider()
    st.subheader("📊 Evaluation")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.session_state.result:
            st.metric("AI Score", f'{st.session_state.result.get("ai_score", 0)}/10')
        else:
            st.metric("AI Score", "--")

    with c2:
        if st.session_state.result:
            st.metric("NLP Similarity", f'{st.session_state.result.get("nlp_score", 0)}/10')
        else:
            st.metric("NLP Similarity", "--")

    with c3:
        if st.session_state.result:
            st.metric("Status", st.session_state.result.get("status", "N/A"))
        else:
            st.metric("Status", "--")

    # Cards ---------------------------------------
    col1, col2 = st.columns(2, gap="medium")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.result:
        next_topics = st.session_state.result.get("next_topics", [])
        next_topic_text = "<br>".join(next_topics) if next_topics else "None"
    else:
        next_topic_text = "No evaluation yet."
        
    st.markdown(f"""
    <div style="
        background:#F8F9FA;
        padding:20px;
        border-radius:15px;
        box-shadow:0 3px 10px rgba(0,0,0,0.2);
        text-align:left;
        width:70%;
        margin:auto;
    ">
        <h3>📚 Next Topics to Revise</h3>
       {next_topic_text}
    </div>
    """, unsafe_allow_html=True)

    with col1:
        if st.session_state.result:
            strengths = st.session_state.result.get("strengths", [])
            strength_text = "<br>".join([f"• {x}" for x in strengths]) if strengths else "None"
        else:
            strength_text = "No evaluation yet."

        st.markdown(f"""
        <div style="
            background:#F8F9FA;
            padding:20px;
            border-radius:15px;
            box-shadow:0 3px 10px rgba(0,0,0,0.2);
            height:220px;
            overflow-y:auto;
            overflow-x:hidden;
            white-space:normal;
            word-wrap:break-word;
            overflow-wrap:break-word;        
            text-align:left;
            margin-bottom: 20px;">
            <h3>📈 Strengths</h3>
            {strength_text}
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.result:
            feedback_text = st.session_state.result.get("feedback", "None")
        else:
            feedback_text = "No evaluation yet."    
        
        st.markdown(f"""
        <div style="
            background:#F8F9FA;
            padding:20px;
            border-radius:15px;
            box-shadow:0 3px 10px rgba(0,0,0,0.2);
            height:220px;
            overflow-y:auto;
            overflow-x:hidden;
            white-space:normal;
            word-wrap:break-word;
            overflow-wrap:break-word;
            text-align:left;">
            <h3>📝 Feedback</h3>
            {feedback_text}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.session_state.result:
            weaknesses = st.session_state.result.get("weaknesses", [])
            weakness_text = "<br>".join([f"• {x}" for x in weaknesses]) if weaknesses else "None"
        else:
            weakness_text = "No evaluation yet."
        
        st.markdown(f"""
        <div style="
            background:#F8F9FA;
            padding:20px;
            border-radius:15px;
            box-shadow:0 3px 10px rgba(0,0,0,0.2);
            height:220px;
            overflow-y:auto;
            overflow-x:hidden;
            white-space:normal;
            word-wrap:break-word;
            overflow-wrap:break-word;
            text-align:left;
            margin-bottom: 20px;">
            <h3>📉 Weaknesses</h3>
            <p>Your areas for improvement.</p>
            {weakness_text}
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.result:
            missing = st.session_state.result.get("missing_concept", [])
            missing_text = "<br>".join([f"• {x}" for x in missing]) if missing else "None"
        else:
            missing_text = "No evaluation yet."

        st.markdown(f"""
        <div style="
            background:#F8F9FA;
            padding:20px;
            border-radius:15px;
            box-shadow:0 3px 10px rgba(0,0,0,0.2);
            height:220px;
            overflow-y:auto;
            overflow-x:hidden;
            white-space:normal;
            word-wrap:break-word;
            overflow-wrap:break-word;
            text-align:left;">
            <h3>🧩 Missing Concepts</h3>
            <p>Important concepts you missed.</p>
            {missing_text}
        </div>
        """, unsafe_allow_html=True)    

    with st.expander("📖 Detailed Analysis"):
        if st.session_state.result:
            st.write(st.session_state.result.get("detailed_analysis", "No detailed analysis available."))
        else:
            st.info("Submit an answer to view detailed analysis.")





# st.session_state.submitted = True          
    # with col2:
    #     st.markdown("""
    #     <div style="
    #         background:#F8F9FA;
    #         padding:20px;
    #         border-radius:15px;
    #         box-shadow:0 3px 10px rgba(0,0,0,0.2);
    #         text-align:center;">
    #         <h3>📚 Next topic to revise</h3>
    #         <p>Machine Learning basics</p>
    #         <p>Python programming</p>
    #     </div>
    #     """, unsafe_allow_html=True)

