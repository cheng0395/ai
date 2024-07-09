import os

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# 使用全局变量来存储会话历史记录
session_store = {}

def get_response(key, user_input, session_id):
    os.environ["DASHSCOPE_API_KEY"] = key

    llm = ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus"
    )

    # 加载文本
    loader = TextLoader("D:\pycharm project\Ai_project\data\mi_data.txt", encoding="utf-8")
    document = loader.load()

    # 文本切割
    text_split = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", "，", " ", ""]
    )

    documents = text_split.split_documents(document)

    # 文本向量化以及数据库存储
    embedding_model = DashScopeEmbeddings(
        model="text-embedding-v1"
    )

    db = FAISS.from_documents(documents, embedding_model)

    retriever = db.as_retriever()

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in session_store:
            # 在每个会话开始时创建新的 ChatMessageHistory 实例
            session_store[session_id] = ChatMessageHistory()
        return session_store[session_id]

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    # 传入相同的 session_id 可以保持会话的连贯性。如果你传入不同的 session_id，则会开始一个新的会话。
    response = conversational_rag_chain.invoke({"input": user_input},
                                               config={"configurable": {"session_id": session_id}}, )

    return response["answer"]


def get_chat_history(session_id):
    if session_id in session_store:
        history = session_store[session_id]
        return history.messages
    else:
        return []


# print(get_response("sk-8dfba49211db4a349e8f3534cf70a0ae", "我叫卤蛋", "abc123"))
# print(get_response("sk-8dfba49211db4a349e8f3534cf70a0ae", "我叫什么", "abc123"))
