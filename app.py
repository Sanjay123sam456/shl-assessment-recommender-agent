import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 SHL Assessment Recommender")
st.caption("Powered by FastAPI + RAG + OpenRouter")


if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.header("Options")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            recommendations = message.get("recommendations", [])

            if recommendations:
                st.divider()
                st.subheader("Recommended Assessments")

                for rec in recommendations:
                    st.markdown(f"### {rec['name']}")
                    st.write(f"**Type:** {rec['test_type']}")
                    st.link_button(
                        "Open in SHL",
                        rec["url"],
                        use_container_width=True,
                    )


prompt = st.chat_input("Ask about SHL assessments...")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {
        "messages": st.session_state.messages
    }

    try:

        response = requests.post(API_URL, json=payload)

        data = response.json()

        assistant_message = {
            "role": "assistant",
            "content": data["reply"],
            "recommendations": data["recommendations"]
        }

        st.session_state.messages.append(assistant_message)

        with st.chat_message("assistant"):
            st.markdown(data["reply"])

            if data["recommendations"]:
                st.divider()
                st.subheader("Recommended Assessments")

                for rec in data["recommendations"]:
                    st.markdown(f"### {rec['name']}")
                    st.write(f"**Type:** {rec['test_type']}")
                    st.link_button(
                        "Open in SHL",
                        rec["url"],
                        use_container_width=True,
                    )

    except Exception as e:
        st.error(f"Could not connect to FastAPI.\n\n{e}")