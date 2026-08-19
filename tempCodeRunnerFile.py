with st.expander("📊 Analytics Dashboard", expanded=False):
            question_ids=[]
            ai_scores=[]
            nlp_scores=[]
            statuses=[]

            for  item in st.session_state.all_results:
                question_ids.append(item["question_id"])
                ai_scores.append(item["evaluation"]["ai_score"])
                nlp_scores.append(item["evaluation"]["nlp_score"])
                statuses.append(item["evaluation"]["status"])

            chart_df=pd.DataFrame({
                "Question":question_ids,
                "AI Score":ai_scores,
                "NLP Score":nlp_scores,
                "Status":statuses
            })
            st.dataframe(chart_df, use_container_width=True)

            st.subheader("🤖 AI Score by Question")

            st.bar_chart(
                chart_df.set_index("Question")[["AI Score","NLP Score"]]
            )

            status_counts=chart_df["Status"].value_counts()

            st.subheader("🏆 Status Distribution")
            st.bar_chart(status_counts)

            st.subheader("📋 Question-wise Performance")
            st.dataframe(chart_df,use_container_width=True)







            st.subheader("📈 Performance Trend")
            st.line_chart(
                chart_df.set_index("Question")[["AI Score"]]
            )


            pass