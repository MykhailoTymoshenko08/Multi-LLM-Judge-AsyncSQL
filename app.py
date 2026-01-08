import os
import time
import sqlite3
import asyncio

from dotenv import load_dotenv
load_dotenv()
API_KEY=os.getenv("API_KEY")

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
#from langchain_core.messages import SystemMessage

def show_stats():
    conn = sqlite3.connect('my_aggregator.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT model_name, AVG(duration), COUNT(*) 
        FROM requests_history 
        GROUP BY model_name
    ''')
    stats = cursor.fetchall()
    conn.close()
    print("\n--- Model statistic ---")
    if not stats: 
        print("No data yet. Ask a question to collect stats.") 
        return
    for row in stats:
        model_name = row[0] 
        avg_time = float(row[1]) if row[1] is not None else 0.0 
        count = row[2] 
        print(f"Model: {model_name} | Average time: {avg_time:.2f}s | Requests: {count}")
    

def create_db():
    conn = sqlite3.connect('my_aggregator.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            question TEXT,
            model_name TEXT,
            answer TEXT,
            duration REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅Datebase is ready to work")

def save_to_db(question, model, answer, duration):
    conn = sqlite3.connect('my_aggregator.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO requests_history (question, model_name, answer, duration)
        VALUES (?, ?, ?, ?)
    ''', (question, model, answer, duration))
    conn.commit()
    conn.close()

async def get_langchain_answer(model_name, user_text, chat_history=None):
    start_time = time.time()
    llm = ChatOpenAI(
        model = model_name,
        openai_api_key = API_KEY,
        base_url = "https://openrouter.ai/api/v1",
        max_tokens = 200
    )

    if chat_history is None:
        chat_history = []
    #prompt = ChatPromptTemplate("{topic}")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Ти корисний помічник."),
        ("placeholder", "{chat_history}"),
        ("human", "{user_input}")
    ])
    chain = prompt | llm | StrOutputParser()

    result = await chain.ainvoke({
        "chat_history": chat_history or [],
        "user_input": user_text
    })

    duration = time.time() - start_time
    save_to_db(user_text, model_name, result, duration)

    return result

async def judge_answers(user_text, answer1, answer2, model):
    start_time = time.time()
    llm = ChatOpenAI(
        model=model,
        openai_api_key=API_KEY,
        base_url="https://openrouter.ai/api/v1",
        max_tokens=500  
    )
    judge_template = """
    You are an expert who analyzes AI answers.

    Question: {question}

    ANSWER 1:
    {answer1}

    ANSWER 2:
    {answer2}

    Task:
    Using the two answers above, produce one single, high‑quality and concise final answer. Do not explain your reasoning, do not compare the answers, and do not mention which parts you selected. Simply provide the best possible final answer.

    FINAL ANSWER:
    """
    
    prompt = ChatPromptTemplate.from_template(judge_template)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    result = await chain.ainvoke({
        "question": user_text,
        "answer1": answer1,
        "answer2": answer2
    })

    duration = time.time() - start_time
    save_to_db(user_text, f"{model}_JUDGE", result, duration)

    return f"✅{result}"

async def main_async():
    create_db()
    history = []
    while True:
        print("\n" + "="*50)
        print("AI AGGREGATOR-JUDGE")
        print("="*50)

        show_stats()

        print("\n" + "="*50)
        print("MENU:")
        print("1. Ask question")
        print("2. Show detailed statistic")
        print("3. Clear memory")
        print("4. Exit")
        print("="*50)
        choice = input("\nChoose action (1-4): ").strip()

        if choice == "1":
            models = [
                "meta-llama/llama-3.3-70b-instruct:free",
                "google/gemma-3-27b-it:free"
            ]
            judge_model = "mistralai/devstral-2512:free"
            user_input = input("Enter your request: ").strip()

            task1 = get_langchain_answer("meta-llama/llama-3.3-70b-instruct:free", user_input, history)
            task2 = get_langchain_answer("google/gemma-3-27b-it:free", user_input, history)

            answer1, answer2 = await asyncio.gather(task1, task2)  
            print("\n" + "="*50)
            print("Original answers:")
            print(f"Model 1: ✅{answer1}")
            print("\n" + "="*50)
            print(f"Model 2: ✅{answer2}")
            print("\n" + "="*50)
            print("\n" + "="*50)

            final_answer = await judge_answers(user_input, answer1, answer2, judge_model)
            print("\n" + "="*50)
            print("Final answer:")
            print(final_answer)
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content=final_answer.replace("✅", "")))
            pass
        elif choice == "2":
            show_stats()
            pass
        elif choice == "4":
            print("\nBye")
            break
        elif choice == "3":
            history.clear()
            print("\nMemory cleared!")
        else:
            print("❌Try again")
        

if __name__ == "__main__":
    asyncio.run(main_async())