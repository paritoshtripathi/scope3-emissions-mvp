"""
Enhanced Mixture of Experts Router with Improved Coordination
"""
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass
from src.rag.agents.base_agent import BaseAgent
from src.rag.agents.scope3_expert import Scope3Expert
from src.rag.agents.data_insight_expert import DataInsightExpert
from src.rag.agents.narrative_expert import NarrativeExpert
from src.rag.agents.tot_reasoner import ToTReasoner

@dataclass
class ExpertAssignment:
    expert_id: str
    confidence: float
    reasoning: str
    priority: int

class MoERouter:
    def __init__(self):
        """Initialize enhanced MoE router"""
        # Initialize experts
        self.experts = {
            'scope3': Scope3Expert(),
            'data_insight': DataInsightExpert(),
            'narrative': NarrativeExpert(),
            'reasoning': ToTReasoner()
        }
        
        # Expert coordination settings
        self.coordination_rules = {
            'max_concurrent': 3,
            'min_confidence': 0.4,
            'fallback_chain': ['scope3', 'data_insight', 'reasoning']
        }
        
        # Performance tracking
        self.performance_metrics = {
            expert_id: {
                'success_rate': 1.0,
                'avg_confidence': 1.0,
                'calls': 0
            }
            for expert_id in self.experts
        }
        
        # Cache for expert assignments
        self.assignment_cache = {}

    async def think(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route query to appropriate experts
        
        Args:
            context: Query context including all relevant information
            
        Returns:
            Expert assignments and coordination plan
        """
        try:
            # 1. Analyze query requirements
            requirements = self._analyze_requirements(context)
            
            # 2. Select experts
            expert_assignments = self._select_experts(requirements, context)
            
            # 3. Create coordination plan
            coordination_plan = self._create_coordination_plan(
                expert_assignments,
                context
            )
            
            # 4. Update cache
            cache_key = self._get_cache_key(context)
            self.assignment_cache[cache_key] = {
                'assignments': expert_assignments,
                'plan': coordination_plan
            }
            
            return {
                'expert_assignments': expert_assignments,
                'coordination_plan': coordination_plan,
                'requirements': requirements
            }
            
        except Exception as e:
            logging.error(f"Error in MoE routing: {e}")
            return self._get_fallback_assignments(context)

    async def act(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute expert actions based on assignments
        
        Args:
            context: Query context with expert assignments
            
        Returns:
            Combined expert responses
        """
        try:
            # Get cached assignments
            cache_key = self._get_cache_key(context)
            cached = self.assignment_cache.get(cache_key, {})
            assignments = cached.get('assignments', [])
            plan = cached.get('plan', {})
            
            # Execute expert actions in order
            responses = {}
            for stage in plan['stages']:
                stage_responses = await self._execute_stage(
                    stage,
                    context,
                    responses
                )
                responses.update(stage_responses)
                
            # Update performance metrics
            self._update_metrics(assignments, responses)
            
            return self._combine_responses(responses, plan)
            
        except Exception as e:
            logging.error(f"Error executing expert actions: {e}")
            return self._get_fallback_response(context)

    def _analyze_requirements(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze query requirements"""
        requirements = {
            'expertise_needed': [],
            'complexity': 'low',
            'priority_areas': []
        }
        
        query = context.get('query', '').lower()
        
        # Check for Scope3 requirements
        if any(term in query for term in ['emission', 'scope3', 'carbon']):
            requirements['expertise_needed'].append('scope3')
            
        # Check for data analysis needs
        if any(term in query for term in ['analyze', 'compare', 'trend']):
            requirements['expertise_needed'].append('data_insight')
            
        # Check for explanation needs
        if any(term in query for term in ['explain', 'describe', 'summarize']):
            requirements['expertise_needed'].append('narrative')
            
        # Assess complexity
        if len(requirements['expertise_needed']) > 2:
            requirements['complexity'] = 'high'
        elif len(requirements['expertise_needed']) > 1:
            requirements['complexity'] = 'medium'
            
        return requirements

    def _select_experts(
        self,
        requirements: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ExpertAssignment]:
        """Select appropriate experts based on requirements"""
        assignments = []
        
        # Always include Scope3 expert for domain expertise
        assignments.append(
            ExpertAssignment(
                expert_id='scope3',
                confidence=0.8,
                reasoning="Primary domain expert for Scope3 emissions",
                priority=1
            )
        )
        
        # Add data insight expert if needed
        if 'data_insight' in requirements['expertise_needed']:
            assignments.append(
                ExpertAssignment(
                    expert_id='data_insight',
                    confidence=0.7,
                    reasoning="Required for data analysis",
                    priority=2
                )
            )
            
        # Add narrative expert for complex queries
        if requirements['complexity'] in ['medium', 'high']:
            assignments.append(
                ExpertAssignment(
                    expert_id='narrative',
                    confidence=0.6,
                    reasoning="Required for comprehensive explanation",
                    priority=3
                )
            )
            
        # Add reasoning expert for complex cases
        if requirements['complexity'] == 'high':
            assignments.append(
                ExpertAssignment(
                    expert_id='reasoning',
                    confidence=0.7,
                    reasoning="Required for complex reasoning",
                    priority=2
                )
            )
            
        return assignments

    def _create_coordination_plan(
        self,
        assignments: List[ExpertAssignment],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create plan for expert coordination"""
        # Sort assignments by priority
        sorted_assignments = sorted(
            assignments,
            key=lambda x: (x.priority, -x.confidence)
        )
        
        # Create execution stages
        stages = []
        current_stage = []
        
        for assignment in sorted_assignments:
            # Start new stage if max_concurrent reached
            if len(current_stage) >= self.coordination_rules['max_concurrent']:
                stages.append(current_stage)
                current_stage = []
                
            current_stage.append(assignment.expert_id)
            
        # Add final stage
        if current_stage:
            stages.append(current_stage)
            
        return {
            'stages': stages,
            'dependencies': self._get_dependencies(assignments),
            'fallback_chain': self.coordination_rules['fallback_chain']
        }

    async def _execute_stage(
        self,
        stage: List[str],
        context: Dict[str, Any],
        previous_responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a stage of expert actions"""
        stage_responses = {}
        
        # Execute experts in parallel (simulated)
        for expert_id in stage:
            try:
                expert = self.experts[expert_id]
                response = await expert.analyze(
                    context['query'],
                    {
                        **context,
                        'previous_responses': previous_responses
                    }
                )
                stage_responses[expert_id] = response
                
            except Exception as e:
                logging.error(f"Error with expert {expert_id}: {e}")
                # Try fallback
                stage_responses[expert_id] = await self._get_expert_fallback(
                    expert_id,
                    context
                )
                
        return stage_responses

    def _get_dependencies(
        self,
        assignments: List[ExpertAssignment]
    ) -> Dict[str, List[str]]:
        """Get expert dependencies"""
        dependencies = {}
        
        # Define basic dependencies
        dependencies['narrative'] = ['scope3', 'data_insight']
        dependencies['reasoning'] = ['scope3']
        dependencies['data_insight'] = ['scope3']
        
        return dependencies

    def _update_metrics(
        self,
        assignments: List[ExpertAssignment],
        responses: Dict[str, Any]
    ) -> None:
        """Update expert performance metrics"""
        for assignment in assignments:
            expert_id = assignment.expert_id
            metrics = self.performance_metrics[expert_id]
            
            # Update call count
            metrics['calls'] += 1
            
            # Update success rate
            success = expert_id in responses
            metrics['success_rate'] = (
                (metrics['success_rate'] * (metrics['calls'] - 1) + success)
                / metrics['calls']
            )
            
            # Update confidence
            if success:
                response = responses[expert_id]
                confidence = getattr(response, 'confidence', 0.5)
                metrics['avg_confidence'] = (
                    (metrics['avg_confidence'] * (metrics['calls'] - 1) + confidence)
                    / metrics['calls']
                )

    def _combine_responses(
        self,
        responses: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine expert responses based on plan"""
        combined = {
            'analysis': {},
            'recommendations': [],
            'confidence': 0.0,
            'metadata': {
                'experts_used': list(responses.keys()),
                'coordination_plan': plan
            }
        }
        
        # Combine scope3 analysis
        if 'scope3' in responses:
            scope3_response = responses['scope3']
            combined['analysis']['scope3'] = {
                'category': scope3_response.category,
                'factors': scope3_response.factors,
                'methodology': scope3_response.methodology
            }
            combined['recommendations'].extend(scope3_response.recommendations)
            combined['confidence'] = scope3_response.confidence
            
        # Add data insights
        if 'data_insight' in responses:
            data_response = responses['data_insight']
            combined['analysis']['data_insights'] = data_response
            
        # Add narrative
        if 'narrative' in responses:
            combined['narrative'] = responses['narrative']
            
        # Add reasoning
        if 'reasoning' in responses:
            combined['reasoning'] = responses['reasoning']
            
        return combined

    def _get_cache_key(self, context: Dict[str, Any]) -> str:
        """Generate cache key from context"""
        return f"{context.get('query', '')}_{context.get('scope3_category', '')}"

    def _get_fallback_assignments(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get fallback expert assignments"""
        return {
            'expert_assignments': [
                ExpertAssignment(
                    expert_id='scope3',
                    confidence=0.5,
                    reasoning="Fallback to primary expert",
                    priority=1
                )
            ],
            'coordination_plan': {
                'stages': [['scope3']],
                'dependencies': {},
                'fallback_chain': self.coordination_rules['fallback_chain']
            },
            'requirements': {
                'expertise_needed': ['scope3'],
                'complexity': 'low',
                'priority_areas': []
            }
        }

    async def _get_expert_fallback(
        self,
        expert_id: str,
        context: Dict[str, Any]
    ) -> Any:
        """Get fallback response for failed expert"""
        # Try next expert in fallback chain
        chain = self.coordination_rules['fallback_chain']
        if expert_id in chain:
            idx = chain.index(expert_id)
            if idx + 1 < len(chain):
                fallback_id = chain[idx + 1]
                try:
                    return await self.experts[fallback_id].analyze(
                        context['query'],
                        context
                    )
                except Exception:
                    pass
                    
        # Ultimate fallback
        return self.experts['scope3']._get_fallback_analysis(
            context.get('scope3_category', 'general')
        )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get expert performance metrics"""
        return {
            'expert_metrics': self.performance_metrics,
            'coordination_rules': self.coordination_rules,
            'cache_size': len(self.assignment_cache)
        }

    def reload_config(self) -> None:
        """Reload configuration settings"""
        # Reload coordination rules
        self.coordination_rules = {
            'max_concurrent': 3,
            'min_confidence': 0.4,
            'fallback_chain': ['scope3', 'data_insight', 'reasoning']
        }
        
        # Clear caches
        self.assignment_cache.clear()
        
        # Reset metrics
        for metrics in self.performance_metrics.values():
            metrics.update({
                'success_rate': 1.0,
                'avg_confidence': 1.0,
                'calls': 0
            })