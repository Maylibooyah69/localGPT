

def load_GPT4all(path='../chatModels/mistral-7b-instruct-v0.1.Q4_0.gguf', chat_model=True):
    from langchain_community.llms import GPT4All
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    from langchain_experimental.chat_models import Llama2Chat
    callbacks = [StreamingStdOutCallbackHandler()]
    model = GPT4All(model=path,
                    callbacks=callbacks, verbose=True)
    if chat_model:
        chat = Llama2Chat(llm=model)
        return chat
    return model


def load_openAI(chat=True):
    if chat:
        from langchain.llms import OpenAIChat
        return OpenAIChat(openai_api_key="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")
    else:
        from langchain.llms import OpenAI
        return OpenAI(openai_api_key="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")
