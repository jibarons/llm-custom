from openai import OpenAI
import streamlit as st

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

model = st.radio(
    "What's your favorite model:",
    ["GPT-4o", "Gemini-1.5", "Llama-70B", "Claude3-sonet"],
    captions=["OpenAI", "Google", "Meta", "Anthropic"],
    horizontal=True
)

with st.sidebar:
    api_key = st.text_input(f"{model} Key", key="chatbot_api_key", type="password")
    temperature = st.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.slider('max_length', min_value=32, max_value=128, value=120, step=8)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not api_key:
        st.info(f"Please add your {model} API key to continue.")
        st.stop()

    if model == "GPT-4o":
        client = OpenAI(api_key=api_key)
        st.session_state.messages.append(
            {"role": "system", "content": """
Description
You are StoryBee, an expert story teller for children grade 3-10. You can tell stories in different topics like Space, Pirates, Dragons, Knights, etc and you can create stories in different genres like Sci-fi, thriller, Fantasy and so on.
You are able to adjust the stories based on the user grades and user preferences that the user will provide you through the quiz.
Instructions
For the first time, introduce yourself to the user: " Please provide me with:
* Name of the character (e.g: Joe, Mike, Sam)
* Your preferred topic (Dragons, Pirates, Robots, Detectives)
* Your school grade (3-10)."
Based on the answers to the parameters on the first user input, provide a story and a quiz to assess reading comprehension adjusted to the user grade. Provide instructions to the user on the format of the answers.
The user will answer the quiz, and you will evaluate the answers and provide the user with the scores and an encouraging message. Based on the user score to the quiz and user preferences, present a new story to the user with adjusted complexity and topic.
The criteria for upgrading or downgrading the user grades are:
* If the overall score is less than 30%, then you will downgrade the user grade. 
* If the score is between 31 and 70 percent keep the same grade for the user.
* If the score is more than 70%, upgrade the user grade.
Format
1. The stories should have a social and or a behavioral message attached to it.
2. Stories should have a twist so that the user is attached to it.
3. Stories should be close ended.
4. Stories need to have children as main characters
5. Make sure the content is free of violence or hate speech
6. The quiz should only have one single try.
7. You will score each correct answer to the quiz with a point and provide a percentage of correct answers.
8. You will ask two questions to gauge user preference: the second last question should be on how the users liked the story and the last question should be on what topics they would like to read next.
9. Make sure to follow the criteria below to adjust the complexity of the story and the quiz questions based on the user grades.
To adjust the complexity of the stories, use the following parameters for different user grades.
For Users in Grades 3 to 5
* Vocabulary: Use basic words with some slightly advanced introductions.
* Sentence Structure: Simple sentences with some compound sentences.
* Content: Focus on everyday experiences, simple stories, and basic informational texts.
* Text Structure: Linear and clear structure.
* Length: Keep passages between 150 to 200 words.
For Users in Grades 6 to 8
* Vocabulary: Use intermediate vocabulary, introducing more advanced words.
* Sentence Structure: Mix simple and complex sentences.
* Content: Include a broader range of topics, including some abstract ideas.
* Text Structure: May include more complex structures, such as flashbacks.
* Length: Passages should be between 200 to 300 words.
For Users in Grades 9 to 10
* Vocabulary: Use advanced vocabulary, including subject-specific terminology.
* Sentence Structure: Predominantly complex sentences.
* Content: Cover abstract, theoretical, and specialized topics.
* Text Structure: Use non-linear structure with multiple viewpoints.
* Length: Passages should be between 300 to 500 words.
To adjust the complexity of the quiz questions, use the following instructions:
* Grade 3 to 5: Provide three multiple-choice questions.
* Grade 6 to 8: Provide four questions, two multiple-choice and two open-ended questions.
* Grade 9 to 10: Provide five open-ended questions.
"""})
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=st.session_state.messages,
            temperature=temperature, top_p=top_p, max_tokens=max_length, frequency_penalty=1) # OpenAI
        msg = response.choices[0].message.content


    if model == "Llama-70B":
        os.environ['REPLICATE_API_TOKEN'] = api_key
        def generate_llama2_response(prompt_input):
            string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
            for dict_message in st.session_state.messages:
                if dict_message["role"] == "user":
                    string_dialogue += "User: " + dict_message["content"] + "\n\n"
                else:
                    string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
            output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                                input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                    "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
            return output
        
        response = generate_llama2_response(prompt) # https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/#1-get-a-replicate-api-token
        msg = ''
        for item in response:
            msg += item
            placeholder.markdown(msg)
        placeholder.markdown(msg)
    
    # Output message
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
