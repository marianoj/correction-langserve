from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langserve import add_routes
from pirate_speak.chain import chain as pirate_speak_chain
from robocorp_action_server import agent_executor as robocorp_action_server_chain

app = FastAPI()

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

# Define your runnable
runnable = ChatPromptTemplate.from_template("Tell me a joke about {topic}") | ChatOpenAI()

# Edit this to add the chain you want to add
add_routes(app, runnable)
add_routes(app, pirate_speak_chain, path="/pirate-speak")
add_routes(app, robocorp_action_server_chain, path="/robocorp-action-server")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
