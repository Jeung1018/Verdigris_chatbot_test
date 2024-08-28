import InvokeAgent as agenthelper
import streamlit as st
import uuid
import json
import pandas as pd
from PIL import Image, ImageOps, ImageDraw
import time

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
if 'trace_output' not in st.session_state:
    st.session_state['trace_output'] = ""

# Load example prompts
with open("example_prompts.json", "r") as file:
    example_prompts = json.load(file)

# Display foldable list of example questions
with st.expander("Frequently Asked Questions (Click to Expand)"):
    st.write("Here are some example questions you can copy and paste into the input box below:")
    for prompt in example_prompts:
        st.markdown(f"- `{prompt}`")

# Add vertical space using margin-top with st.markdown
st.markdown("<div style='margin-top: 20px'></div>", unsafe_allow_html=True)

# Display a text box for input
st.write("## Type Your Question")
with st.form(key="qa_form", clear_on_submit=True):
    prompt = st.text_input(
        "Type your question below or copy and paste from the examples above",
        max_chars=2000,
        key="input_prompt"
    )
    submit_button = st.form_submit_button("Get Answer from AI")

# Function to calculate dynamic height for responses
def calculate_text_area_height(text, min_height=100, max_height=400):
    lines = text.count("\n") + 5
    estimated_height = min(max_height, max(min_height, lines * 40))
    return estimated_height

# Function to stream the response
def stream_response(llm_response, metadata_list):
    # Stream the main response content
    for char in llm_response:
        yield char
        time.sleep(0.01)  # Adjust the speed of streaming

    # After the main content is fully streamed, add a separation and then stream the links
    yield "\n\n"  # Add separation between the main content and the links

    if isinstance(metadata_list, list) and metadata_list:
        urls_text = "This answer is generated by referring to our company documentation below.\n\nFeel free to ask follow-up questions or see the references:\n"
        yield urls_text
        time.sleep(0.01)  # Adjust the speed of streaming

        for item in metadata_list:
            yield f"- **{item['title']}** [Link]({item['url']})\n"
            time.sleep(0.01)  # Adjust the speed of streaming
    else:
        yield "This answer does not contain references from our documentation. \n\nPlease contact support@verdigris.co for confirming the credibility of the content or ask more questions."
        time.sleep(0.01)  # Adjust the speed of streaming

# Handle form submission
if submit_button and prompt:
    event = {
        "sessionId": st.session_state['session_id'],
        "question": prompt
    }

    with st.spinner('Thinking...'):
        captured_string, llm_response, metadata_list = agenthelper.askQuestion(event['question'], event['sessionId'])

    if llm_response:
        st.write_stream(stream_response(llm_response, metadata_list))

        st.session_state['history'].append({"question": prompt, "answer": llm_response})
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
