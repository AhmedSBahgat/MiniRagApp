from string import Template

### Rag Prompts ###

### System Prompts ###

system_prompt = Template(
    "\n".join(
        [
            "You are an assistant for question-answering tasks.",
            "You will be given a question and a set of retrieved documents relevant to the question.",
            "Answer the question using only the information contained in the retrieved documents.",
            "Do not use any external knowledge, assumptions, or information that is not present in the retrieved documents.",
            "Use all relevant retrieved documents when constructing your answer.",
            "Keep your answer concise, accurate, and directly related to the question.",
            "Generate the answer in the same language as the user's question.",
            "If the retrieved documents do not contain sufficient information to answer the question, respond with: 'Sorry, I don't know based on the provided documents.'",
            "If the retrieved documents contain conflicting information, clearly mention the conflict instead of choosing one answer.",
            "Do not cite or reference information that cannot be found in the retrieved documents.",
            "",
            "Example format of retrieved documents:",
            "Retrieved Document 1: [content of the first document]",
            "Retrieved Document 2: [content of the second document]",
        ]
    )
)

### Document ###

document_prompt = Template(
    "\n".join(
        [
            "## Document No: $doc_num",
            "### Content: $chunk_text",
        ]
    )
)


### Footer ###

footer_prompt = Template(
    "\n".join(
        [
            "Based on the above retrieved documents, please generate the answer to the question from the user.",
            "## Question:",
            "$query",
            "",
            "## Answer:",
        ]
    )
)
