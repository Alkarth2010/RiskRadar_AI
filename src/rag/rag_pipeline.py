import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings(
    "ignore",
    message="The class `HuggingFaceEmbeddings`.*",
    category=Warning,
)

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
from pathlib import Path

from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS

from langchain_community.embeddings import (
    HuggingFaceEmbeddings
)

from src.utils.s3_storage import (
    build_s3_key,
    download_prefix,
    use_s3_storage,
)


class RiskRadarRAG:

    def __init__(self):

        load_dotenv()

        self.api_key = os.getenv("GOOGLE_API_KEY")

        if use_s3_storage():
            self.policy_dir = str(
                Path(".cache") / "s3" / "data" / "policies"
            )
            download_prefix(
                build_s3_key("data/policies/"),
                Path(self.policy_dir),
                suffix=".txt",
            )
        else:
            self.policy_dir = "data/policies"

        print("Initializing local embedding model...")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
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

    def retrieve_policy_context(
        self,
        policy_names,
        question="Provide investigation guidance"
    ):
        """
        Retrieve context for specific policies.
        """

        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )

        query = (
            " ".join(policy_names)
            + " "
            + question
        )

        docs = retriever.invoke(query)

        context = "\n\n".join(
            [doc.page_content for doc in docs]
        )

        sources = list(
            set(
                [
                    doc.metadata.get(
                        "source",
                        "unknown"
                    ).split("/")[-1]
                    for doc in docs
                ]
            )
        )

        return {
            "context": context,
            "sources": sources
        }

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

            if not self.api_key:
                raise ValueError(
                    "GOOGLE_API_KEY is required for LLM policy Q&A."
                )

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
