"""
ML module for analyzing user prompt history and generating characteristics
"""
import json
from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from collections import Counter
import numpy as np
import logging

logger = logging.getLogger(__name__)


class PromptAnalyzer:
    """Analyzes user prompts to extract characteristics and preferences"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.topic_model = None
        
        # Keywords for different categories
        self.travel_keywords = {
            'luxury': ['luxury', 'premium', 'exclusive', 'upscale', 'high-end', 'vip'],
            'budget': ['cheap', 'budget', 'affordable', 'discount', 'save', 'economical'],
            'adventure': ['adventure', 'trekking', 'hiking', 'extreme', 'action', 'thrill'],
            'relaxation': ['relax', 'calm', 'peaceful', 'spa', 'beach', 'quiet'],
            'cultural': ['culture', 'history', 'museum', 'architecture', 'heritage', 'local'],
            'family': ['family', 'kids', 'children', 'parent', 'baby', 'school'],
            'business': ['business', 'meeting', 'conference', 'work', 'corporate', 'professional'],
            'food': ['food', 'cuisine', 'restaurant', 'dining', 'culinary', 'taste'],
        }
        
        self.sentiment_indicators = {
            'positive': ['love', 'amazing', 'excellent', 'perfect', 'great', 'wonderful', 'awesome'],
            'negative': ['hate', 'bad', 'terrible', 'awful', 'poor', 'disappointing', 'worst'],
            'neutral': ['good', 'ok', 'fine', 'alright', 'reasonable', 'acceptable'],
        }
    
    def analyze_prompts(self, prompts: List[str]) -> Dict[str, Any]:
        """
        Analyze a list of user prompts and extract characteristics
        
        Args:
            prompts: List of prompt texts from user
            
        Returns:
            Dictionary containing analysis results
        """
        if not prompts:
            return self._empty_analysis()
        
        logger.info(f"Analyzing {len(prompts)} prompts for characteristics")
        
        analysis = {
            'travel_preferences': self._extract_travel_preferences(prompts),
            'budget_profile': self._extract_budget_profile(prompts),
            'booking_patterns': self._extract_booking_patterns(prompts),
            'interests': self._extract_interests(prompts),
            'personality_traits': self._extract_personality_traits(prompts),
            'pain_points': self._extract_pain_points(prompts),
            'motivation_drivers': self._extract_motivation_drivers(prompts),
            'decision_style': self._extract_decision_style(prompts),
            'tone_preference': self._extract_tone_preference(prompts),
            'communication_style': self._extract_communication_style(prompts),
            'avg_sentiment': self._calculate_avg_sentiment(prompts),
            'detailed_summary': self._generate_detailed_summary(prompts),
            'confidence_score': self._calculate_confidence(prompts),
        }
        
        return analysis
    
    def _extract_travel_preferences(self, prompts: List[str]) -> Dict[str, Any]:
        """Extract travel preferences from prompts"""
        text = ' '.join(prompts).lower()
        
        preferences = {
            'preferred_destinations': [],
            'travel_frequency': 'regular',
            'preferred_transportation': [],
            'accommodation_style': 'unknown',
            'trip_duration_preference': 'medium',
        }
        
        # Extract destinations
        destination_keywords = ['paris', 'london', 'dubai', 'tokyo', 'new york', 'bali', 'thailand', 'amsterdam', 'barcelona', 'rome', 'athens', 'india', 'nepal', 'bhutan', 'maldives', 'caribbean']
        for dest in destination_keywords:
            if dest in text:
                preferences['preferred_destinations'].append(dest)
        
        # Travel frequency
        if 'monthly' in text or 'every month' in text:
            preferences['travel_frequency'] = 'frequent'
        elif 'yearly' in text or 'annual' in text or 'once a year' in text:
            preferences['travel_frequency'] = 'occasional'
        elif 'weekend' in text:
            preferences['travel_frequency'] = 'very_frequent'
        
        # Transportation
        if 'flight' in text or 'air' in text or 'airline' in text:
            preferences['preferred_transportation'].append('flight')
        if 'train' in text or 'rail' in text:
            preferences['preferred_transportation'].append('train')
        if 'car' in text or 'road' in text or 'drive' in text:
            preferences['preferred_transportation'].append('car')
        
        # Accommodation
        if 'hotel' in text or 'luxury' in text or 'resort' in text:
            preferences['accommodation_style'] = 'hotel'
        elif 'hostel' in text or 'airbnb' in text or 'apartment' in text:
            preferences['accommodation_style'] = 'alternative'
        elif 'resort' in text or 'all-inclusive' in text:
            preferences['accommodation_style'] = 'resort'
        
        # Trip duration
        if 'week' in text or '7 days' in text:
            preferences['trip_duration_preference'] = 'medium'
        elif 'day' in text or '2-3' in text or '3-4' in text:
            preferences['trip_duration_preference'] = 'short'
        elif 'month' in text or '2 weeks' in text:
            preferences['trip_duration_preference'] = 'long'
        
        return preferences
    
    def _extract_budget_profile(self, prompts: List[str]) -> Dict[str, Any]:
        """Extract budget preferences from prompts"""
        text = ' '.join(prompts).lower()
        
        profile = {
            'budget_tier': 'medium',
            'price_sensitivity': 'moderate',
            'willing_to_splurge': False,
            'look_for_deals': False,
        }
        
        # Budget tier
        if any(word in text for word in ['luxury', 'premium', 'expensive', '5-star']):
            profile['budget_tier'] = 'luxury'
        elif any(word in text for word in ['cheap', 'budget', 'affordable', 'economical']):
            profile['budget_tier'] = 'budget'
        
        # Price sensitivity
        if 'price' in text or 'cost' in text or 'expensive' in text:
            profile['price_sensitivity'] = 'high'
        
        # Splurge willingness
        if 'splurge' in text or 'treat myself' in text or 'special occasion' in text:
            profile['willing_to_splurge'] = True
        
        # Deal seeking
        if 'deal' in text or 'discount' in text or 'save' in text or 'offer' in text:
            profile['look_for_deals'] = True
        
        return profile
    
    def _extract_booking_patterns(self, prompts: List[str]) -> Dict[str, Any]:
        """Extract booking patterns from prompts"""
        text = ' '.join(prompts).lower()
        
        patterns = {
            'advance_booking_tendency': 'moderate',
            'group_size': 'solo',
            'booking_flexibility': 'flexible',
            'preferred_booking_channel': 'online',
        }
        
        # Booking advance
        if 'last minute' in text or 'asap' in text or 'urgent' in text:
            patterns['advance_booking_tendency'] = 'last_minute'
        elif 'month ahead' in text or 'advance' in text or 'plan ahead' in text:
            patterns['advance_booking_tendency'] = 'advance'
        
        # Group size
        if 'family' in text or 'kids' in text or 'children' in text:
            patterns['group_size'] = 'family'
        elif 'couple' in text or 'partner' in text or 'friend' in text:
            patterns['group_size'] = 'group'
        
        # Flexibility
        if 'flexible' in text or 'flexible dates' in text:
            patterns['booking_flexibility'] = 'flexible'
        elif 'fixed' in text or 'specific dates' in text or 'must be' in text:
            patterns['booking_flexibility'] = 'inflexible'
        
        return patterns
    
    def _extract_interests(self, prompts: List[str]) -> List[str]:
        """Extract user interests from prompts"""
        text = ' '.join(prompts).lower()
        interests = []
        
        for category, keywords in self.travel_keywords.items():
            if any(keyword in text for keyword in keywords):
                interests.append(category)
        
        # Additional interests
        if 'beach' in text or 'ocean' in text or 'sea' in text:
            interests.append('beach')
        if 'mountain' in text or 'hiking' in text or 'trekking' in text:
            interests.append('mountain')
        if 'nightlife' in text or 'party' in text or 'club' in text:
            interests.append('nightlife')
        if 'shopping' in text or 'mall' in text or 'retail' in text:
            interests.append('shopping')
        
        return list(set(interests))
    
    def _extract_personality_traits(self, prompts: List[str]) -> List[str]:
        """Extract personality traits from prompts"""
        text = ' '.join(prompts).lower()
        traits = []
        
        if any(word in text for word in ['plan', 'organized', 'structured', 'schedule']):
            traits.append('organized')
        if any(word in text for word in ['spontaneous', 'flexible', 'go with flow', 'last minute']):
            traits.append('spontaneous')
        if any(word in text for word in ['adventure', 'explore', 'discover', 'new']):
            traits.append('adventurous')
        if any(word in text for word in ['comfort', 'familiar', 'same', 'known']):
            traits.append('comfort_seeking')
        if any(word in text for word in ['detail', 'specific', 'exact', 'precise']):
            traits.append('detail_oriented')
        if any(word in text for word in ['social', 'group', 'meet', 'interact', 'friend']):
            traits.append('social')
        if any(word in text for word in ['quiet', 'alone', 'solo', 'peace']):
            traits.append('introverted')
        
        return traits
    
    def _extract_pain_points(self, prompts: List[str]) -> List[str]:
        """Extract pain points from prompts"""
        text = ' '.join(prompts).lower()
        pain_points = []
        
        if 'expensive' in text or 'costly' in text:
            pain_points.append('high_costs')
        if 'complicated' in text or 'confusing' in text or 'hard to find' in text:
            pain_points.append('information_overload')
        if 'slow' in text or 'wait' in text or 'delay' in text:
            pain_points.append('time_constraints')
        if 'cancel' in text or 'refund' in text or 'risk' in text:
            pain_points.append('booking_risk')
        if 'quality' in text or 'bad experience' in text or 'disappointed' in text:
            pain_points.append('quality_assurance')
        if 'trust' in text or 'scam' in text or 'fraud' in text:
            pain_points.append('trust_issues')
        
        return pain_points
    
    def _extract_motivation_drivers(self, prompts: List[str]) -> List[str]:
        """Extract what motivates the user"""
        text = ' '.join(prompts).lower()
        drivers = []
        
        if any(word in text for word in ['save', 'deal', 'discount', 'cheap']):
            drivers.append('cost_savings')
        if any(word in text for word in ['quality', 'best', 'top', 'luxury', 'premium']):
            drivers.append('quality_excellence')
        if any(word in text for word in ['time', 'fast', 'quick', 'efficient']):
            drivers.append('convenience')
        if any(word in text for word in ['experience', 'memorable', 'unique', 'special']):
            drivers.append('memorable_experiences')
        if any(word in text for word in ['social', 'share', 'instagram', 'photo']):
            drivers.append('social_sharing')
        if any(word in text for word in ['learn', 'discover', 'explore', 'culture']):
            drivers.append('learning_exploration')
        
        return drivers
    
    def _extract_decision_style(self, prompts: List[str]) -> str:
        """Extract user decision-making style"""
        text = ' '.join(prompts).lower()
        
        if any(word in text for word in ['data', 'research', 'compare', 'reviews', 'ratings']):
            return 'analytical'
        elif any(word in text for word in ['feeling', 'gut', 'instinct', 'vibe']):
            return 'intuitive'
        elif any(word in text for word in ['recommend', 'trust', 'expert', 'advice']):
            return 'trust_based'
        else:
            return 'balanced'
    
    def _extract_tone_preference(self, prompts: List[str]) -> str:
        """Extract preferred communication tone"""
        text = ' '.join(prompts).lower()
        
        if any(word in text for word in ['professional', 'formal', 'business']):
            return 'professional'
        elif any(word in text for word in ['fun', 'casual', 'chill', 'relaxed']):
            return 'casual'
        else:
            return 'helpful'
    
    def _extract_communication_style(self, prompts: List[str]) -> str:
        """Extract communication style preference"""
        text = ' '.join(prompts).lower()
        
        if any(word in text for word in ['brief', 'short', 'quick', 'summary']):
            return 'concise'
        elif any(word in text for word in ['detail', 'explain', 'comprehensive', 'thorough']):
            return 'detailed'
        else:
            return 'balanced'
    
    def _calculate_avg_sentiment(self, prompts: List[str]) -> float:
        """Calculate average sentiment across prompts"""
        sentiments = []
        
        for prompt in prompts:
            prompt_lower = prompt.lower()
            sentiment_score = 0.0
            
            # Positive indicators
            positive_count = sum(1 for word in self.sentiment_indicators['positive'] if word in prompt_lower)
            # Negative indicators
            negative_count = sum(1 for word in self.sentiment_indicators['negative'] if word in prompt_lower)
            
            if positive_count > negative_count:
                sentiment_score = min(1.0, positive_count * 0.3)
            elif negative_count > positive_count:
                sentiment_score = max(-1.0, -negative_count * 0.3)
            
            sentiments.append(sentiment_score)
        
        return round(sum(sentiments) / len(sentiments), 2) if sentiments else 0.0
    
    def _generate_detailed_summary(self, prompts: List[str]) -> str:
        """Generate a detailed summary of user characteristics"""
        analysis = self.analyze_prompts(prompts)
        
        summary_parts = []
        
        # Interests summary
        if 'interests' in analysis and analysis['interests']:
            interests_str = ', '.join(analysis['interests'])
            summary_parts.append(f"This user is interested in {interests_str} travel experiences.")
        
        # Travel patterns
        if 'travel_preferences' in analysis:
            prefs = analysis['travel_preferences']
            if prefs.get('preferred_destinations'):
                dests = ', '.join(prefs['preferred_destinations'])
                summary_parts.append(f"Preferred destinations include {dests}.")
        
        # Budget profile
        if 'budget_profile' in analysis:
            budget = analysis['budget_profile']
            if budget.get('budget_tier') == 'luxury':
                summary_parts.append("User has a luxury travel budget and is willing to spending on premium experiences.")
            elif budget.get('budget_tier') == 'budget':
                summary_parts.append("User is cost-conscious and looks for affordable travel options.")
        
        # Decision style
        if 'decision_style' in analysis:
            style = analysis['decision_style']
            summary_parts.append(f"Adopts a {style} decision-making approach, researching thoroughly before booking.")
        
        # Personality
        if 'personality_traits' in analysis and analysis['personality_traits']:
            traits_str = ', '.join(analysis['personality_traits'])
            summary_parts.append(f"Personality: {traits_str}.")
        
        # Pain points
        if 'pain_points' in analysis and analysis['pain_points']:
            pain_str = ', '.join(analysis['pain_points'])
            summary_parts.append(f"Key concerns: {pain_str}.")
        
        return ' '.join(summary_parts) if summary_parts else "Limited information available for user characterization."
    
    def _calculate_confidence(self, prompts: List[str]) -> float:
        """Calculate confidence score of analysis"""
        # More prompts = higher confidence
        prompt_count_confidence = min(len(prompts) / 10, 1.0)
        
        # More detailed prompts = higher confidence
        avg_prompt_length = sum(len(p.split()) for p in prompts) / len(prompts) if prompts else 0
        length_confidence = min(avg_prompt_length / 50, 1.0)
        
        return round((prompt_count_confidence + length_confidence) / 2, 2)
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'travel_preferences': {},
            'budget_profile': {},
            'booking_patterns': {},
            'interests': [],
            'personality_traits': [],
            'pain_points': [],
            'motivation_drivers': [],
            'decision_style': 'balanced',
            'tone_preference': 'helpful',
            'communication_style': 'balanced',
            'avg_sentiment': 0.0,
            'detailed_summary': 'Insufficient data for analysis.',
            'confidence_score': 0.0,
        }
