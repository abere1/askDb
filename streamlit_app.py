
import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("ASKDB_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="AskDB",
    page_icon=None,
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background: #0a0d14;
    color: #edf1fa;
}

.block-container {
    max-width: 1150px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

h1 {
    font-size: 3rem !important;
    font-weight: 800 !important;
    letter-spacing: -1.8px;
}

h2, h3 {
    letter-spacing: -0.5px;
}

.intro {
    color: #99a4b8;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}

div[data-testid="stTextArea"] textarea {
    background: #111725;
    border: 1px solid #293449;
    border-radius: 14px;
    color: #f4f6fc;
    padding: 16px;
}

div.stButton > button[kind="primary"] {
    background: #8b7cff;
    color: #090b12;
    border: none;
    border-radius: 10px;
    height: 46px;
    font-weight: 700;
}

div.stButton > button[kind="primary"]:hover {
    background: #a49aff;
    color: #090b12;
}

div[data-testid="stMetric"] {
    background: #111725;
    border: 1px solid #273247;
    border-radius: 12px;
    padding: 16px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #273247;
    border-radius: 12px;
    overflow: hidden;
}

div[data-testid="stExpander"] {
    border: 1px solid #273247;
    border-radius: 12px;
    background: #101522;
}

hr {
    border-color: #252e40;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

if "question" not in st.session_state:
    st.session_state.question = ""

if "result" not in st.session_state:
    st.session_state.result = None

if "error" not in st.session_state:
    st.session_state.error = None

st.markdown(
    "<div style='color:#a99cff;font-weight:700;letter-spacing:3px;"
    "font-size:12px'>ASKDB</div>",
    unsafe_allow_html=True,
)

st.title("Your data. Just ask.")
st.markdown(
    '<p class="intro">Ask a question in plain English. '
    'Get answers directly from your database.</p>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("#### What do you want to know?")

    question = st.text_area(
        "Question",
        key="question",
        height=110,
        placeholder=(
            "For example: Which 5 products generated "
            "the most revenue?"
        ),
        label_visibility="collapsed",
    )

    examples = [
        "How many customers are in each country?",
        "Show monthly sales for completed orders.",
        "Which products have the highest revenue?",
        "How many orders are there for each status?",
    ]

    st.caption("Try asking")

    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(
                example,
                key=f"example_{i}",
                use_container_width=True,
            ):
                st.session_state.question = example
                st.rerun()

    run = st.button(
        "Run query",
        type="primary",
        use_container_width=True,
    )

if run:
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        st.session_state.result = None
        st.session_state.error = None

        try:
            with st.spinner("Finding your answer..."):
                response = requests.post(
                    f"{API_URL}/query/ask",
                    json={"question": question.strip()},
                    timeout=120,
                )

            if response.ok:
                st.session_state.result = response.json()
            else:
                try:
                    detail = response.json().get("detail", "Request failed.")
                except ValueError:
                    detail = "Request failed."
                st.session_state.error = detail

        except requests.RequestException:
            st.session_state.error = (
                "Couldn't connect to AskDB. Make sure the API is running."
            )

if st.session_state.error:
    st.error(st.session_state.error)

result = st.session_state.result

if result:
    st.markdown("---")
    st.markdown("### Answer")

    metric1, metric2 = st.columns(2)

    metric1.metric("Rows returned", result["row_count"])
    metric2.metric("Columns", len(result["columns"]))

    rows = result["rows"]

    if rows:
        df = pd.DataFrame(rows, columns=result["columns"])
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download results as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="askdb_results.csv",
            mime="text/csv",
        )
    else:
        st.info("The query ran successfully, but returned no rows.")

    with st.expander("View generated SQL"):
        st.code(result["sql"], language="sql")

    st.caption("Results are limited by the database query executor.")
