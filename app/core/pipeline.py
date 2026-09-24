from app.retrieval.hybrid_search import hybrid_search
from app.generation.context_builder import build_context
from app.generation.llm import generate_answer, rewrite_query


def ask(question, chat_history=None, allowed_departments=None):
    if chat_history is None:
        chat_history = []

    standalone_question = rewrite_query(question, chat_history)
    retrieved_chunks = hybrid_search(standalone_question, top_k=4, allowed_departments=allowed_departments)
    context = build_context(retrieved_chunks)
    answer = generate_answer(standalone_question, context)
    return answer