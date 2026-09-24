import re


def clean_text(text):
    text = re.sub(r'\.{4,}\s*\d*', '', text)
    text = re.sub(r'^[a-z]{1,8}\.\)\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)
    return text.strip()