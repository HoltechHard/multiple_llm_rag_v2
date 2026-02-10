import os
import sys
import asyncio
import nest_asyncio
from dotenv import load_dotenv
import streamlit as st
from streamlit_chat import message as st_message
import time
import pandas as pd
import json
from datetime import datetime
import streamlit.components.v1 as components
from pathlib import Path

# own classes
from scrap.scraper import WebScrapper
from rag.summarization import WebSummarizer
from rag.ingest import EmbeddingIngestor
from rag.chatbot import ChatBot
from parse.parsing import LLMParser
from config.ai_models import list_models
from couch_db.couchdb2 import couchbase_data
from utils.dialog import show_details_dialog
from utils.experiments import preprocess_experimental_data

# Set Windows event loop policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()
nest_asyncio.apply()

# Session variables
if "url_submitted" not in st.session_state:
    st.session_state.url_submitted = False
if "extraction_done" not in st.session_state:
    st.session_state.extraction_done = False
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "embedding_done" not in st.session_state:
    st.session_state.embedding_done = False
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "summary" not in st.session_state:
    st.session_state.summary = ""

# ---------------------------
# Page Config in streamlit
# ---------------------------

st.set_page_config(layout="wide", page_title="Web-ChatBot")
st.title("Project Chatbot with Multiple LLMs + RAG")

# ---------------------------
# Streamlit UI
# ---------------------------

page = st.sidebar.selectbox("Menu", ["Home", "AI Chatbot", "Reports", "Benchmarks"])

if page == "Home":
    st.markdown(
        """
        ## Welcome to Web-Chatbot
        **Web-Chatbot** is a small chatbot empowered by integration of multiple LLM with RAG of website knowledge extraction through LangChain.
        
        **Functionalities:**
        - **Web Scraping:** Crawl and extract web page content.
        - **Web Summarization:** Generate detailed summaries of the extracted content.
        - **Create Embeddings:** Embeddings with FAISS for vector representation and retrieval of web-scraped information
        - **Chatbot Interface:** Execute Question-Answering task via a conversational agent.
        - **Reports:** Generate historical reports of chatbot interactions.
        - **Bechmark Visualization:** Visualize the performance of different LLMs and their capabilities.

        **Technologies:**
        - **LLM:** Models 
            1) deepseek-r1:1.5b
            2) qwen3:1.7b
            3) llama3.2:3b
            4) gemma2:2b
            5) gpt-4o
        - **FAISS:** vector database to store embeddings
        - **CouchDB:** document database to store the chatbot results
        - **LangChain:** framework to integrate LLM, external data and tools
        - **Streamlit:** python library to fast prototype web apps
        - **Craw4AI:** python library to crawl and scrape web pages
        - **Highcharts:** javascript library for data visualization creating dashboards
        
        Get started!
        """
    )    

