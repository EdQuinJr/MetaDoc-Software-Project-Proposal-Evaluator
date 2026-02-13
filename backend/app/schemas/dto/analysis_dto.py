"""
Analysis-related Data Transfer Objects
"""

from typing import Optional, Dict, Any, List


class MetadataDTO:
    """DTO for document metadata serialization"""
    
    @staticmethod
    def serialize(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize document metadata"""
        if not metadata:
            return {}
        
        return {
            'author': metadata.get('author'),
            # Map service keys (creation_date) to DTO keys or standard ones
            'created_date': metadata.get('creation_date') or metadata.get('created_date'),
            'modified_date': metadata.get('last_modified_date') or metadata.get('modified_date'),
            'last_editor': metadata.get('last_editor') or metadata.get('last_modified_by'),
            'revision_count': metadata.get('revision_count') or metadata.get('revision'),
            'editing_time_minutes': metadata.get('editing_time_minutes') or metadata.get('total_editing_time'),
            'application': metadata.get('application'),
            'contributors': metadata.get('contributors', []),
            
            # Keep legacy keys for backward compatibility if needed
            'title': metadata.get('title'),
            'subject': metadata.get('subject'),
            'keywords': metadata.get('keywords')
        }


class ContentStatisticsDTO:
    """DTO for content statistics serialization"""
    
    @staticmethod
    def serialize(statistics: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize content statistics"""
        if not statistics:
            return {}
        
        return {
            'word_count': statistics.get('word_count', 0),
            'character_count': statistics.get('character_count', 0),
            'paragraph_count': statistics.get('paragraph_count', 0),
            'sentence_count': statistics.get('sentence_count', 0),
            'page_count': statistics.get('page_count', 0),
            'average_words_per_sentence': statistics.get('average_words_per_sentence', 0),
            'average_sentence_length': statistics.get('average_sentence_length', 0)
        }


class HeuristicInsightsDTO:
    """DTO for heuristic insights serialization"""
    
    @staticmethod
    def serialize(insights: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize heuristic insights"""
        if not insights:
            return {}
        
        return {
            'timeliness_score': insights.get('timeliness_score'),
            'timeliness_classification': insights.get('timeliness_classification'),
            'submission_pattern': insights.get('submission_pattern'),
            'contribution_growth': insights.get('contribution_growth'),
            'revision_count': insights.get('revision_count'),
            'last_minute_submission': insights.get('last_minute_submission'),
            'early_submission': insights.get('early_submission'),
            'recommendations': insights.get('recommendations', [])
        }


class NLPResultDTO:
    """DTO for NLP analysis results serialization"""
    
    @staticmethod
    def serialize(nlp_results: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize NLP analysis results"""
        if not nlp_results:
            return {}
        
        return {
            'flesch_reading_ease': nlp_results.get('flesch_reading_ease'),
            'flesch_kincaid_grade': nlp_results.get('flesch_kincaid_grade'),
            'gunning_fog': nlp_results.get('gunning_fog'),
            'smog_index': nlp_results.get('smog_index'),
            'automated_readability_index': nlp_results.get('automated_readability_index'),
            'coleman_liau_index': nlp_results.get('coleman_liau_index'),
            'readability_grade': nlp_results.get('readability_grade'),
            'named_entities': nlp_results.get('named_entities', []),
            'top_terms': nlp_results.get('top_terms', []),
            'sentiment_score': nlp_results.get('sentiment_score'),
            'language': nlp_results.get('language')
        }


class AnalysisResultDTO:
    """DTO for complete analysis result serialization"""
    
    @staticmethod
    def serialize(analysis, include_full_text: bool = False) -> Dict[str, Any]:
        """Serialize AnalysisResult model"""
        if not analysis:
            return None
        
        data = {
            'id': analysis.id,
            'submission_id': analysis.submission_id,
            'document_metadata': MetadataDTO.serialize(analysis.document_metadata) if analysis.document_metadata else {},
            'content_statistics': ContentStatisticsDTO.serialize(analysis.content_statistics) if analysis.content_statistics else {},
            'heuristic_insights': HeuristicInsightsDTO.serialize(analysis.heuristic_insights) if analysis.heuristic_insights else {},
            'timeliness_classification': analysis.timeliness_classification.value if hasattr(analysis, 'timeliness_classification') and analysis.timeliness_classification else None,
            'contribution_growth_percentage': analysis.contribution_growth_percentage,
            'nlp_results': NLPResultDTO.serialize(analysis.nlp_results) if analysis.nlp_results else {},
            'flesch_kincaid_score': analysis.flesch_kincaid_score,
            'readability_grade': analysis.readability_grade,
            'named_entities': analysis.named_entities,
            'top_terms': analysis.top_terms,
            'ai_summary': analysis.ai_summary,
            'ai_insights': analysis.ai_insights,
            'is_complete_document': analysis.is_complete_document,
            'validation_warnings': analysis.validation_warnings,
            'analysis_version': analysis.analysis_version,
            'processing_duration_seconds': analysis.processing_duration_seconds,
            'created_at': analysis.created_at.isoformat() if hasattr(analysis, 'created_at') else None
        }
        
        if include_full_text and hasattr(analysis, 'document_text'):
            data['document_text'] = analysis.document_text
        
        return data
    
    @staticmethod
    def serialize_summary(analysis) -> Dict[str, Any]:
        """Serialize analysis result summary (minimal data)"""
        if not analysis:
            return None
        
        return {
            'id': analysis.id,
            'submission_id': analysis.submission_id,
            'word_count': analysis.content_statistics.get('word_count') if analysis.content_statistics else None,
            'flesch_kincaid_score': analysis.flesch_kincaid_score,
            'readability_grade': analysis.readability_grade,
            'timeliness_classification': analysis.timeliness_classification.value if hasattr(analysis, 'timeliness_classification') and analysis.timeliness_classification else None,
            'is_complete_document': analysis.is_complete_document,
            'created_at': analysis.created_at.isoformat() if hasattr(analysis, 'created_at') else None
        }
