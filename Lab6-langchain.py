import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# initialize antrophic llm
#llm = init_chat_model(
    #model="claude-haiku-4-5-20251001",
    #model_provider="anthropic",
    #temperature=0,
    #max_tokens=1024,
#)

# initialize openai llm
llm = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai",
    temperature=0,
    max_tokens=1024,
)

# Show title and description.
st.title("Lab 6 with LangChain")
st.write(" ")
st.title("Movie Recommendation Chatbot")
st.write("Get movie recommendations based on genre and mood preferences and learn about the suggested options!")
st.write("Indicate your preferences in the sidebar and then click the 'Recommend Movies' button")
st.write(" ")

# sidebar
st.sidebar.header("Your Movie Preferences:")
genre = st.sidebar.selectbox(
    'Preferred movie genre', 
    ('Action', 'Comedy', 'Horror', 'Drama', 'Sci-Fi', 'Thriller', 'Romance')
)
mood = st.sidebar.selectbox(
    'What mood are you in/want to be in?',
    ('Excited', 'Happy', 'Sad', 'Bored', 'Scared', 'Romantic', 'Curious', 'Tense', 'Melancholy')
)
persona = st.sidebar.selectbox(
    'How would you describe yourself?',
    ('Film Critic', 'Casual Friend', 'Movie Journalist', 'Hopeless Romantic')
)

# build prompt template and chain
prompt_template = """You are a {persona}

Recommend exactly 3 movies that match these preferences:
-Genre: {genre}
-Mood: {mood}

For each movie provide:
1. Movie title
2. one or two notable actors and actresses in the cast
3. a brief 1-2 sentence description
4. a brief 1-2 sentence explanation about why it fits the {genre} genre and {mood} mood

Respond in the tone and style of a {persona}

"""

prompt = PromptTemplate(
    input_variables=["genre", "mood", "persona"],
    template = prompt_template
)

chain = prompt | llm | StrOutputParser()

# initialize session state
if "last_recommendation" not in st.session_state:
    st.session_state.last_recommendation = None

if "followup_response" not in st.session_state:
    st.session_state.followup_response = None
    
if "follow_up" not in st.session_state:
    st.session_state.follow_up = ""

# invoke chain
if st.button("Recommend Movies"):
    with st.spinner(f"As a {persona}, you are feeling {mood} and want to watch a {genre} movie..."):
        
        recommendations = chain.invoke({
            "genre": genre,
            "mood": mood,
            "persona": persona
        })
    
        st.session_state.last_recommendation = recommendations
        st.session_state.followup_response = None
        st.session_state.follow_up = "" 

if st.session_state.last_recommendation:
    st.write(" ")
    st.write(st.session_state.last_recommendation)

    # for follow-up questions
    st.divider()

    follow_up = st.text_input('Ask any follow-up questions about the recommended movies: ',
                              key = 'follow_up')

    # question asking prompt template and chain
    question_template = """You are a {persona}

    You recommended {recommendations} based on this criteria:
    -Genre: {genre}
    -Mood: {mood}

    The user asked '{follow_up}'

    Provide a brief but detailed answer to this question, no longer than one paragraph.

    Respond in the tone and style of a {persona}

    """

    question_prompt = PromptTemplate(
        input_variables=["genre", "mood", "persona", "recommendations", "follow_up"],
        template = question_template
    )

    question_chain = question_prompt | llm | StrOutputParser()

    # invoke chain
    if follow_up:
        followup_response = question_chain.invoke({
            "genre": genre,
            "mood": mood,
            "persona": persona,
            "follow_up": follow_up,
            "recommendations": st.session_state.last_recommendation
        })
        
        st.session_state.followup_response = followup_response

    if st.session_state.followup_response:    
        st.write(" ")
        st.write(st.session_state.followup_response)

