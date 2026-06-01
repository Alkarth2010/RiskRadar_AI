import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)


class RiskRadarRAG:

    def __init__(self):

        load_dotenv()

        self.api_key = os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in .env"
            )

        self.policy_dir = "data/policies"
        self.persist_dir = "chroma_db"

        print("Initializing Gemini models...")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=self.api_key
        )

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.2
        )

        self.vectorstore = self._load_or_create_vectorstore()

    def _load_documents(self):

        documents = []

        policy_path = Path(self.policy_dir)

        if not policy_path.exists():
            raise FileNotFoundError(
                f"Folder not found: {self.policy_dir}"
            )

        txt_files = list(policy_path.glob("*.txt"))

        if not txt_files:
            raise ValueError(
                "No policy files found."
            )

        print(f"Found {len(txt_files)} policy files")

        for file in txt_files:

            try:

                loader = TextLoader(
                    str(file),
                    encoding="utf-8"
                )

                docs = loader.load()

                documents.extend(docs)

                print(f"Loaded: {file.name}")

            except Exception as e:

                print(
                    f"Failed loading {file.name}: {e}"
                )

        return documents

    def _create_vectorstore(self):

        docs = self._load_documents()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents(docs)

        print(f"Created {len(chunks)} chunks")

        vectorstore = FAISS.from_documents(
            chunks,
            self.embeddings
        )

        print("FAISS index created")

        return vectorstore

    def _load_or_create_vectorstore(self):

        print("Creating FAISS index...")

        return self._create_vectorstore()

    def query(self, question):

        try:

            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 3}
            )

            docs = retriever.invoke(question)

            context = "\n\n".join(
                [doc.page_content for doc in docs]
            )

            prompt = f"""
You are RiskRadar AI, a fraud investigation assistant.

Answer ONLY using the retrieved policy context.

If the answer is not present in the context,
say:
"I could not find this information in the policy documents."

Policy Context:
{context}

Question:
{question}

Answer:
"""

            response = self.llm.invoke(prompt)

            sources = list(
                set(
                    [
                        os.path.basename(
                            doc.metadata.get(
                                "source",
                                "unknown"
                            )
                        )
                        for doc in docs
                    ]
                )
            )

            return {
                "answer": response.content,
                "sources": sources
            }

        except Exception as e:

            return {
                "answer": f"ERROR: {e}",
                "sources": []
            }


if __name__ == "__main__":

    rag = RiskRadarRAG()

    print("\nRiskRadar RAG Ready")

    while True:

        question = input(
            "\nAsk a policy question (q to quit): "
        )

        if question.lower() == "q":
            break

        result = rag.query(question)

        print("\nANSWER")
        print("-" * 60)
        print(result["answer"])

        print("\nSOURCES")
        print("-" * 60)
        print(result["sources"])