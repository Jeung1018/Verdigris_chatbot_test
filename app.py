import InvokeAgent as agenthelper
import streamlit as st
import uuid
import json
import pandas as pd
from PIL import Image, ImageOps, ImageDraw

# Streamlit page configuration
st.set_page_config(page_title="Verdigris Chatbot", page_icon=":robot_face:", layout="wide")

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

# Function to crop image into a circle
def crop_to_circle(image):
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0) + image.size, fill=255)
    result = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    result.putalpha(mask)
    return result

# Title with logo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("verdigris_logo.png", width=140)
with col2:
    st.title("Verdigris Chatbot")
    st.write("powered by Claude 3.5 Sonnet")

# Sidebar for user trace data
st.sidebar.title("Trace Data")

# Session State Management
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'prompt' not in st.session_state:
    st.session_state['prompt'] = ""
if 'trace_output' not in st.session_state:
    st.session_state['trace_output'] = ""

# example prompts
with open("example_prompts.json", "r") as file:
    example_prompts = json.load(file)

# Add vertical space using margin-top with st.markdown
st.markdown("<div style='margin-top: 20px'></div>", unsafe_allow_html=True)

# Form to submit the selected prompt
with st.form(key="selected_prompt_form", clear_on_submit=True):
    selected_prompt = st.selectbox(
        "Frequently asked questions",
        example_prompts,
        key="select_box_prompt"
    )
    submit_selected_button = st.form_submit_button("Submit Selected Prompt")

# Form to submit the typed question
with st.form(key="typed_prompt_form", clear_on_submit=True):
    typed_prompt = st.text_input(
        "Type your question below or select the question from above",
        max_chars=2000,
        value=st.session_state['prompt'],
        key="input_prompt"
    )
    submit_typed_button = st.form_submit_button("Submit Typed Question")

# Function to calculate dynamic height for responses
def calculate_text_area_height(text, min_height=100, max_height=400):
    lines = text.count("\n") + 5
    estimated_height = min(max_height, max(min_height, lines * 40))
    return estimated_height

# Handle submission of selected prompt
if submit_selected_button and selected_prompt:
    st.session_state['prompt'] = selected_prompt
    event = {
        "sessionId": st.session_state['session_id'],
        "question": selected_prompt
    }
    with st.spinner('Thinking...'):
        captured_string, llm_response, metadata_list = agenthelper.askQuestion(event['question'], event['sessionId'])

    if llm_response:
        if isinstance(metadata_list, list) and metadata_list:
            urls_text = "\n"+"\nThis answer is generated by referring to our company documentation below.\n\nFeel free to ask follow-up questions or see the references:\n"
            for item in metadata_list:
                urls_text += f"- **{item['title']}** [Link]({item['url']})\n"
        else:
            urls_text = "\n"+"\n"+"\n\nThis answer does not contain references from our documentation. \n\n please contact support@verdigri.co for confirming the credibility of the content or ask more questions.\n"
        llm_response += urls_text

        st.session_state['history'].append({"question": selected_prompt, "answer": llm_response})
        st.session_state['trace_output'] = captured_string

# Handle submission of typed question
if submit_typed_button and typed_prompt:
    st.session_state['prompt'] = typed_prompt
    event = {
        "sessionId": st.session_state['session_id'],
        "question": typed_prompt
    }
    with st.spinner('Thinking...'):
        captured_string, llm_response, metadata_list = agenthelper.askQuestion(event['question'], event['sessionId'])

    if llm_response:
        if isinstance(metadata_list, list) and metadata_list:
            urls_text = "\n"+"\nThis answer is generated by referring to our company documentation below.\n\nFeel free to ask follow-up questions or see the references:\n"
            for item in metadata_list:
                urls_text += f"- **{item['title']}** [Link]({item['url']})\n"
        else:
            urls_text = "\n"+"\n"+"\n\nThis answer does not contain references from our documentation. \n\n please contact support@verdigri.co for confirming the credibility of the content or ask more questions.\n"
        llm_response += urls_text

        st.session_state['history'].append({"question": typed_prompt, "answer": llm_response})
        st.session_state['trace_output'] = captured_string

# Display the trace data in the sidebar
if st.session_state['trace_output']:
    st.sidebar.text_area("Trace Output", value=st.session_state['trace_output'], height=300)

# Display conversation history
st.write("## Conversation History")

# Load images outside the loop to optimize performance
human_image = Image.open('human_face.png')
robot_image = Image.open('verdigrisChar.jpg')
circular_human_image = crop_to_circle(human_image)
circular_robot_image = crop_to_circle(robot_image)

for index, chat in enumerate(reversed(st.session_state['history'])):
    col1_q, col2_q = st.columns([2, 10])
    with col1_q:
        st.image(circular_human_image, width=125)
    with col2_q:
        st.text_area("Q:", value=chat["question"], height=50, key=f"question_{index}", disabled=True)

    col1_a, col2_a = st.columns([2, 10])
    if isinstance(chat["answer"], pd.DataFrame):
        with col1_a:
            st.image(circular_robot_image, width=100)
        with col2_a:
            st.dataframe(chat["answer"], key=f"answer_df_{index}")
    else:
        answer_height = calculate_text_area_height(chat["answer"])
        with col1_a:
            st.image(circular_robot_image, width=150)
        with col2_a:
            st.markdown(
                f"<div style='height: {answer_height}px; overflow-y: auto;'>{chat['answer']}</div>",
                unsafe_allow_html=True
            )
