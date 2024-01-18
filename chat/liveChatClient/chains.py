from langchain_community.llms import GPT4All
from langchain.prompts import PromptTemplate
# from gpt4all import GPT4All
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
callbacks = [StreamingStdOutCallbackHandler()]
# model = GPT4All(model_name='mistral-7b-instruct-v0.1.Q4_0.gguf',
#                 model_path=('../chatModels/'),
#                 allow_download=False)
model = GPT4All(model="../chatModels/mistral-7b-instruct-v0.1.Q4_0.gguf",
                callbacks=callbacks, verbose=True)


prompt = PromptTemplate(
    input_variables=["topic"], template="Tell me a joke about {topic}.")

chain = prompt | model | StrOutputParser()

print(chain.invoke({"topic": "Uraeus"})[0])
