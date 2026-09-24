def build_context(retrieved_chunks):
    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks, start=1):
        block = f"[Source {i}: {chunk['source_file']}]\n{chunk['text']}"
        context_blocks.append(block)
    return "\n\n---\n\n".join(context_blocks)