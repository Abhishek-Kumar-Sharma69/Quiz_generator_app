import os
import google.generativeai as genai
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the API key
# api_key = os.getenv("GEMINI_API_KEY") 
api_key=st.secrets["api"]["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

def call_gemini_api(prompt, model="models/gemini-1.5-flash", max_tokens=150):
    """Call Gemini API to generate text based on the prompt."""
    response = genai.GenerativeModel(model).generate_content(
        contents=[prompt]
    )
    if response.candidates:
        return response.candidates[0].content.parts[0].text
    else:
        return "No response received from the model."

def create_the_quiz_prompt_template():
    """Create the prompt template for the quiz app."""
    template = """
    You are an expert quiz maker for technical fields. Let's think step by step and
    create a quiz with {num_questions} {quiz_type} questions about the following concept/content: {quiz_context}.

    The format of the quiz could be one of the following:
    - Multiple-choice: 
    - Questions:
        <Question1>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
        <Question2>: <a. Answer 1>, <b. Answer 2>, <c. Answer 3>, <d. Answer 4>
        ....
    - Answers:
        <Answer1>: <a|b|c|d>
        <Answer2>: <a|b|c|d>
        ....
        Example:
        - Questions:
        - 1. What is the time complexity of a binary search tree?
            a. O(n)
            b. O(log n)
            c. O(n^2)
            d. O(1)
        - Answers: 
            1. b
    - True-false:
        - Questions:
            <Question1>: <True|False>
            <Question2>: <True|False>
            .....
        - Answers:
            <Answer1>: <True|False>
            <Answer2>: <True|False>
            .....
        Example:
        - Questions:
            - 1. What is a binary search tree?
            - 2. How are binary search trees implemented?
        - Answers:
            - 1. True
            - 2. False
    - Open-ended:
    - Questions:
        <Question1>: 
        <Question2>:
    - Answers:    
        <Answer1>:
        <Answer2>:
    Example:
        Questions:
        - 1. What is a binary search tree?
        - 2. How are binary search trees implemented?

        - Answers: 
            1. A binary search tree is a data structure that is used to store data in a sorted manner.
            2. Binary search trees are implemented using linked lists.
    """
    prompt = PromptTemplate.from_template(template)
    return prompt

def create_quiz_chain(prompt_template, model_name):
    """Creates the chain for the quiz app."""
    def chain_fn(inputs):
        prompt = prompt_template.format(**inputs)
        return call_gemini_api(prompt, model=model_name)
    return chain_fn

def split_questions_answers(quiz_response):
    """Function that splits the questions and answers from the quiz response."""
    questions = quiz_response.split("**Answers:**")[0]
    answers = quiz_response.split("**Answers:**")[1]
    return questions, answers

def main():
    st.title("Quiz App")
    st.write("This app generates a quiz based on a given context.")
    prompt_template = create_the_quiz_prompt_template()
    
    context = st.text_area("Enter the concept/context for the quiz")
    num_questions = st.number_input("Enter the number of questions", min_value=1, max_value=10, value=3)
    quiz_type = st.selectbox("Select the quiz type", ["multiple-choice", "true-false", "open-ended"])
    model_name = st.selectbox("Select the model", ["models/gemini-1.5-flash", "models/gemini-1.5-pro"])
    
    if st.button("Generate Quiz"):
        chain_fn = create_quiz_chain(prompt_template, model_name)
        quiz_response = chain_fn({"num_questions": num_questions, "quiz_type": quiz_type, "quiz_context": context})
        st.write("Quiz Generated!")
        questions, answers = split_questions_answers(quiz_response)
        st.session_state.answers = answers
        st.session_state.questions = questions
        st.write(questions)
    
    if st.button("Show Answers"):
        st.markdown(st.session_state.questions)
        st.write("----")
        st.markdown(st.session_state.answers)

if __name__ == "__main__":
    main()
