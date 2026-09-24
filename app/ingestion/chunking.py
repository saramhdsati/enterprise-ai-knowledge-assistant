import re


def chunk_by_headings(text, min_chunk_size=100):
    heading_pattern = re.compile(
        r'^(#{1,3}\s+.+|(\d+\.)+\d*\s*[-–]?\s*.+)$',
        re.MULTILINE
    )

    lines = text.split('\n')
    chunks = []
    current_chunk = []
    seen_first_heading = False

    for line in lines:
        is_heading = bool(heading_pattern.match(line.strip())) and len(line.strip()) < 100

        if is_heading and current_chunk:
            if seen_first_heading:
                # فلش الـ chunk العادي
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                current_chunk = [line]
            else:
                # ده أول heading — سيبي المقدمة (عنوان/ميتاداتا) ملصوقة بيه، متعملهاش chunk لوحدها
                current_chunk.append(line)
                seen_first_heading = True
        else:
            current_chunk.append(line)

    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        if chunk_text:
            chunks.append(chunk_text)

    merged_chunks = []
    buffer = ""
    for chunk in chunks:
        buffer = (buffer + "\n\n" + chunk).strip() if buffer else chunk
        if len(buffer) >= min_chunk_size:
            merged_chunks.append(buffer)
            buffer = ""
    if buffer:
        if merged_chunks:
            merged_chunks[-1] += "\n\n" + buffer
        else:
            merged_chunks.append(buffer)

    return merged_chunks