"""
Streamlit web UI for the Hybrid RAG system.
"""

import streamlit as st

from configs.logging import get_logger
from configs.settings import settings
from src.citations.formatter import CitationFormatter
from src.rag.pipeline import HybridRAGPipeline
from src.utils.logger import QueryLogger
from src.utils.timer import PipelineTimer

logger = get_logger(__name__)


def init_session_state():
    """Initialize Streamlit session state."""
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = HybridRAGPipeline()

    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    if "timer" not in st.session_state:
        st.session_state.timer = PipelineTimer()


def format_result(result, show_timings=False):
    """Format and display query result."""
    # Display answer
    st.markdown("## Answer")
    st.markdown(result.answer)

    # Display sources
    if result.documents:
        st.markdown("## Sources")

        for i, doc in enumerate(result.documents, 1):
            with st.expander(
                f"📄 Source {i}: {doc.metadata.source} "
                f"(Score: {doc.score:.2%})"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Document Info**")
                    info = []
                    if doc.metadata.article:
                        info.append(
                            f"Article: {doc.metadata.article}"
                        )
                    if doc.metadata.page:
                        info.append(f"Page: {doc.metadata.page}")
                    if doc.metadata.chapter:
                        info.append(
                            f"Chapter: {doc.metadata.chapter}"
                        )
                    if doc.metadata.part:
                        info.append(f"Part: {doc.metadata.part}")

                    for item in info:
                        st.text(item)

                with col2:
                    st.write("**Citation**")
                    formatted = CitationFormatter.format_inline(doc)
                    st.code(formatted, language="text")

                st.markdown("**Content**")
                st.text(doc.text)


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Indian Constitution RAG",
        page_icon="📜",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    init_session_state()

    # Header
    st.markdown("# 📜 Indian Constitution RAG System")
    st.markdown(
        "Query the Indian Constitution using Hybrid Retrieval-Augmented Generation"
    )

    # Sidebar
    with st.sidebar:
        st.markdown("## Settings")

        citation_format = st.selectbox(
            "Citation Format",
            ["inline", "footnote", "hierarchical", "apa"],
        )

        show_timings = st.checkbox(
            "Show Performance Metrics",
            value=False,
        )

        show_context = st.checkbox(
            "Show Retrieved Context",
            value=False,
        )

        st.markdown("---")
        st.markdown("## Model Configuration")
        st.text(f"Embedding: {settings.EMBEDDING_MODEL}")
        st.text(f"Reranker: {settings.RERANKER_MODEL}")
        st.text(f"LLM: {settings.LLM_MODEL}")

    # Main content
    col1, col2 = st.columns([3, 1])

    with col1:
        question = st.text_area(
            "Ask a question about the Indian Constitution",
            placeholder="E.g., What are the fundamental rights guaranteed by the Constitution?",
            height=100,
        )

    with col2:
        search_button = st.button(
            "Search",
            use_container_width=True,
            type="primary",
        )

    if search_button and question:
        # Log query
        query_logger = QueryLogger(question)
        query_logger.log_start()

        # Create progress container
        progress_container = st.container()

        with progress_container:
            progress_bar = st.progress(0)

            # Execute query
            try:
                with st.spinner("🔍 Searching documents..."):
                    progress_bar.progress(25)

                    result = st.session_state.pipeline.query(question)

                    progress_bar.progress(75)

                # Add to history
                st.session_state.query_history.append(
                    {
                        "question": question,
                        "answer": result.answer,
                        "documents": result.documents,
                    }
                )

                progress_bar.progress(100)

                # Display results
                st.markdown("---")
                format_result(
                    result,
                    show_timings=show_timings,
                )

                # Show context if requested
                if show_context:
                    with st.expander("📋 Retrieved Context"):
                        for i, doc in enumerate(
                            result.documents, 1
                        ):
                            st.markdown(
                                f"### Document {i}"
                            )
                            st.text(doc.text)

                query_logger.log_complete(0)

            except Exception as e:
                st.error(f"Error: {str(e)}")
                query_logger.log_error("query_execution", e)
                logger.error(f"Query error: {e}")

    # Query history
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("## Query History")

        for i, item in enumerate(
            reversed(st.session_state.query_history)
        ):
            with st.expander(
                f"Previous Query {i + 1}: {item['question'][:50]}..."
            ):
                st.markdown("**Question:**")
                st.text(item["question"])
                st.markdown("**Answer:**")
                st.markdown(item["answer"])

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    Hybrid RAG System | Powered by ChromaDB, Ollama, and Sentence-Transformers
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
