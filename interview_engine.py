import pandas as pd
import random


def load_dataset():
    df=pd.read_csv("repaired_dataset.csv")
    return df


def filter_questions(df,topic,difficulty,total_question):
    filtered_df=df.copy()

    if topic!="Mixed (All topics)":
        filtered_df=filtered_df[filtered_df['topic']==topic]

    if difficulty!="All levels":
        filtered_df=filtered_df[filtered_df['difficulty']==difficulty]

    if filtered_df.empty:
        return filtered_df    

    selected_ques=filtered_df.sample(n=min(total_question,len(filtered_df)))


    return selected_ques
