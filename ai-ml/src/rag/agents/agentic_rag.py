"""
Enhanced Agentic RAG Agent with MOE, TOT and Self-learning Capabilities
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import numpy as np
from src.rag.agents.base_agent import BaseAgent
from src.rag.agents.tot_reasoner import ToTReasoner
from src.rag.agents.moe_router import MoERouter

@dataclass
class LearningContext:
    kb_embeddings: List[float] = field(default_factory=list)
    user_context_history: List[Dict[str, Any]] = field(default_factory=list)
    learned_patterns: Dict[str, float] = field(default_factory=dict)
    adaptation_weights: Dict[str, float] = field(default_factory=dict)

class AgenticRAG(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AgenticRAG",
            description="Enhanced RAG with MOE, TOT and self-learning capabilities"
        )
        self.specializations = [
            "context_enhancement",
            "query_refinement",
            "response_generation",
            "relevance_assessment",
            "self_learning",
            "expert_routing"
        ]
        
        # Core components
        self.moe_router = MoERouter()
        self.tot_reasoner = ToTReasoner()
        
        # State management
        self.retrieval_history = []
        self.query_refinements = []
        self.learning_context = LearningContext()
        
        # Learning parameters
        self.adaptation_rate = 0.1
        self.context_window_size = 5

    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced thinking process with MOE and TOT integration
        
        Args:
            context: Current context including query and retrieved documents
            
        Returns:
            Updated context with comprehensive analysis
        """
        # Update learning context
        self._update_learning_context(context)
        
        # Generate thought paths using TOT
        tot_context = await self.tot_reasoner.think({
            'problem': context.get('query', ''),
            'constraints': self._extract_constraints(context),
            'history': self.retrieval_history
        })
        
        # Route to appropriate experts using MOE
        expert_assignments = self._route_to_experts(context)
        
        # Analyze context and plan next steps
        retrieval_plan = {
            'needs_refinement': self._needs_query_refinement(context),
            'context_sufficient': self._assess_context_sufficiency(context),
            'focus_areas': self._identify_focus_areas(context),
            'expert_assignments': expert_assignments,
            'thought_paths': tot_context.get('thought_paths', [])
        }

        # Track retrieval history
        if 'retrieved_docs' in context:
            self.retrieval_history.append({
                'query': context.get('query', ''),
                'docs': context.get('retrieved_docs', []),
                'expert_assignments': expert_assignments
            })

        # Update context with enhanced plan
        context['retrieval_plan'] = retrieval_plan
        context['learning_state'] = self._get_learning_state()
        context['confidence_scores'] = self._calculate_confidence_scores(context)
        
        return context

    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute enhanced retrieval and generation strategy
        
        Args:
            context: Current context including retrieval plan
            
        Returns:
            Enhanced response with metadata and learning updates
        """
        plan = context.get('retrieval_plan', {})
        
        if plan.get('needs_refinement'):
            # Get refined query through TOT reasoning
            tot_result = await self.tot_reasoner.act({
                'thought_paths': plan.get('thought_paths', []),
                'context': context
            })
            
            refined_query = self._generate_refined_query(tot_result)
            self.query_refinements.append(refined_query)
            
            return {
                'action': 'refine_query',
                'refined_query': refined_query,
                'reasoning': tot_result.get('reasoning_chain', []),
                'confidence': tot_result.get('confidence', 0.8)
            }
        
        # Generate enhanced response using assigned experts
        expert_responses = await self._gather_expert_responses(
            plan.get('expert_assignments', {}),
            context
        )
        
        # Synthesize final response
        response = {
            'content': self._synthesize_response(expert_responses, context),
            'metadata': {
                'sources': self._extract_sources(context),
                'expert_contributions': self._summarize_expert_contributions(expert_responses),
                'learning_updates': self._get_learning_updates(),
                'confidence': self._calculate_final_confidence(expert_responses)
            }
        }

        # Update learning context with response
        self._update_learning_from_response(response)

        return response

    def _update_learning_context(self, context: Dict[str, Any]) -> None:
        """Update learning context with new information"""
        # Update user context history
        self.learning_context.user_context_history.append({
            'query': context.get('query', ''),
            'timestamp': context.get('timestamp', ''),
            'domain': self._extract_domain(context)
        })
        
        # Maintain window size
        if len(self.learning_context.user_context_history) > self.context_window_size:
            self.learning_context.user_context_history.pop(0)
        
        # Update learned patterns
        self._update_learned_patterns(context)

    def _update_learned_patterns(self, context: Dict[str, Any]) -> None:
        """Update pattern recognition based on new context"""
        domain = self._extract_domain(context)
        current_success = context.get('last_response_success', 0.8)
        
        if domain in self.learning_context.learned_patterns:
            # Adaptive update
            old_value = self.learning_context.learned_patterns[domain]
            self.learning_context.learned_patterns[domain] = (
                (1 - self.adaptation_rate) * old_value +
                self.adaptation_rate * current_success
            )
        else:
            self.learning_context.learned_patterns[domain] = current_success

    def _route_to_experts(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Route query to appropriate experts using MOE"""
        query = context.get('query', '')
        domain = self._extract_domain(context)
        
        # Get expert assignments from MOE router
        assignments = {}
        for expert in self.moe_router.experts:
            if any(spec in query.lower() for spec in expert.specialization):
                confidence = self._calculate_expert_confidence(
                    expert.name,
                    domain,
                    context
                )
                if confidence >= expert.confidence_threshold:
                    assignments[expert.name] = confidence
                    
        return assignments

    async def _gather_expert_responses(
        self,
        expert_assignments: Dict[str, float],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Gather responses from assigned experts"""
        responses = []
        for expert_name, confidence in expert_assignments.items():
            # Get expert instance
            expert = self._get_expert_instance(expert_name)
            if expert:
                response = await expert.think(context)
                responses.append({
                    'expert': expert_name,
                    'response': response,
                    'confidence': confidence
                })
        return responses

    def _calculate_expert_confidence(
        self,
        expert_name: str,
        domain: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for expert assignment"""
        base_confidence = 0.8
        
        # Adjust based on learned patterns
        if domain in self.learning_context.learned_patterns:
            base_confidence *= self.learning_context.learned_patterns[domain]
            
        # Adjust based on historical performance
        historical_performance = self._get_historical_performance(expert_name)
        
        return min(base_confidence * historical_performance, 1.0)

    def _get_historical_performance(self, expert_name: str) -> float:
        """Get historical performance score for expert"""
        relevant_history = [
            h for h in self.retrieval_history
            if expert_name in h.get('expert_assignments', {})
        ]
        
        if not relevant_history:
            return 0.8
            
        return sum(
            h['expert_assignments'][expert_name]
            for h in relevant_history
        ) / len(relevant_history)

    def _synthesize_response(
        self,
        expert_responses: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """Synthesize final response from expert contributions"""
        if not expert_responses:
            return "Insufficient expert coverage to generate response"
            
        # Weight responses by confidence
        weighted_responses = []
        for response in expert_responses:
            content = response['response'].get('content', '')
            confidence = response['confidence']
            weighted_responses.append((content, confidence))
            
        # Combine weighted responses
        total_weight = sum(weight for _, weight in weighted_responses)
        if total_weight == 0:
            return "Unable to generate confident response"
            
        synthesized = " ".join(
            content for content, _ in weighted_responses
        )
        
        return synthesized

    def _get_learning_state(self) -> Dict[str, Any]:
        """Get current learning state"""
        return {
            'learned_patterns': self.learning_context.learned_patterns,
            'adaptation_weights': self.learning_context.adaptation_weights,
            'context_history_size': len(self.learning_context.user_context_history)
        }

    def _get_learning_updates(self) -> Dict[str, Any]:
        """Get learning updates from last interaction"""
        return {
            'pattern_updates': len(self.learning_context.learned_patterns),
            'context_window': self.context_window_size,
            'adaptation_rate': self.adaptation_rate
        }

    def _extract_domain(self, context: Dict[str, Any]) -> str:
        """Extract domain from context"""
        query = context.get('query', '').lower()
        
        # Simple domain extraction logic
        if any(term in query for term in ['emissions', 'carbon', 'scope3']):
            return 'emissions_calculation'
        elif any(term in query for term in ['regulation', 'compliance', 'policy']):
            return 'regulatory_compliance'
        elif any(term in query for term in ['data', 'analysis', 'metrics']):
            return 'data_analysis'
        
        return 'general'

    def _calculate_confidence_scores(self, context: Dict[str, Any]) -> List[float]:
        """Calculate confidence scores for context"""
        scores = [0.8]  # Base confidence
        
        # Add expert confidences
        expert_assignments = context.get('retrieval_plan', {}).get('expert_assignments', {})
        if expert_assignments:
            scores.extend(expert_assignments.values())
            
        # Add TOT confidence
        tot_paths = context.get('retrieval_plan', {}).get('thought_paths', [])
        if tot_paths:
            scores.append(max(path.get('confidence', 0.0) for path in tot_paths))
            
        return scores

    def _calculate_final_confidence(
        self,
        expert_responses: List[Dict[str, Any]]
    ) -> float:
        """Calculate final confidence score"""
        if not expert_responses:
            return 0.5
            
        confidences = [r['confidence'] for r in expert_responses]
        return sum(confidences) / len(confidences)

    def _needs_query_refinement(self, context: Dict[str, Any]) -> bool:
        """Determine if query needs refinement"""
        return (
            len(self.query_refinements) < 3 and
            not self._assess_context_sufficiency(context)
        )

    def _generate_refined_query(self, tot_result: Dict[str, Any]) -> str:
        """Generate refined query based on TOT reasoning"""
        reasoning_chain = tot_result.get('reasoning_chain', [])
        if not reasoning_chain:
            return "Refined query based on default strategy"
            
        return f"Refined query based on reasoning: {reasoning_chain[-1]}"

    def _extract_constraints(self, context: Dict[str, Any]) -> List[str]:
        """Extract constraints from context"""
        constraints = []
        
        # Add basic constraints
        if context.get('max_tokens'):
            constraints.append(f"max_tokens: {context['max_tokens']}")
        if context.get('temperature'):
            constraints.append(f"temperature: {context['temperature']}")
            
        return constraints

    def _get_expert_instance(self, expert_name: str) -> Optional[BaseAgent]:
        """Get expert instance by name"""
        if expert_name == "DataInsightExpert":
            return self.moe_router.data_insight_expert
        elif expert_name == "NarrativeExpert":
            return self.moe_router.narrative_expert
        return None

    def _summarize_expert_contributions(
        self,
        expert_responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize contributions from each expert"""
        return {
            response['expert']: {
                'confidence': response['confidence'],
                'contribution_type': self._get_contribution_type(response)
            }
            for response in expert_responses
        }

    def _get_contribution_type(self, response: Dict[str, Any]) -> str:
        """Determine type of expert contribution"""
        if 'analysis' in str(response.get('response', {})):
            return 'analysis'
        elif 'recommendation' in str(response.get('response', {})):
            return 'recommendation'
        return 'general'