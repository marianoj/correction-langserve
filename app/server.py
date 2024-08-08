#!/usr/bin/env python
import os
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
from langchain_core.language_models.chat_models import LangSmithParams
from openai_functions_agent import agent_executor as openai_functions_agent_chain
from research_assistant import chain as research_assistant_chain
from rag_conversation import chain as rag_conversation_chain
from rag_ollama_multi_query import chain as rag_ollama_multi_query_chain
from summarize_anthropic import chain as summarize_anthropic_chain
# from market_research import chain as market_research_chain
# from shopping_assistant.agent import agent_executor as shopping_assistant_chain
# from target_audience.agent import agent_executor as target_audience_chain


# from anthropic_iterative_search import chain as anthropic_iterative_search_chain
# from csv_agent.agent import agent_executor as csv_agent_chain

tavily_api_key = os.environ.get('TAVILY_API_KEY')

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
    playground_type="chat",
)

add_routes(
    app,
    ChatAnthropic(model="claude-3-haiku-20240307"),
    path="/anthropic",
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

add_routes(app, openai_functions_agent_chain, path="/openai-functions-agent")
add_routes(app, research_assistant_chain, path="/research-assistant")
add_routes(app, rag_conversation_chain, path="/rag-conversation")
add_routes(app, rag_ollama_multi_query_chain, path="/rag-ollama-multi-query")
add_routes(app, summarize_anthropic_chain, path="/summarize-anthropic")
# add_routes(app, shopping_assistant_chain, path="/shopping-assistant")
# add_routes(app, target_audience_chain, path="/target-audience")
# add_routes(app, market_research_chain, path="/market-research")

# add_routes(app, anthropic_iterative_search_chain, path="/anthropic-iterative-search")
# add_routes(app, csv_agent_chain, path="/csv-agent")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)