import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# initialize llm
llm = init_chat_model(
    model="claude-haiku-4-5-20251001",
    model_provider="anthropic",
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
    ('Film Critic', 'Casual Friend', 'Movie Journalist')
)

# build prompt template and chain
prompt_template = f"""You are a {persona}

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
if "last_recommnedation" not in st.session_state:
    st.session_state.last_recommendation = None

# invoke chain
if st.button("Recommend Movies"):
    with st.spinner(f"As a {persona}, you are feeling {mood} and want to watch a {genre} movie..."):
        
        response = chain.invoke({
            "genre": genre,
            "mood": mood,
            "persona": persona
        })
    
        st.session_state.last_recommendation = response

        st.write(" ")
        st.write(response)



