import os
import json
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph.graph import MessagesState, StateGraph, START, END

# Show title and description.
st.title("Lab 9")
st.write(" ")
st.title("Multi-Agent Trip Planner")
st.write("A supervisor agent will be used to ochestrate three specialist agents- research, budget, and itinerary- to plan a trip. ")
st.write(" ")

# openai client
client = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# openai instances 
agent_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
supervisor_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# load data
with open("travel_data.json", 'r') as f:
    TRAVEL_DATA = json.load(f)

# define tools
@tool
def search_destination(query: str) -> str:
    """Search for information about a travel destination."""

    for city, data in TRAVEL_DATA["destinations"].items():
        if query.strip().lower() in city.lower():
            return json.dumps({
                "destinations": city,
                "info": data
                })

    return json.dumps({"destination": query,
                       "info": "No information found."})

@tool
def calculate_budget(destination: str, days: int, budget_level: str) -> str:
    """Calculate a budget for a trip based on destination, duration, and budget level."""

    if budget_level.strip().lower() not in TRAVEL_DATA["daily_costs"]:
        return json.dumps({"error": "Invalid budget level."})
    
    daily = TRAVEL_DATA["daily_costs"][budget_level.strip().lower()]
    daily_total = sum(daily.values())
    total_cost = daily_total * days

    flight_cost = TRAVEL_DATA["flight_estimates"].get(destination.strip().lower(), TRAVEL_DATA["flight_estimates"]["default"])
    
    trip_cost = total_cost + flight_cost

    return json.dumps({
        "destination": destination,
        "days": days,
        "budget_level": budget_level,
        "breakdown": {
            "daily_costs": daily,
            "daily_total": daily_total,
            "total_cost": total_cost,
            "flight_cost": flight_cost
        },
        "trip_cost": trip_cost,
        "money_saving_tips": TRAVEL_DATA["money_saving_tips"]
    })

@tool
def create_schedule(destination: str, days: int, interests: str) -> str:
    """Create a daily itinerary for a trip based on destination, duration, and interests."""

    interest_list = [i.strip().lower() for i in interests.split(",")]

    activity_pool = []
    for interest in interest_list:
        if interest in TRAVEL_DATA["activities"]:
            activity_pool.extend(TRAVEL_DATA["activities"][interest])

    if not activity_pool:
        activity_pool = [
        "General city exploration",
        "Local food tasting",
        "Visit a popular landmark"
    ]

    schedule = []
    slots = ["Morning", "Afternoon", "Evening"]
    
    for day in range(1, days + 1):
        day_plan = {}
        for slot in slots:
            index = (day + len(schedule) + len(slot)) % len(activity_pool)
            day_plan[slot] = activity_pool[index]

        schedule.append({
            'day': day,
            'destination': destination,
            'plan': day_plan
        })

    return json.dumps({
        "destination": destination,
        "days": days,
        "interests": interest_list,
        "schedule": schedule
    })

# create agents
research_agent = create_react_agent(
    model=agent_llm,
    tools=[search_destination],
    name="research_agent",
    prompt=("You are a travel research specialist. Your ONLY job is to look up destination information." \
    "Always use the search_destination tool to find information about the destination. " \
    "Do not provide any information that is not from the tool. Always use the tool when asked about the destination." \
    "Do not make up any information."
    )
)

budget_agent = create_react_agent(
    model=agent_llm,
    tools=[calculate_budget],
    name="budget_agent",
    prompt=("You are a travel budget specialist. Your ONLY job is to calculate the budget for a trip." \
    "Always use the calculate_budget tool to compute the trip budget based on the destination, duration, and budget level." \
    "Do not provide any information that is not from the tool. Always use the tool when asked about the budget." \
    "Do not make up any information."
    )   
)

itinerary_agent = create_react_agent(
    model=agent_llm,
    tools=[create_schedule],
    name="itinerary_agent",
    prompt=("You are a travel itinerary specialist. Your ONLY job is to create a daily schedule for a trip." \
    "Always use the create_schedule tool to generate a daily itinerary based on the destination, duration, and interests." \
    "Do not provide any information that is not from the tool. Always use the tool when asked about the itinerary." \
    "Do not make up any information."
    )   
)

