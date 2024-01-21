from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from operator import itemgetter


def generate_chat_chain(prompt, memory, chat):
    chain = (
        RunnablePassthrough.assign(
            history=RunnableLambda(
                memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | chat
    )
    return chain, memory


def call_chain(chain, memory, inputs, verbose=False):
    chat_input = {"input": inputs}
    response = chain.invoke(chat_input)
    if verbose:
        print(response)
    memory.save_context(chat_input, {"output": response.content})
    return response
