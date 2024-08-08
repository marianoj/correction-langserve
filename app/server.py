#!/usr/bin/env python
from typing import List, Union
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langserve import add_routes
from langserve.pydantic_v1 import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from pirate_speak.chain import chain as pirate_speak_chain
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# from anthropic_iterative_search import chain as anthropic_iterative_search_chain
# from csv_agent.agent import agent_executor as csv_agent_chain

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

add_routes(app, pirate_speak_chain, path="/pirate-speak")
model = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
add_routes(
    app,
    prompt | model,
    path="/joke",
    enable_feedback_endpoint=True,
    enable_public_trace_link_endpoint=True,
    playground_type="chat",
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful, professional assistant named Ayyaz."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
chain = prompt | ChatOpenAI(model="gpt-4o-mini")

class InputChat(BaseModel):
    """Input for the chat endpoint."""

    messages: List[Union[HumanMessage, AIMessage, SystemMessage]] = Field(
        ...,
        description="The chat messages representing the current conversation.",
    )

add_routes(
    app,
    chain.with_types(input_type=InputChat),
    enable_feedback_endpoint=True,
    enable_public_trace_link_endpoint=True,
    playground_type="chat",
)

# add_routes(app, anthropic_iterative_search_chain, path="/anthropic-iterative-search")
# add_routes(app, csv_agent_chain, path="/csv-agent")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)