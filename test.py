from langchain import PromptTemplate, LLMChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

template = """Question: {question}

Answer: Let's think step by step."""

prompt = PromptTemplate(template=template, input_variables=["question"])
callbacks = [StreamingStdOutCallbackHandler()]


question = "What NFL team won the Super Bowl in the year Justin Bieber was born?"
llm_chain = LLMChain(prompt=prompt, llm=llm)
print("running")
print(llm_chain.run(question))
