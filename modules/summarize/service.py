import logging

logger = logging.getLogger(__name__)


def summarize_text(text: str, language: str = "french", sentences_count: int = 5) -> dict:
    """
    Résume un texte avec l'algorithme LSA (Latent Semantic Analysis) via sumy.

    Installation: pip install sumy nltk
    NLTK punkt: téléchargé automatiquement au premier appel.

    Args:
        text: Texte à résumer
        language: Langue du texte (french, english, spanish, german, italian, portuguese)
        sentences_count: Nombre de phrases dans le résumé

    Returns:
        dict { summary: str, sentences_count: int }
    """
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        from sumy.nlp.stemmers import Stemmer
        from sumy.utils import get_stop_words
    except ImportError:
        raise RuntimeError("Installez sumy: pip install sumy nltk")

    # Téléchargement silencieux des données NLTK nécessaires
    try:
        import nltk
        nltk.download("punkt", quiet=True)
        nltk.download("punkt_tab", quiet=True)
    except Exception:
        pass

    logger.info(f"📝 Résumé: {len(text)} caractères, langue={language}, phrases={sentences_count}")

    parser = PlaintextParser.from_string(text, Tokenizer(language))
    stemmer = Stemmer(language)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)

    sentences = summarizer(parser.document, sentences_count)
    summary = " ".join(str(s) for s in sentences)

    logger.info(f"✅ Résumé: {len(summary)} caractères ({len(sentences)} phrases)")

    return {
        "summary": summary,
        "sentences_count": len(sentences),
    }
