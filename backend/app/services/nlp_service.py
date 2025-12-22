"""
NLP Analysis Service - Handles natural language processing and readability analysis

Extracted from api/nlp.py to follow proper service layer architecture.
"""

try:
    import spacy
except ImportError:
    spacy = None

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
except ImportError:
    nltk = None

try:
    import textstat
except ImportError:
    textstat = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from flask import current_app
from collections import Counter
import re


class NLPService:
    """Service for NLP-based content analysis and insights"""
    
    def __init__(self):
        self.spacy_model = None
        self.nltk_initialized = False
        self.gemini_initialized = False
    
    def _initialize_nltk(self):
        """Initialize NLTK with required data (lazy)"""
        if self.nltk_initialized:
            return
        
        if not nltk:
            if current_app:
                current_app.logger.warning("NLTK not installed. Install with: pip install nltk")
            return
        
        try:
            required_nltk_data = [
                'punkt',
                'stopwords',
                'averaged_perceptron_tagger',
                'vader_lexicon'
            ]
            
            for item in required_nltk_data:
                try:
                    nltk.data.find(f'tokenizers/{item}')
                except LookupError:
                    nltk.download(item, quiet=True)
            
            self.nltk_initialized = True
            if current_app:
                current_app.logger.info("NLTK initialized successfully")
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"NLTK initialization failed: {e}")
            self.nltk_initialized = False
    
    def _initialize_spacy(self):
        """Initialize spaCy model"""
        if not spacy:
            if current_app:
                current_app.logger.warning("spaCy not installed. Install with: pip install spacy")
            return
            
        try:
            model_names = ['en_core_web_sm', 'en_core_web_md', 'en_core_web_lg']
            
            for model_name in model_names:
                try:
                    self.spacy_model = spacy.load(model_name)
                    if current_app:
                        current_app.logger.info(f"Loaded spaCy model: {model_name}")
                    break
                except OSError:
                    continue
            
            if not self.spacy_model:
                if current_app:
                    current_app.logger.warning("No spaCy English model found. Install with: python -m spacy download en_core_web_sm")
                
        except Exception as e:
            if current_app:
                current_app.logger.error(f"spaCy initialization failed: {e}")
    
    def _initialize_gemini(self):
        """Initialize Google Gemini AI (optional)"""
        if not genai:
            if current_app:
                current_app.logger.warning("Google Generative AI not installed. Install with: pip install google-generativeai")
            return
            
        try:
            api_key = current_app.config.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_initialized = True
                if current_app:
                    current_app.logger.info("Gemini AI initialized successfully")
            else:
                if current_app:
                    current_app.logger.info("Gemini API key not provided - AI features disabled")
                
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Gemini initialization failed: {e}")
            self.gemini_initialized = False
    
    def perform_local_nlp_analysis(self, text):
        """Perform comprehensive local NLP analysis"""
        if not text or len(text.strip()) < 10:
            return {
                'error': 'Insufficient text for NLP analysis',
                'readability': None,
                'token_analysis': None,
                'named_entities': None,
                'sentiment': None
            }
        
        try:
            results = {}
            
            results['readability'] = self._analyze_readability(text)
            results['token_analysis'] = self._analyze_tokens(text)
            results['named_entities'] = self._extract_named_entities(text)
            results['sentiment'] = self._analyze_sentiment(text)
            results['text_statistics'] = self._compute_text_statistics(text)
            results['language_info'] = self._detect_language(text)
            
            return results
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Local NLP analysis failed: {e}")
            return {
                'error': f'NLP analysis error: {e}',
                'readability': None,
                'token_analysis': None,
                'named_entities': None,
                'sentiment': None
            }
    
    def _analyze_readability(self, text):
        """Analyze text readability using multiple metrics"""
        if not textstat:
            return None
            
        try:
            readability_scores = {
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'gunning_fog_index': textstat.gunning_fog(text),
                'automated_readability_index': textstat.automated_readability_index(text),
                'coleman_liau_index': textstat.coleman_liau_index(text),
                'dale_chall_readability': textstat.dale_chall_readability_score(text)
            }
            
            fk_grade = readability_scores['flesch_kincaid_grade']
            if fk_grade <= 6:
                reading_level = 'Elementary'
            elif fk_grade <= 9:
                reading_level = 'Middle School'
            elif fk_grade <= 12:
                reading_level = 'High School'
            elif fk_grade <= 16:
                reading_level = 'College'
            else:
                reading_level = 'Graduate'
            
            readability_scores['reading_level'] = reading_level
            readability_scores['grade_level'] = round(fk_grade, 1)
            
            return readability_scores
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Readability analysis failed: {e}")
            return None
    
    def _analyze_tokens(self, text):
        """Analyze tokens using NLTK"""
        try:
            self._initialize_nltk()
            
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            filtered_tokens = [w for w in tokens if w.isalnum() and w not in stop_words]
            
            word_freq = Counter(filtered_tokens)
            top_terms = word_freq.most_common(20)
            
            return {
                'total_tokens': len(tokens),
                'unique_tokens': len(set(tokens)),
                'filtered_tokens': len(filtered_tokens),
                'top_terms': [{'term': term, 'frequency': freq} for term, freq in top_terms],
                'vocabulary_richness': len(set(tokens)) / len(tokens) if tokens else 0
            }
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Token analysis failed: {e}")
            return None
    
    def _extract_named_entities(self, text):
        """Extract named entities using spaCy"""
        try:
            if not self.spacy_model:
                self._initialize_spacy()
            
            if not self.spacy_model:
                return None
            
            doc = self.spacy_model(text[:100000])  # Limit text length for performance
            
            entities = {}
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
            
            entity_summary = {
                label: list(set(ents))[:10]  # Unique entities, max 10 per type
                for label, ents in entities.items()
            }
            
            return {
                'entities_by_type': entity_summary,
                'total_entities': len(doc.ents),
                'entity_types': list(entities.keys())
            }
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Named entity extraction failed: {e}")
            return None
    
    def _analyze_sentiment(self, text):
        """Basic sentiment analysis"""
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            
            self._initialize_nltk()
            sia = SentimentIntensityAnalyzer()
            scores = sia.polarity_scores(text)
            
            return {
                'compound': scores['compound'],
                'positive': scores['pos'],
                'neutral': scores['neu'],
                'negative': scores['neg'],
                'overall': 'positive' if scores['compound'] > 0.05 else 'negative' if scores['compound'] < -0.05 else 'neutral'
            }
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Sentiment analysis failed: {e}")
            return None
    
    def _compute_text_statistics(self, text):
        """Compute additional text statistics"""
        try:
            return {
                'syllable_count': textstat.syllable_count(text),
                'lexicon_count': textstat.lexicon_count(text),
                'sentence_count': textstat.sentence_count(text),
                'avg_syllables_per_word': textstat.avg_syllables_per_word(text),
                'difficult_words': textstat.difficult_words(text)
            }
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Text statistics failed: {e}")
            return None
    
    def _detect_language(self, text):
        """Detect language (basic)"""
        return {
            'detected_language': 'en',
            'confidence': 0.95,
            'note': 'Basic English detection'
        }
    
    def generate_ai_summary(self, text, submission_context=None):
        """Generate AI-powered summary using Gemini"""
        if not self.gemini_initialized:
            self._initialize_gemini()
        
        if not self.gemini_initialized:
            return None, "Gemini AI not configured"
        
        try:
            prompt = f"Provide a concise summary of the following academic document:\n\n{text[:5000]}"
            
            if submission_context:
                prompt = f"Assignment: {submission_context.get('assignment_type', 'Unknown')}\n\n" + prompt
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            if response.text:
                return response.text, None
            else:
                return None, "No response from Gemini"
                
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Gemini AI summary failed: {e}")
            return None, str(e)
