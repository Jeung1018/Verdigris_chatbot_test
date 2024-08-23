from datetime import datetime, timedelta
import boto3
import json
import os
import base64
import io
import sys
import re
import streamlit as st
from requests import request
from boto3.session import Session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from dotenv import load_dotenv

# Load environment variables from .env file
# load_dotenv()

# Ensure these environment variables are set in your .env file

# agentId = os.getenv("AGENT_ID")
# agentAliasId = os.getenv("AGENT_ALIAS_ID")
# theRegion = os.getenv("AWS_REGION")
my_db.connect(**st.secrets.db_credentials)
st.write("theRegion:", st.secrets["AWS_REGION"])

def extract_metadata(split_response):
    # Initialize an empty list to store dictionaries containing unique title, category, and URL
    metadata_list = []

    # Combine all parts of split_response into a single string for easier regex parsing
    combined_response = " ".join(split_response)

    # Regular expression patterns to match the metadata blocks
    metadata_pattern = r'"metadata":\{[^}]+\}'

    # Regular expression patterns to match title, category, and URL within each metadata block
    title_pattern = r'"title":"([^"]+)"'
    category_pattern = r'"category":"([^"]+)"'
    url_pattern = r'"url":"(https://[^"]+)"'

    # Set to track unique metadata entries
    unique_entries = set()

    # Iterate over each metadata block in the combined response
    for metadata_block in re.findall(metadata_pattern, combined_response):
        # Find the title, category, and URL within the current metadata block
        title_match = re.search(title_pattern, metadata_block)
        category_match = re.search(category_pattern, metadata_block)
        url_match = re.search(url_pattern, metadata_block)

        # If all fields are found, store them in the list as a dictionary
        if title_match and category_match and url_match:
            entry = (title_match.group(1), category_match.group(1), url_match.group(1))
            if entry not in unique_entries:
                unique_entries.add(entry)
                metadata_list.append({
                    "title": entry[0],
                    "category": entry[1],
                    "url": entry[2]
                })

    # Output the metadata list for debugging
    print("Extracted metadata_list:", metadata_list)
    return metadata_list

def decode_response(response):
    # Create a StringIO object to capture print statements
    captured_output = io.StringIO()
    sys.stdout = captured_output

    # Decode the response
    string = ""
    for line in response.iter_content():
        try:
            string += line.decode(encoding='utf-8')
        except:
            continue

    print("Decoded response", string)
    split_response = string.split(":message-type")
    print(f"Split Response: {split_response}")
    print(f"length of split: {len(split_response)}")

    # Splitting response into message-type segments
    for idx in range(len(split_response)):
        if "bytes" in split_response[idx]:
            encoded_last_response = split_response[idx].split("\"")[3]
            decoded = base64.b64decode(encoded_last_response)
            final_response = decoded.decode('utf-8')
            print(final_response)
        else:
            print(f"no bytes at index {idx}")
            print(split_response[idx])

    # Extract metadata using the new function
    metadata_list = extract_metadata(split_response)

    # Last response decoding
    last_response = split_response[-1]
    print(f"Last Response: {last_response}")
    if "bytes" in last_response:
        print("Bytes in last response")
        encoded_last_response = last_response.split("\"")[3]
        decoded = base64.b64decode(encoded_last_response)
        final_response = decoded.decode('utf-8')
    else:
        print("no bytes in last response")
        part1 = string[string.find('finalResponse') + len('finalResponse":'):]
        part2 = part1[:part1.find('"}') + 2]
        final_response = json.loads(part2)['text']

    # Final response final check
    final_response = final_response.replace("\"", "")
    final_response = final_response.replace("{input:{value:", "")
    final_response = final_response.replace(",source:null}}", "")
    llm_response = final_response

    # Restore original stdout
    sys.stdout = sys.__stdout__

    # Get the string from captured output
    captured_string = captured_output.getvalue()

    # Return both the captured output and the final response, along with metadata_list
    return captured_string, llm_response, metadata_list


def sigv4_request(
        url,
        method='GET',
        body=None,
        params=None,
        headers=None,
        service='execute-api',
        region=theRegion,
        credentials=Session().get_credentials().get_frozen_credentials()
    ):
    """Sends an HTTP request signed with SigV4"""
    headers = headers or {}

    print("Headers before signing:", headers)  # Debugging line to check headers

    req = AWSRequest(
        method=method,
        url=url,
        data=body,
        params=params,
        headers=headers
    )

    SigV4Auth(credentials, service, region).add_auth(req)

    # Print the headers after signing to debug the request signing process
    print("Headers after signing:", req.headers)

    req = req.prepare()

    return request(
        method=req.method,
        url=req.url,
        headers=req.headers,
        data=req.body
    )

def askQuestion(question, sessionId, endSession=False):
    url = f'https://bedrock-agent-runtime.{theRegion}.amazonaws.com/agents/{agentId}/agentAliases/{agentAliasId}/sessions/{sessionId}/text'
    myobj = {
        "inputText": question,
        "enableTrace": True,
        "endSession": endSession
    }

    response = sigv4_request(
        url,
        method='POST',
        service='bedrock',
        headers={
            'content-type': 'application/json',
            'accept': 'application/json',
        },
        region=theRegion,
        body=json.dumps(myobj)
    )

    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        print(f"Response content: {response}")
        return None, None

    content_type = response.headers.get('Content-Type')
    print(f"Content-Type: {content_type}")

    captured_string, llm_response, metadata_list = decode_response(response)
    return captured_string, llm_response, metadata_list