# create supervisor
supervisor_prompt = """
You are the Supervisor Agent responsible for coordinating three specialist agents.
Your job is to read the user's request, decide which specialist(s) should handle it,
and then synthesize their outputs into one clear, organized final response.

You have access to the following agents:

1. research_agent — Handles destination information, highlights, culture, weather, and travel tips.
2. budget_agent — Handles cost estimates, daily expenses, flight estimates, and budget planning.
3. itinerary_agent — Handles day-by-day schedules and activity planning based on interests.

Routing rules:
- If the user asks about a destination, send the task to research_agent.
- If the user asks about costs, prices, or budgeting, send the task to budget_agent.
- If the user asks about schedules, activities, or itineraries, send the task to itinerary_agent.
- If the user asks for full trip planning (e.g., “Plan my trip to Tokyo”), call ALL THREE agents.

After receiving the outputs from the selected agents:
- Combine their results into one cohesive, well-structured response.
- Do NOT invent information. Only use what the agents return.
- Present the final answer in a friendly, organized, easy-to-read format.
"""

workflow = create_supervisor(
    agents=[research_agent, budget_agent, itinerary_agent],
    model=supervisor_llm,
    name="Supervisor",
    prompt=supervisor_prompt
)

multi_agent_app = workflow.compile()

# streamlit interface
with st.sidebar:
    st.header("Trip Details")

    destination = st.text_input("Destination")
    duration = st.slider("Duration (days)", min_value=1, max_value=30)
    budget_level = st.selectbox("Budget Level", options=["budget", "moderate", "luxury"])
    interests = st.multiselect("Interests", options=["Culture", "Food", "Nature", "Nightlife", "History"])

if 'ma_result' not in st.session_state:
    st.session_state.ma_result = None

if 'ma_messages' not in st.session_state:
    st.session_state.ma_messages = None

interest_str = ", ".join(interests)

query = (
    f"Plan a {duration}-day trip to {destination}. "
    f"My budget level is {budget_level.lower()}. "
    f"My interests include: {interest_str}. "
    f"Please provide destination research, a budget breakdown, "
    f"and a day-by-day itinerary."
)

st.subheader("Your Query")
st.write(query)
st.write(" ")

if st.button("Plan My Trip"):
    with st.spinner("Planning your trip..."):
        result = multi_agent_app.invoke({
            "messages": [{"role": "user", "content": query}]
        })

        st.session_state.ma_result = result
        st.session_state.ma_messages = result["messages"]

if st.session_state.ma_messages:
    st.subheader("Your Travel Plan")
    final_answer = st.session_state.ma_messages[-1].content
    st.markdown(final_answer)

result = st.session_state.ma_result

if result:
    with st.sidebar:
        st.subheader("Agent Activity Log:")

        agent_emojis = {
            "research_agent": "🔎",
            "budget_agent": "💰",
            "itinerary_agent": "🗺️",
            "Supervisor": "🧠"
        }

        agent_tools = {
            "research_agent": "search_destination",
            "budget_agent": "calculate_budget",
            "itinerary_agent": "create_schedule",
        }

        lines = []
        seen = set()
        messages = result["messages"]

        for msg in messages:
            msg_name = getattr(msg, "name", None)

            if msg_name in agent_emojis and msg_name not in seen:
                seen.add(msg_name)
                lines.append(f"{agent_emojis[msg_name]}  **{msg_name}**")

                if msg_name in agent_tools:
                    lines.append(f"&nbsp;&nbsp;&nbsp;↳ 🛠️ `{agent_tools[msg_name]}`")

                lines.append("")

        st.markdown("\n\n".join(lines))

######## chat bot mode
def to_dict_message(msg):
    if isinstance(msg, dict):
        return msg
    return {"role": msg.role, "content": msg.content}

# define graph nodes
def supervisor_node(state: MessagesState):
    last_msg = state["messages"][-1]["content"].strip().lower()

    if "research" in last_msg or "destination" in last_msg:
        route = "research"
    elif "budget" in last_msg or "cost" in last_msg or "price" in last_msg:
        route = "budget"
    elif "itinerary" in last_msg or "schedule" in last_msg or "activities" in last_msg:
        route = "itinerary"
    elif "plan" in last_msg or "trip" in last_msg:
        route = "all"
    else:
        route = "chat"

    return {
        "messages": state["messages"] + [
            {"role": "assistant", "content": route}
        ]
    }