elif page == "AI Chatbot":

    # chatbot formulary
    with st.form("url_form"):
        url_input = st.text_input("Enter a URL to crawl:")
        submit_url = st.form_submit_button("Submit URL")

        if submit_url and url_input:
            st.session_state.url_submitted = True
            st.session_state.extraction_done = False
            st.session_state.embedding_done = False
            st.session_state.chat_history = []
            st.session_state.summary = ""
    
    if st.session_state.url_submitted:
        col1, col2 = st.columns(2)

        with col1:
            st.header("1. Web-Scrapping")

            if not st.session_state.extraction_done:
                with st.spinner("Extracting website..."):
                    scraper = WebScrapper()
                    extracted = asyncio.run(scraper.crawl(url_input))
                    st.session_state.extracted_text = extracted
                    st.session_state.extraction_done = True
                st.success("Extraction complete!")

            preview = "\n".join([line for line in st.session_state.extracted_text.splitlines() if line.strip()][:5])
            st.text_area("Extracted Text Preview", preview, height=150)

            st.download_button(
                label="Download Extracted Text",
                data=st.session_state.extracted_text,
                file_name="extract_text.txt",
                mime="text/plain",
            )

            st.markdown("---")

            st.header("2. Web-Summarization")

            if st.button("Summarize Web Page", key="summarize_button"):
                with st.spinner("Summarizing..."):
                    summarizer = WebSummarizer()
                    st.session_state.summary = summarizer.summarize(st.session_state.extracted_text)
                st.success("Summarization complete!")            

            if st.session_state.summary:
                st.subheader("Summarized Output")
                
                # LLM parsing
                parser = LLMParser()
                main_text, think_text = parser.parse_llm_response(st.session_state.summary)
                
                # Reasoning in expander (only if present)
                if think_text:
                    with st.expander("Thinking/Reasoning", expanded=False):
                        st.markdown(think_text)

                # Main summary/answer
                if main_text:
                    st.markdown(main_text)
                else:
                    st.markdown("No summary content generated!")

        with col2:
            st.header("3. Create Embeddings")

            if st.session_state.extraction_done and not st.session_state.embedding_done:
                if st.button("Create Embeddings"):
                    with st.spinner("Creating embeddings..."):
                        embeddings = EmbeddingIngestor()
                        st.session_state.vectorstore = embeddings.create_embeddings(st.session_state.extracted_text)
                        st.session_state.embedding_done = True
                    st.success("Vectors are created!")

            elif st.session_state.embedding_done:
                st.info("Embeddings have been created.")

            st.markdown("---")

            st.header("4. ChatBot")

            if st.session_state.embedding_done:

                # process of generate new experiment
                user_input = st.text_input("Your Message:", key="chat_input")

                if st.button("New Experiment", key="new_experiment") and user_input:

                    if url_input and user_input:
                        experiment_key = couchbase_data.init_experiment(url_input, user_input)

                        if experiment_key:
                            st.session_state.current_experiment = experiment_key
                            st.success(f"Experiment registered: {experiment_key}!")
                        else:
                            st.error("Error to register experiment!")
                
                selected_model = st.selectbox(
                    label = "--- Select LLM model ---",
                    options = list_models(),
                    index = 0,
                    help = "Select the LLM model for Chatbot"
                )                
                
                # register details of experiment in couchbase
                if st.button("Send", key="send_button") and user_input:

                    if not st.session_state.current_experiment:
                        st.warning("Please, register the experiment first!")
                    else:
                        # start chatbot
                        start_time = time.time()
                        chatbot = ChatBot(st.session_state.vectorstore, selected_model)   
                        bot_answer = chatbot.qa(user_input)
                    
                        end_time = time.time()
                        total_time = (end_time - start_time)/60

                        st.session_state.chat_history.append({
                            "user": user_input, 
                            "bot": bot_answer, 
                            "time": total_time
                        })

                        # save to file
                        chat_file_content = "\n\n".join([f"User: {chat['user']}\nBot: {chat['bot']}\nTime: {chat.get('time', 0):.2f} min" for chat in st.session_state.chat_history])                        
                        with open(f"history/chat_history.txt", "w", encoding="utf-8") as cf:
                            cf.write(chat_file_content)

                        try:                            
                            # insert results chatbot in couchbase
                            success = couchbase_data.insert(
                                experiment_key = st.session_state.current_experiment,
                                model_name = selected_model,
                                answer = bot_answer,                                
                                time = total_time,
                                score = None
                            )

                            if not success:
                                st.warning("Failed to save QA in couchbase!")
                        except Exception as e:
                            st.error(f"Couchbase error: {str(e)}")

                # clear conversation button
                if st.button("Clear conversation", key = "clear_button"):
                    st.session_state.chat_history = []

                # show response in frontend
                if st.session_state.chat_history:
                    for chat in st.session_state.chat_history:
                        # initialize the parser
                        parser = LLMParser()

                        # print user question in frontend
                        st.markdown(f"Time: {chat.get('time', 0):.2f} minutes")
                        st_message(chat["user"], is_user=True)
                        
                        # print the bot answer in fronted
                        bot_main_text, bot_think_text = parser.parse_llm_response(chat["bot"])

                        # hidden reasoning process in expander
                        if bot_think_text:
                            with st.expander("Thinking / Reasoning", expanded=False):
                                st.markdown(bot_think_text)

                        # Show main bot answer
                        st_message(
                            bot_main_text if bot_main_text else chat["bot"],
                            is_user=False
                        )

            else:
                st.info("Please create embeddings to activate the chat.")


