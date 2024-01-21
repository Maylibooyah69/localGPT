from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.schema import messages_from_dict, messages_to_dict
import json
import psutil


def memory_to_json(memory, save=False):
    mes_dict = messages_to_dict(memory.chat_memory.messages)
    total_dict = {'messages': mes_dict}
    if save:
        with open('memory.json', 'w') as fp:
            json.dump(total_dict, fp)
    return total_dict


def json_to_memory(mes_json):
    """Handle the memory from the frontend."""

    if isinstance(mes_json, str):
        # If mes_json is a string, parse it as JSON
        mes_dict = json.loads(mes_json)
    elif isinstance(mes_json, dict):
        # If mes_json is already a dictionary, use it directly
        mes_dict = mes_json
    else:
        raise TypeError(
            'mes_json must be a string or a dictionary', type(mes_json))
    # return an empty memory if no messages
    if 'messages' not in mes_dict or len(mes_dict['messages']) == 0:
        print('No messages in memory')
        return ConversationBufferMemory(memory_key="chat_history")

    mes = messages_from_dict(mes_dict['messages'])
    print('mes', mes)
    mem = ConversationBufferMemory(
        chat_memory=ChatMessageHistory(messages=mes), memory_key="chat_history")
    return mem


def get_last_human_msg_from_mem(memory):
    """Get the last human message from memory. And remove from memory to make a prediction."""
    messages = memory.chat_memory.messages
    for msg in messages[::-1]:
        if msg.type == 'human':
            memory.chat_memory.messages.remove(msg)
            return msg.content
    return ''