def research_node(state: MessagesState):
    user_msg = state["messages"][-1]["content"]

    result = research_agent.invoke({
        "messages": [{"role": "user", "content": user_msg}]
    })

    return {
        "messages": state["messages"] + [
            {"role": "assistant", "content": result["messages"][-1].content}
        ]
    }

def budget_node(state: MessagesState):
    user_msg = state["messages"][-1]["content"]

    result = budget_agent.invoke({
        "messages": [{"role": "user", "content": user_msg}]
    })

    return {
        "messages": state["messages"] + [
            {"role": "assistant", "content": result["messages"][-1].content}
        ]
    }

def itinerary_node(state: MessagesState):
    user_msg = state["messages"][-1]["content"]

    result = itinerary_agent.invoke({
        "messages": [{"role": "user", "content": user_msg}]
    })

    return {
        "messages": state["messages"] + [
            {"role": "assistant", "content": result["messages"][-1].content}
        ]
    }

def run_all_agents(state: MessagesState):
    user_msg = state["messages"][-1]["content"]

    r = research_agent.invoke({"messages": [{"role": "user", "content": user_msg}]})
    b = budget_agent.invoke({"messages": [{"role": "user", "content": user_msg}]})
    i = itinerary_agent.invoke({"messages": [{"role": "user", "content": user_msg}]})

    combined = (
        "Destination Research\n" + r["messages"][-1].content + "\n\n" +
        "Budget Estimate\n" + b["messages"][-1].content + "\n\n" +
        "Itinerary\n" + i["messages"][-1].content
    )

    return {
        "messages": state["messages"] + [
            {"role": "assistant", "content": combined}
        ]
    }

def synthesizer_node(state: MessagesState):
    all_text = "\n\n".join([m["content"] for m in state["messages"]])

    final_prompt = (
        "Combine the following agent outputs into a clean, organized final answer:\n\n"
        + all_text
    )

    result = supervisor_llm.invoke([{"role": "user", "content": final_prompt}])

    return {
        "messages": state["messages"] + [
            {"role": "assistant", "content": result.content}
        ]
    }

# define router
def route_from_supervisor(state: MessagesState):
    last_msg = state['messages'][-1].content.strip().lower()
    if 'research' in last_msg:
        return 'research'
    elif 'budget' in last_msg:
        return 'budget'
    elif 'itinerary' in last_msg:
        return 'itinerary'
    elif 'all' in last_msg:
        return 'all'
    else:
        return 'chat'

# build stateGraph
chatbot_graph = StateGraph(MessagesState)

# Add nodes
chatbot_graph.add_node('supervisor', supervisor_node)
chatbot_graph.add_node('research', research_node)
chatbot_graph.add_node('budget', budget_node)
chatbot_graph.add_node('itinerary', itinerary_node)
chatbot_graph.add_node('all_agents', run_all_agents)
chatbot_graph.add_node('synthesizer', synthesizer_node)

# Edges
chatbot_graph.add_edge(START, 'supervisor')
chatbot_graph.add_conditional_edges(
    'supervisor',
    route_from_supervisor,
    {
        'research': 'research',
        'budget': 'budget',
        'itinerary': 'itinerary',
        'all': 'all_agents',
        'chat': 'synthesizer',
    },
)

chatbot_graph.add_edge('research', 'synthesizer')
chatbot_graph.add_edge('budget', 'synthesizer')
chatbot_graph.add_edge('itinerary', 'synthesizer')
chatbot_graph.add_edge('all_agents', 'synthesizer')
chatbot_graph.add_edge('synthesizer', END)

chatbot_app = chatbot_graph.compile()

# streamlit interface
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.write("---")
st.subheader("Ask about your trip")

user_input = st.chat_input(" ")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Thinking..."):
        result = chatbot_app.invoke({
            "messages": st.session_state.chat_history
        })

    final_response = result["messages"][-1].content

    st.session_state.chat_history.append({"role": "assistant", "content": final_response})

    with st.chat_message("assistant"):
        st.markdown(final_response)

