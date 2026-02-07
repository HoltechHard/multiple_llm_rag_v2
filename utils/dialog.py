import streamlit as st
from parse.parsing import LLMParser

# pop-up window to show details
@st.dialog("Experiment Details", width="large")
def show_details_dialog(model_name, full_answer):
    st.markdown(f"### Model: {model_name}")
    
    # Parse and render markdown
    parser = LLMParser()
    main_text, think_text = parser.parse_llm_response(full_answer)

    if think_text:
        with st.expander("Thinking / Reasoning", expanded=True):
            st.markdown(think_text)
    
    if main_text:
        st.markdown(main_text)
    else:
        st.markdown(full_answer)