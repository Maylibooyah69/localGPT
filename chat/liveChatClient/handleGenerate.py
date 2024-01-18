from langchain.schema import SystemMessage
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from operator import itemgetter
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain_community.llms import GPT4All
from langchain.schema import messages_from_dict, messages_to_dict
from langchain_experimental.chat_models import Llama2Chat
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
import json

# model = GPT4All("./chatModels/mistral-7b-instruct-v0.1.Q4_0.gguf")
callbacks = [StreamingStdOutCallbackHandler()]
model = GPT4All(model="../chatModels/mistral-7b-instruct-v0.1.Q4_0.gguf",
                callbacks=callbacks, verbose=True)

template_messages = [
    SystemMessage(content="You are a helpful assistant."),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{text}"),
]
prompt_template = ChatPromptTemplate.from_messages(template_messages)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful chatbot"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)
chat = Llama2Chat(llm=model)
memory = ConversationBufferMemory(return_messages=True)
chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(
            memory.load_memory_variables) | itemgetter("history")
    )
    | prompt
    | chat
)

inputs = {"input": "hi im bob"}
response = chain.invoke(inputs)
print(response)

memory.save_context(inputs, {"output": response.content})
memory.load_memory_variables({})


extracted_messages = chain.memory.chat_memory.messages
extracted_messages


ingest_to_db = messages_to_dict(extracted_messages)
print(ingest_to_db)

retrieve_from_db = json.loads(json.dumps(ingest_to_db))
print(retrieve_from_db)

retrieved_messages = messages_from_dict(retrieve_from_db)
print(retrieved_messages)

retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
print(retrieved_chat_history)