elif page == "Reports":

    st.header("Experiment Reports")

    # read data from couchbase
    experiment_data = couchbase_data.read_documents()

    if not experiment_data:
        st.warning("No data found in couchbase")
        st.stop()

    experiment_keys = list(experiment_data.keys())

    if not experiment_keys:
        st.warning("No experiments found in the database!")
        st.stop()

    st.markdown("---")

    # create expanders frontend (like accordion)
    for experiment_key in experiment_keys:
        experiment = experiment_data[experiment_key]

        if not isinstance(experiment, dict):
            continue
        
        with st.expander(f"**Experiment:** \n{experiment_key}", expanded = False):
            
            # experiment metadata
            st.markdown(f"**URL:** \n{experiment.get('url')}")
            st.markdown(f"**Question:** \n{experiment.get('question')}")
            st.markdown(f"**Date:** \n{experiment.get('date')}")
            
            st.markdown("---")

            # generation of each response in each accordion
            df = pd.DataFrame({
                'Model': experiment.get('model_name', []),
                'Answer': experiment.get('answer', []),
                'Time': experiment.get('time', []),
                'Score': experiment.get('score', [])
            })            

            # display the current page
            st.subheader("Report of conversations")

            # pagination logic
            page_size = 5
            total_items = len(df)
            total_pages = max(1, (total_items - 1) // page_size + 1)

            # Fix Duplicate ID by providing a unique key
            page_num = st.number_input(
                f"Page number", 
                min_value = 1, 
                max_value = total_pages, 
                value = 1,
                key = f"page_num_{experiment_key}"
            )
            
            start_idx = (page_num - 1) * page_size
            end_idx = start_idx + page_size
            current_df_slice = df.iloc[start_idx:end_idx]

            event = st.dataframe(
                data = current_df_slice,
                column_config = {
                    "Model": st.column_config.TextColumn(
                        "Model", width = "medium"
                    ),
                    "Answer": st.column_config.TextColumn(
                        "Answer", width = "large"
                    ),
                    "Time": st.column_config.NumberColumn(
                        "Time (min)", format="%.2f", width = "small"
                    ),
                    "Score": st.column_config.NumberColumn(
                        "Score", format="%.2f", width = "small"
                    )
                }, 
                use_container_width = True,
                hide_index = True,
                on_select="rerun",
                selection_mode="single-row",
                key=f"df_{experiment_key}"
            )

            st.markdown("---")

            # Trigger dialog if a row is selected
            if event and event.selection and event.selection.rows:
                selected_row_idx = event.selection.rows[0]
                selected_data = current_df_slice.iloc[selected_row_idx]                
                show_details_dialog(selected_data['Model'], selected_data['Answer'])


elif page == "Benchmarks":

    # read data from couchbase
    experiment_data = couchbase_data.read_documents()
    
    # testing
    processed_data = preprocess_experimental_data(experiment_data)

    # Serialize to JSON strings
    exp_keys_json = json.dumps(processed_data[0])
    series_json = json.dumps(processed_data[1])

    # Load HTML template and JS scripts
    html_template = Path("static/html/charts.html").read_text(encoding="utf-8")
    
    # Load JS script content
    js_charts = Path("static/js/render_chart.js").read_text(encoding="utf-8")

    # Inject data and script
    html_filled = html_template.replace(
        "__JS_CHARTS__", js_charts
    ).replace(
        "__EXP_KEYS__", exp_keys_json
    ).replace(
        "__SERIES__", series_json
    )

    # Render
    components.html(
        html_filled,
        height=1000,
        scrolling=False
    )
    