from services.llm import llm

response = llm.invoke("Reply with exactly: Connection Successful")

print(response.content)