import json
from langchain.schema.messages import HumanMessage, AIMessage
from datetime import datetime

# save the chat history to a json file
def save_chat_history_json(chat_history, file_path):
    with open(file_path, "w") as f:
        # convert the messages to a dictionary
        json_data = [message.dict() for message in chat_history]
        # save the messages to a json file
        json.dump(json_data, f)

# load the chat history from a json file
def load_chat_history_json(file_path):
    with open(file_path, "r") as f:
        # load the messages from the json file
        json_data = json.load(f)
        # convert the messages to the appropriate class
        messages = [HumanMessage(**message) if message["type"] == "human" else AIMessage(**message) for message in json_data]
        # return the messages
        return messages

# get the current timestamp
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")