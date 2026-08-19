import matplotlib.pyplot as plt
import streamlit as st
import os
os.makedirs("charts",exist_ok=True)

def ai_score_chart(chart_df):
    
    st.subheader("🤖 AI Score by Question")

    fig,ax=plt.subplots(figsize=(8,4))

    ax.bar(
        chart_df["Question"],
        chart_df["AI Score"]
    )

    ax.set_xlabel("Question")

    ax.set_ylabel("AI Score")

    ax.set_title("AI Score by Question")

    plt.tight_layout()

    fig.savefig("charts/ai_score.png",bbox_inches="tight",dpi=300)

    st.pyplot(fig)
    plt.close(fig)


def performance_trend(chart_df):
    st.subheader("📈 Performance Trend")

    fig,ax=plt.subplots(figsize=(8,4))

    ax.plot(
        chart_df["Question"],
        chart_df['AI Score'],
        marker="o",
        linewidth=2,
        label="AI Score"
    )

    ax.plot(
        chart_df["Question"],
        chart_df["NLP Score"],
        marker="o",
        linewidth=2,
        label="NLP Score"
    )

    ax.set_xlabel("Question")

    ax.set_ylabel("Score")

    ax.set_title("Performance Trend")

    ax.legend()

    plt.tight_layout()

    fig.savefig("charts/trend.png",bbox_inches="tight",dpi=300)

    st.pyplot(fig)
    plt.close(fig)

def status_ditribution(chart_df):
    st.subheader("🏆 Status Distribution")

    status_counts=chart_df["Status"].value_counts()

    fig,ax=plt.subplots(figsize=(6,6))

    ax.pie(
        status_counts,
        labels=status_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_title("Interview Status Distribution")
    
    plt.tight_layout()
    
    plt.savefig("charts/status.png",bbox_inches="tight", dpi=300)
    
    st.pyplot(fig)
    
    plt.close(fig)



