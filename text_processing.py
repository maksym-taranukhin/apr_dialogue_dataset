import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def advanced_text_splitter(text, max_chunk_size=1000):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    for sentence in sentences:
        if sum(len(s) for s in current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk.append(sentence)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks
