from app.core import state


def rewrite_query(current_question, chat_history):
    if not chat_history:
        return current_question

    history_text = "\n".join(
        f"{turn['role']}: {turn['text']}" for turn in chat_history[-4:]
    )

    rewrite_prompt = f"""Given this conversation history and a follow-up question,
rewrite the follow-up question to be a standalone question that includes all necessary context.
Only output the rewritten question, nothing else.

CONVERSATION HISTORY:
{history_text}

FOLLOW-UP QUESTION: {current_question}

STANDALONE QUESTION:"""

    response = state.groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": rewrite_prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content.strip()


def generate_answer(question, context):
    system_prompt = """You are an internal company assistant for NovaBridge Technologies Inc.
Answer the employee's question using ONLY the information explicitly stated in the provided sources below.

STRICT RULES — follow all of them:
1. Every fact, number, date, or name in your answer must be traceable to an exact statement in the sources. Do not infer, estimate, combine, or extrapolate information that is not explicitly written.
2. If the sources only partially answer the question, answer only the part that is explicitly supported, and clearly state which part is missing or not covered.
3. If none of the sources contain relevant information to answer the question, respond with exactly: "I couldn't find this information in the company documents." Do not add speculation after this sentence.
4. Never use outside/general knowledge to fill gaps, even if you are confident it is correct. If it is not in the sources, it does not exist for this answer.
5. Do not average, sum, or otherwise mathematically combine numbers from different sources unless the sources explicitly state the combined result.
6. If two sources appear to conflict, point out the conflict instead of picking one silently.
7. At the end of your answer, cite which source(s) you used, like this: (Source: filename.ext). If you said you couldn't find the information, do not cite a source.
8. Be concise and direct."""

    user_prompt = f"""SOURCES:
{context}

QUESTION: {question}"""

    response = state.groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content