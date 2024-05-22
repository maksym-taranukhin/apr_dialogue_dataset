def save_documents(docs):
    with open("documents.txt", "a", encoding='utf-8') as file:
        for doc in docs:
            file.write(doc + "\n\n")
