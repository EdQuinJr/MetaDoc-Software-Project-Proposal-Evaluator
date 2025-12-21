"""
Module 4: NLP-Based Readability, Content Trends, and AI-Assisted Insights

Implements SRS requirements:
- M4.UC01: Local NLP Analysis (spaCy/NLTK/textstat)
- M4.UC02: External AI Summary (Google Gemini)
- M4.UC03: Consolidate NLP & AI Outputs

Handles:
1. Local NLP analysis using spaCy, NLTK, and textstat
2. Tokenization, stopword removal, and frequency analysis
3. Readability scoring (Flesch-Kincaid)
4. Named Entity Recognition (NER) for people, dates, organizations
5. Optional Gemini-generated summaries for qualitative insights
6. Consolidation of all NLP results into a unified report
"""

import os
import re
import json
from datetime import datetime
from collections import Counter
from flask import Blueprint, request, jsonify, current_app

# NLP Libraries
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import textstat

# AI Integration
import google.generativeai as genai

from app.core.extensions import db
from app.models import Submission, AnalysisResult
from app.services.audit_service import AuditService

nlp_bp = Blueprint('nlp', __name__)

class NLPAnalysisService:
    """Service for NLP-based content analysis and insights"""
    
    def __init__(self):
        self.spacy_model = None
        self.nltk_initialized = False
        self.gemini_initialized = False
        # Note: Lazy initialization - libraries will be initialized on first use
    
    def _initialize_nltk(self):
        """Initialize NLTK with required data (lazy)"""
        if self.nltk_initialized:
            return
        
        try:
            # Download required NLTK data
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
        try:
            # Try to load English model
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
        """
        Perform comprehensive local NLP analysis
        
        SRS Reference: M4.UC01 - Local NLP Analysis
        """
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
            
            # 1. Readability Analysis using textstat
            results['readability'] = self._analyze_readability(text)
            
            # 2. Token Analysis using NLTK
            results['token_analysis'] = self._analyze_tokens(text)
            
            # 3. Named Entity Recognition using spaCy
            results['named_entities'] = self._extract_named_entities(text)
            
            # 4. Sentiment Analysis (basic)
            results['sentiment'] = self._analyze_sentiment(text)
            
            # 5. Text Statistics
            results['text_statistics'] = self._compute_text_statistics(text)
            
            # 6. Language Detection
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
        try:
            readability_scores = {
                'flesch_kincaid_grade': textstat.flesch_kincaid().flesch_kincaid_grade(text),
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'gunning_fog_index': textstat.gunning_fog(text),
                'automated_readability_index': textstat.automated_readability_index(text),
                'coleman_liau_index': textstat.coleman_liau_index(text),
                'dale_chall_readability': textstat.dale_chall_readability_score(text)
            }
            
            # Determine reading level
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
            
            return {
                'scores': readability_scores,
                'reading_level': reading_level,
                'grade_equivalent': round(fk_grade, 1),
                'interpretation': self._interpret_readability_score(readability_scores['flesch_reading_ease'])
            }
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Readability analysis error: {e}")
            return {'error': f'Readability analysis failed: {e}'}
    
    def _analyze_tokens(self, text):
        """Analyze tokens, frequency, and linguistic features"""
        if not self.nltk_initialized:
            self._initialize_nltk()
        
        try:
            # Tokenization
            sentences = sent_tokenize(text)
            words = word_tokenize(text.lower())
            
            # Remove stopwords and punctuation
            stop_words = set(stopwords.words('english'))
            filtered_words = [
                word for word in words 
                if word.isalpha() and word not in stop_words and len(word) > 2
            ]
            
            # Frequency analysis
            word_freq = Counter(filtered_words)
            top_words = word_freq.most_common(10)
            
            # Vocabulary diversity (Type-Token Ratio)
            vocabulary_diversity = len(set(filtered_words)) / len(filtered_words) if filtered_words else 0
            
            return {
                'total_words': len(words),
                'unique_words': len(set(words)),
                'filtered_words': len(filtered_words),
                'vocabulary_diversity': round(vocabulary_diversity, 3),
                'top_terms': [{'term': word, 'frequency': freq} for word, freq in top_words],
                'sentences_count': len(sentences),
                'average_sentence_length': len(words) / len(sentences) if sentences else 0
            }
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Token analysis error: {e}")
            return {'error': f'Token analysis failed: {e}'}
    
    def _extract_named_entities(self, text):
        """Extract named entities using spaCy"""
        if not self.spacy_model:
            self._initialize_spacy()
        
        try:
            # Limit text length for processing
            if len(text) > 100000:  # 100k characters limit
                text = text[:100000]
            
            doc = self.spacy_model(text)
            
            # Extract entities by type
            entities_by_type = {}
            entity_counts = Counter()
            
            for ent in doc.ents:
                label = ent.label_
                if label not in entities_by_type:
                    entities_by_type[label] = []
                
                entities_by_type[label].append({
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': round(float(ent._.get('confidence', 0.5)), 2) if hasattr(ent._, 'confidence') else 0.5
                })
                
                entity_counts[label] += 1
            
            # Focus on key entity types as per SRS
            key_entities = {
                'PERSON': entities_by_type.get('PERSON', []),
                'DATE': entities_by_type.get('DATE', []),
                'ORG': entities_by_type.get('ORG', []),
                'GPE': entities_by_type.get('GPE', []),  # Geopolitical entities
                'MONEY': entities_by_type.get('MONEY', []),
                'TIME': entities_by_type.get('TIME', [])
            }
            
            return {
                'entities_by_type': key_entities,
                'entity_counts': dict(entity_counts),
                'total_entities': sum(entity_counts.values()),
                'entity_density': sum(entity_counts.values()) / len(doc) if len(doc) > 0 else 0
            }
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"NER analysis error: {e}")
            return {'error': f'Named entity recognition failed: {e}'}
    
    def _analyze_sentiment(self, text):
        """Basic sentiment analysis using NLTK VADER"""
        if not self.nltk_initialized:
            self._initialize_nltk()
        
        try:
            from nltk.sentiment import SentimentIntensityAnalyzer
            
            sia = SentimentIntensityAnalyzer()
            scores = sia.polarity_scores(text)
            
            # Determine overall sentiment
            compound_score = scores['compound']
            if compound_score >= 0.05:
                overall_sentiment = 'positive'
            elif compound_score <= -0.05:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
            
            return {
                'scores': scores,
                'overall_sentiment': overall_sentiment,
                'confidence': abs(compound_score)
            }
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Sentiment analysis error: {e}")
            return {'error': f'Sentiment analysis failed: {e}'}
    
    def _compute_text_statistics(self, text):
        """Compute additional text statistics"""
        try:
            # Sentence and paragraph analysis
            sentences = sent_tokenize(text)
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            # Complexity metrics
            avg_sentence_length = sum(len(sent.split()) for sent in sentences) / len(sentences) if sentences else 0
            avg_word_length = sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
            
            return {
                'total_characters': len(text),
                'total_sentences': len(sentences),
                'total_paragraphs': len(paragraphs),
                'average_sentence_length_words': round(avg_sentence_length, 2),
                'average_word_length_characters': round(avg_word_length, 2),
                'lexical_diversity': len(set(text.split())) / len(text.split()) if text.split() else 0
            }
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Text statistics error: {e}")
            return {'error': f'Text statistics computation failed: {e}'}
    
    def _detect_language(self, text):
        """Simple language detection"""
        try:
            # Basic English detection
            english_indicators = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
            text_lower = text.lower()
            english_score = sum(1 for word in english_indicators if word in text_lower)
            
            is_likely_english = english_score >= 3
            
            return {
                'likely_english': is_likely_english,
                'english_indicator_score': english_score,
                'confidence': 'high' if english_score >= 5 else 'medium' if english_score >= 3 else 'low'
            }
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Language detection error: {e}")
            return {'error': f'Language detection failed: {e}'}
    
    def _interpret_readability_score(self, flesch_score):
        """Interpret Flesch Reading Ease score"""
        if flesch_score >= 90:
            return "Very Easy (5th grade)"
        elif flesch_score >= 80:
            return "Easy (6th grade)"
        elif flesch_score >= 70:
            return "Fairly Easy (7th grade)"
        elif flesch_score >= 60:
            return "Standard (8th-9th grade)"
        elif flesch_score >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif flesch_score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (Graduate level)"
    
    def generate_ai_summary(self, text, submission_context=None):
        """
        Generate AI-powered summary using Gemini
        
        SRS Reference: M4.UC02 - External AI Summary
        """
        if not self.gemini_initialized:
            self._initialize_gemini()
        
        try:
            # Anonymize text for privacy compliance
            anonymized_text = self._anonymize_text_for_ai(text)
            
            # Prepare prompt
            prompt = self._create_analysis_prompt(anonymized_text, submission_context)
            
            # Generate content using Gemini
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            if response.text:
                # Parse structured response
                summary_data = self._parse_ai_response(response.text)
                return summary_data, None
            else:
                return None, "Empty response from AI"
                
        except Exception as e:
            if current_app:
                current_app.logger.error(f"AI summary generation failed: {e}")
            return None, f"AI summary error: {e}"
    
    def _anonymize_text_for_ai(self, text):
        """Anonymize text for privacy compliance before AI processing"""
        try:
            # Replace potential personal identifiers
            anonymized = text
            
            # Replace email patterns
            anonymized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', anonymized)
            
            # Replace phone patterns
            anonymized = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', anonymized)
            
            # Replace potential names (capitalized words followed by capitalized words)
            anonymized = re.sub(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]', anonymized)
            
            # Limit text length for API efficiency
            if len(anonymized) > 8000:
                anonymized = anonymized[:8000] + "\n[TEXT TRUNCATED]"
            
            return anonymized
            
        except Exception as e:
            if current_app:
                current_app.logger.warning(f"Text anonymization failed: {e}")
            return text[:8000]  # Fallback to truncation only
    
    def _create_analysis_prompt(self, text, context):
        """Create structured prompt for AI analysis"""
        prompt = f"""
        Please analyze the following academic document and provide a structured summary:

        Document Type: Academic Paper/Assignment
        Context: {context.get('assignment_type', 'Unknown') if context else 'Academic Document'}

        Text to analyze:
        {text}

        Please provide analysis in the following JSON format:
        {{
            "summary": "Brief 2-3 sentence summary of the document",
            "key_topics": ["topic1", "topic2", "topic3"],
            "writing_quality": "assessment of writing quality (poor/fair/good/excellent)",
            "content_depth": "assessment of content depth (shallow/moderate/comprehensive)",
            "academic_level": "estimated academic level (high school/undergraduate/graduate)",
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["improvement1", "improvement2"],
            "estimated_completion_effort": "low/medium/high"
        }}

        Focus on academic writing quality, content organization, and depth of analysis.
        """
        
        return prompt
    
    def _parse_ai_response(self, response_text):
        """Parse structured AI response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Fallback to plain text summary
                return {
                    'summary': response_text[:500],
                    'key_topics': [],
                    'writing_quality': 'unknown',
                    'content_depth': 'unknown',
                    'academic_level': 'unknown',
                    'strengths': [],
                    'areas_for_improvement': [],
                    'estimated_completion_effort': 'unknown'
                }
        except Exception as e:
            if current_app:
                current_app.logger.error(f"AI response parsing failed: {e}")
            return {
                'summary': 'AI analysis failed to parse',
                'error': str(e)
            }
    
    def consolidate_nlp_results(self, local_results, ai_summary=None):
        """
        Consolidate all NLP analysis results
        
        SRS Reference: M4.UC03 - Consolidate NLP & AI Outputs
        """
        try:
            consolidated = {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'local_nlp': local_results,
                'ai_insights': ai_summary,
                'summary_metrics': {},
                'recommendations': []
            }
            
            # Extract key metrics for dashboard display
            if 'readability' in local_results and 'scores' in local_results['readability']:
                consolidated['summary_metrics']['flesch_kincaid_grade'] = local_results['readability']['scores'].get('flesch_kincaid_grade')
                consolidated['summary_metrics']['reading_level'] = local_results['readability'].get('reading_level')
            
            if 'token_analysis' in local_results:
                consolidated['summary_metrics']['vocabulary_diversity'] = local_results['token_analysis'].get('vocabulary_diversity')
                consolidated['summary_metrics']['unique_words'] = local_results['token_analysis'].get('unique_words')
            
            if 'named_entities' in local_results:
                consolidated['summary_metrics']['total_entities'] = local_results['named_entities'].get('total_entities', 0)
            
            # Generate recommendations based on analysis
            consolidated['recommendations'] = self._generate_recommendations(local_results, ai_summary)
            
            return consolidated, None
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"NLP consolidation failed: {e}")
            return None, f"Consolidation error: {e}"
    
    def _generate_recommendations(self, local_results, ai_summary):
        """Generate recommendations based on NLP analysis"""
        recommendations = []
        
        try:
            # Readability recommendations
            if 'readability' in local_results and 'scores' in local_results['readability']:
                fk_grade = local_results['readability']['scores'].get('flesch_kincaid_grade', 0)
                if fk_grade > 16:
                    recommendations.append({
                        'category': 'readability',
                        'message': 'Consider simplifying sentence structure for better readability',
                        'priority': 'medium'
                    })
                elif fk_grade < 8:
                    recommendations.append({
                        'category': 'readability',
                        'message': 'Consider using more sophisticated vocabulary and sentence structures',
                        'priority': 'low'
                    })
            
            # Vocabulary diversity recommendations
            if 'token_analysis' in local_results:
                diversity = local_results['token_analysis'].get('vocabulary_diversity', 0)
                if diversity < 0.3:
                    recommendations.append({
                        'category': 'vocabulary',
                        'message': 'Consider using more varied vocabulary to improve writing quality',
                        'priority': 'medium'
                    })
            
            # AI-based recommendations
            if ai_summary and 'areas_for_improvement' in ai_summary:
                for improvement in ai_summary['areas_for_improvement']:
                    recommendations.append({
                        'category': 'ai_suggestion',
                        'message': improvement,
                        'priority': 'high'
                    })
            
            return recommendations
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Recommendation generation failed: {e}")
            return []

# Initialize service lazily
nlp_service = None

def get_nlp_service():
    """Get or create the NLP service instance"""
    global nlp_service
    if nlp_service is None:
        nlp_service = NLPAnalysisService()
    return nlp_service

@nlp_bp.route('/analyze/<submission_id>', methods=['POST'])
def analyze_nlp(submission_id):
    """
    Perform comprehensive NLP analysis on a submission
    
    Combines M4.UC01, M4.UC02, and M4.UC03
    """
    try:
        # Get submission and analysis result
        submission = Submission.query.filter_by(id=submission_id).first()
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
        
        if not submission.analysis_result or not submission.analysis_result.document_text:
            return jsonify({'error': 'Document text not available. Complete metadata extraction first.'}), 400
        
        text = submission.analysis_result.document_text
        
        # Perform local NLP analysis
        local_results = get_nlp_service().perform_local_nlp_analysis(text)
        
        # Optional AI analysis
        ai_summary = None
        enable_ai = request.json.get('enable_ai_summary', False) if request.json else False
        
        if enable_ai and get_nlp_service().gemini_initialized:
            context = {
                'assignment_type': getattr(submission.deadline, 'assignment_type', None) if submission.deadline else None,
                'course_code': getattr(submission.deadline, 'course_code', None) if submission.deadline else None
            }
            
            ai_summary, ai_error = get_nlp_service().generate_ai_summary(text, context)
            if ai_error:
                current_app.logger.warning(f"AI summary failed: {ai_error}")
        
        # Consolidate results
        consolidated_results, consolidation_error = get_nlp_service().consolidate_nlp_results(local_results, ai_summary)
        
        if consolidation_error:
            return jsonify({'error': consolidation_error}), 500
        
        # Update analysis result
        analysis_result = submission.analysis_result
        analysis_result.nlp_results = consolidated_results
        
        # Extract key fields for database
        if 'readability' in local_results and 'scores' in local_results['readability']:
            analysis_result.flesch_kincaid_score = local_results['readability']['scores'].get('flesch_kincaid_grade')
            analysis_result.readability_grade = local_results['readability'].get('reading_level')
        
        if 'named_entities' in local_results:
            analysis_result.named_entities = local_results['named_entities']
        
        if 'token_analysis' in local_results and 'top_terms' in local_results['token_analysis']:
            analysis_result.top_terms = local_results['token_analysis']['top_terms']
        
        if ai_summary:
            analysis_result.ai_summary = ai_summary.get('summary')
            analysis_result.ai_insights = ai_summary
        
        db.session.commit()
        
        # Log NLP analysis completion
        AuditService.log_submission_event(
            'nlp_analysis_completed',
            submission,
            additional_metadata={
                'flesch_kincaid_grade': analysis_result.flesch_kincaid_score,
                'ai_summary_generated': ai_summary is not None,
                'recommendation_count': len(consolidated_results.get('recommendations', []))
            }
        )
        
        return jsonify({
            'message': 'NLP analysis completed successfully',
            'submission_id': submission_id,
            'analysis_results': consolidated_results,
            'ai_summary_included': ai_summary is not None
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"NLP analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@nlp_bp.route('/readability/<submission_id>', methods=['GET'])
def get_readability_analysis(submission_id):
    """Get only readability analysis for a submission"""
    try:
        submission = Submission.query.filter_by(id=submission_id).first()
        
        if not submission or not submission.analysis_result:
            return jsonify({'error': 'Submission or analysis not found'}), 404
        
        text = submission.analysis_result.document_text
        if not text:
            return jsonify({'error': 'Document text not available'}), 400
        
        readability_results = get_nlp_service()._analyze_readability(text)
        
        return jsonify({
            'submission_id': submission_id,
            'readability_analysis': readability_results
        })
        
    except Exception as e:
        current_app.logger.error(f"Readability analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@nlp_bp.route('/entities/<submission_id>', methods=['GET'])
def get_named_entities(submission_id):
    """Get named entity analysis for a submission"""
    try:
        submission = Submission.query.filter_by(id=submission_id).first()
        
        if not submission or not submission.analysis_result:
            return jsonify({'error': 'Submission or analysis not found'}), 404
        
        text = submission.analysis_result.document_text
        if not text:
            return jsonify({'error': 'Document text not available'}), 400
        
        entity_results = get_nlp_service()._extract_named_entities(text)
        
        return jsonify({
            'submission_id': submission_id,
            'named_entity_analysis': entity_results
        })
        
    except Exception as e:
        current_app.logger.error(f"Named entity analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

