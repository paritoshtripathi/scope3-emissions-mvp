"""
Enterprise-grade Conversation Expert with LLM Integration
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .base_agent import BaseAgent
from ..models.inference import InferenceEngine

@dataclass
class ConversationContext:
    domain_focus: str
    confidence: float
    requires_expertise: bool
    suggested_experts: List[str]
    reasoning_chain: List[str]

class ConversationExpert(BaseAgent):
    def __init__(self):
        super().__init__(
            name="conversation_expert",
            description="Natural language understanding and conversation flow expert"
        )
        self.inference = InferenceEngine()
        self.specializations = [
            "natural_language_understanding",
            "intent_classification",
            "context_management",
            "conversation_flow",
            "expert_routing"
        ]

    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze query and determine optimal processing strategy
        """
        try:
            # Extract query and context
            query = context.get('query', '')
            history = context.get('history', [])
            
            # Build analysis context
            analysis_context = self._build_analysis_context(query, history)
            
            # Use LLM for analysis
            analysis_result = await self.inference.generate_response(
                query=query,
                context=analysis_context,
                domain="conversation_analysis"
            )
            
            # Process analysis results
            conversation_context = self._process_analysis(analysis_result, context)
            
            # Determine processing strategy
            strategy = {
                'requires_kb': conversation_context.requires_expertise,
                'domain_focus': conversation_context.domain_focus,
                'expert_routing': {
                    'suggested_experts': conversation_context.suggested_experts,
                    'confidence': conversation_context.confidence
                },
                'reasoning': conversation_context.reasoning_chain
            }
            
            return {
                'conversation_context': conversation_context,
                'processing_strategy': strategy,
                'analysis_result': analysis_result
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'fallback_strategy': {
                    'requires_kb': True,
                    'domain_focus': 'general',
                    'expert_routing': {'suggested_experts': ['scope3']}
                }
            }

    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate appropriate response or route to experts
        """
        try:
            strategy = context.get('processing_strategy', {})
            
            if not strategy.get('requires_kb'):
                # Use LLM for natural conversation
                response_context = self._build_response_context(context)
                response = await self.inference.generate_response(
                    query=context.get('query', ''),
                    context=response_context,
                    domain="conversation_response"
                )
                
                return {
                    'response': response,
                    'confidence': strategy.get('expert_routing', {}).get('confidence', 0.8),
                    'metadata': {
                        'processing_type': 'natural_conversation',
                        'domain_focus': strategy.get('domain_focus'),
                        'reasoning': strategy.get('reasoning', [])
                    }
                }
            
            # Route to domain experts
            return {
                'route_to_experts': strategy.get('expert_routing', {}).get('suggested_experts', []),
                'context_enhancement': {
                    'domain_focus': strategy.get('domain_focus'),
                    'reasoning_chain': strategy.get('reasoning', [])
                },
                'confidence': strategy.get('expert_routing', {}).get('confidence', 0.7)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'fallback_response': {
                    'route_to_experts': ['scope3'],
                    'confidence': 0.5
                }
            }

    def _build_analysis_context(self, query: str, history: List[Dict[str, Any]]) -> str:
        """Build context for analysis"""
        return f"""
        Task: Analyze the following query for a Scope3 emissions analysis system.
        
        Query: {query}
        
        Previous Context:
        {self._format_history(history)}
        
        Analyze for:
        1. Query type (general conversation vs domain-specific)
        2. Required domain expertise (scope3, emissions, analysis)
        3. Confidence in classification
        4. Required reasoning steps
        
        Format response as JSON with:
        - domain: string (general, scope3, analysis)
        - requires_expertise: boolean
        - confidence: float (0-1)
        - reasoning_chain: list of strings
        """

    def _build_response_context(self, context: Dict[str, Any]) -> str:
        """Build context for response generation"""
        strategy = context.get('processing_strategy', {})
        query = context.get('query', '')
        
        return f"""
        Task: Generate a professional response for a Scope3 emissions analysis system.
        
        Query: {query}
        Domain Focus: {strategy.get('domain_focus')}
        Expertise Required: {strategy.get('requires_kb')}
        Confidence: {strategy.get('expert_routing', {}).get('confidence')}
        
        Requirements:
        1. Professional and helpful tone
        2. Focus on emissions analysis when relevant
        3. Natural conversational style
        4. Guide towards system capabilities
        5. No hardcoded responses
        
        Previous Context:
        {self._format_history(context.get('history', []))}
        """

    def _process_analysis(
        self,
        analysis_result: str,
        context: Dict[str, Any]
    ) -> ConversationContext:
        """Process analysis results"""
        try:
            # Parse JSON response
            import json
            result = json.loads(analysis_result)
            
            # Extract key information
            domain = result.get('domain', 'general')
            confidence = result.get('confidence', 0.8)
            requires_expertise = result.get('requires_expertise', True)
            reasoning_chain = result.get('reasoning_chain', [])
            
            # Determine expert routing
            suggested_experts = []
            if requires_expertise:
                if 'scope3' in domain or 'emissions' in domain:
                    suggested_experts.extend(['scope3', 'data_insight'])
                if 'analysis' in domain or 'metrics' in domain:
                    suggested_experts.extend(['data_insight'])
                if len(reasoning_chain) > 2:  # Complex reasoning needed
                    suggested_experts.append('reasoning')
            
            return ConversationContext(
                domain_focus=domain,
                confidence=confidence,
                requires_expertise=requires_expertise,
                suggested_experts=list(dict.fromkeys(suggested_experts)),
                reasoning_chain=reasoning_chain
            )
            
        except Exception as e:
            # Fallback to safe defaults
            return ConversationContext(
                domain_focus='general',
                confidence=0.5,
                requires_expertise=True,
                suggested_experts=['scope3'],
                reasoning_chain=[]
            )

    def _format_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history"""
        if not history:
            return "No previous context"
            
        formatted = []
        for msg in history[-3:]:  # Last 3 messages for context
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            formatted.append(f"{role}: {content}")
            
        return "\n".join(formatted)