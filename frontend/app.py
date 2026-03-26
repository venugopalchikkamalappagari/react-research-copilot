import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="ReAct Research Copilot",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 ReAct Research Copilot")
st.caption("Ask questions about the document corpus. The agent will search, reason, and cite sources.")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This copilot uses the **ReAct** pattern:
    - 🧠 **Reason** about what to search
    - 🔧 **Act** by calling tools
    - 👁️ **Observe** results
    - 🔁 Repeat until ready to answer
    """)
    st.divider()
    st.header("📚 Corpus")
    st.markdown("39 documents — markdown + PDFs")
    st.divider()
    if st.button("🏥 Check API Health"):
        try:
            r = requests.get(f"{API_URL}/health")
            st.success(r.json()["message"])
        except Exception:
            st.error("API not reachable")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("steps"):
            with st.expander(f"🔍 Agent steps ({msg['step_count']} steps)"):
                for step in msg["steps"]:
                    st.markdown(f"**Step {step['step']}:** `{step['action']}({step['args']})`")
                    st.code(step["observation"][:500], language="text")

# Chat input
if question := st.chat_input("Ask a question about the corpus..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            try:
                import time
                start = time.time()
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": question},
                    timeout=300
                )
                data = response.json()
                answer = data["answer"]
                steps = data["steps"]
                step_count = data["step_count"]

                elapsed = round(time.time() - start, 2)
                st.caption(f"⏱️ Response time: {elapsed}s")
                st.markdown(answer)
                with st.expander(f"🔍 Agent steps ({step_count} steps)"):
                    for step in steps:
                        st.markdown(f"**🔢 Step {step['step']}**")
                        if step.get("thought"):
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                st.markdown("🧠 **Thought**")
                            with col2:
                                st.info(step["thought"])
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.markdown("🔧 **Action**")
                        with col2:
                            st.code(f"{step['action']}({step['args']})", language="python")
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.markdown("👁️ **Observe**")
                        with col2:
                            st.code(step["observation"][:600], language="text")
                        st.divider()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "steps": steps,
                    "step_count": step_count
                })

            except Exception as e:
                st.error(f"Error: {e}")