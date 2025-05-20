"""
Specialized Scope3 Domain Expert Agent
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from src.rag.agents.base_agent import BaseAgent

@dataclass
class Scope3Analysis:
    category: str
    confidence: float
    factors: List[str]
    methodology: str
    recommendations: List[Dict[str, Any]]
    references: List[str]

class Scope3Expert(BaseAgent):
    def __init__(self):
        """Initialize Scope3 domain expert"""
        super().__init__(
            name="scope3_expert",
            description="Expert in Scope 3 emissions analysis and recommendations"
        )
        
        # Category-specific expertise
        self.category_expertise = {
            'purchased_goods': ['spend-based', 'supplier-specific', 'hybrid'],
            'capital_goods': ['asset-lifetime', 'depreciation'],
            'fuel_energy': ['upstream-emissions', 'transmission-loss'],
            'transportation': ['distance-based', 'fuel-based', 'spend-based'],
            'waste': ['waste-type', 'treatment-specific'],
            'business_travel': ['distance-based', 'spend-based'],
            'employee_commuting': ['survey-based', 'average-data'],
            'leased_assets': ['asset-specific', 'average-data'],
            'processing': ['process-specific', 'average-data'],
            'use_phase': ['lifetime-emissions', 'energy-consumption'],
            'end_of_life': ['disposal-method', 'material-specific'],
            'franchises': ['franchise-specific', 'average-data'],
            'investments': ['investment-specific', 'average-data']
        }
        
        # Calculation methodologies
        self.methodologies = {
            'spend_based': {
                'description': 'Calculate emissions based on financial spend',
                'required_data': ['spend_amount', 'emission_factor'],
                'limitations': ['Less accurate than activity data']
            },
            'supplier_specific': {
                'description': 'Use supplier-provided emission data',
                'required_data': ['supplier_emissions', 'allocation_factor'],
                'limitations': ['Data availability', 'Consistency']
            },
            'activity_based': {
                'description': 'Calculate based on activity metrics',
                'required_data': ['activity_data', 'emission_factor'],
                'limitations': ['Data collection complexity']
            }
        }
        
        # Reduction strategies database
        self.reduction_strategies = {
            'supplier_engagement': {
                'description': 'Work with suppliers to reduce emissions',
                'potential_impact': 'High',
                'implementation_complexity': 'Medium',
                'applicable_categories': ['purchased_goods', 'capital_goods']
            },
            'material_substitution': {
                'description': 'Use lower-emission materials',
                'potential_impact': 'High',
                'implementation_complexity': 'Medium',
                'applicable_categories': ['purchased_goods', 'packaging']
            },
            'process_optimization': {
                'description': 'Optimize processes for efficiency',
                'potential_impact': 'Medium',
                'implementation_complexity': 'Low',
                'applicable_categories': ['processing', 'manufacturing']
            }
        }

    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute thinking step with given context
        
        Args:
            context: Current context including query and retrieved documents
            
        Returns:
            Updated context with agent's thoughts
        """
        try:
            # Perform Scope3 analysis
            analysis = await self.analyze(
                query=context.get('query', ''),
                context=context
            )
            
            # Update context with analysis results
            thoughts = {
                'category': analysis.category,
                'confidence': analysis.confidence,
                'relevant_factors': analysis.factors,
                'recommended_methodology': analysis.methodology,
                'potential_strategies': analysis.recommendations,
                'key_references': analysis.references,
                'reasoning': {
                    'methodology_choice': f"Selected {analysis.methodology} based on available data and category requirements",
                    'confidence_factors': f"Confidence score of {analysis.confidence} based on data quality and factor coverage",
                    'key_considerations': [rec['description'] for rec in analysis.recommendations]
                }
            }
            
            # Update agent's memory
            self.update_memory({
                'analysis': thoughts,
                'context': context
            })
            
            return {
                **context,
                'scope3_analysis': thoughts
            }
            
        except Exception as e:
            logging.error(f"Error in Scope3Expert thinking: {e}")
            return {
                **context,
                'scope3_analysis': {
                    'error': str(e),
                    'fallback': True
                }
            }

    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action based on thoughts
        
        Args:
            context: Current context including thoughts
            
        Returns:
            Action results with recommendations and next steps
        """
        try:
            analysis = context.get('scope3_analysis', {})
            category = analysis.get('category', 'general')
            
            # Generate actionable recommendations
            actions = {
                'immediate_actions': [],
                'data_requirements': [],
                'next_steps': []
            }
            
            # Add methodology-specific actions
            methodology = analysis.get('recommended_methodology')
            if methodology in self.methodologies:
                actions['data_requirements'].extend(
                    self.methodologies[methodology]['required_data']
                )
            
            # Add category-specific actions
            if category in self.category_expertise:
                expertise = self.category_expertise[category]
                actions['immediate_actions'].append({
                    'action': 'data_collection',
                    'details': f"Collect data for {', '.join(expertise)} analysis"
                })
            
            # Add reduction strategy actions
            for strategy in analysis.get('potential_strategies', []):
                actions['next_steps'].append({
                    'action': 'implement_strategy',
                    'strategy': strategy['type'],
                    'priority': strategy.get('priority', 'Medium'),
                    'details': strategy['description']
                })
            
            # Update agent's state
            self.update_state({
                'last_category': category,
                'recommended_actions': actions
            })
            
            return {
                'actions': actions,
                'metadata': {
                    'category': category,
                    'confidence': analysis.get('confidence', 0.0),
                    'timestamp': context.get('timestamp')
                }
            }
            
        except Exception as e:
            logging.error(f"Error in Scope3Expert action: {e}")
            return {
                'error': str(e),
                'fallback_actions': {
                    'immediate_actions': [{
                        'action': 'data_collection',
                        'details': 'Collect basic category data'
                    }],
                    'next_steps': [{
                        'action': 'consult_documentation',
                        'details': 'Review GHG Protocol guidance'
                    }]
                }
            }

    async def analyze(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Scope3Analysis:
        """
        Analyze Scope3 emissions query and context
        
        Args:
            query: User query
            context: Query context including category and data
            
        Returns:
            Detailed Scope3 analysis
        """
        category = 'general'  # Initialize with default category
        try:
            # Extract category and relevant factors
            category = self._extract_category(query, context)
            relevant_factors = self._identify_relevant_factors(category, context)
            
            # Determine best methodology
            methodology = self._determine_methodology(category, context)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                category,
                context,
                relevant_factors
            )
            
            # Find relevant references
            references = self._find_references(category, methodology)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                category,
                context,
                relevant_factors
            )
            
            return Scope3Analysis(
                category=category,
                confidence=confidence,
                factors=relevant_factors,
                methodology=methodology,
                recommendations=recommendations,
                references=references
            )
            
        except Exception as e:
            logging.error(f"Error in Scope3 analysis: {e}")
            return self._get_fallback_analysis(category)

    def _extract_category(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> str:
        """Extract Scope3 category from query and context"""
        # First check context
        if 'scope3_category' in context:
            return context['scope3_category']
            
        # Check query for category keywords
        query_lower = query.lower()
        for category in self.category_expertise.keys():
            if category.lower().replace('_', ' ') in query_lower:
                return category
                
        # Default to most general category
        return 'general'

    def _identify_relevant_factors(
        self,
        category: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Identify relevant emission factors"""
        factors = []
        
        # Add category-specific factors
        if category in self.category_expertise:
            factors.extend(self.category_expertise[category])
            
        # Add context-based factors
        if 'data_available' in context:
            available_data = context['data_available']
            if 'spend_data' in available_data:
                factors.append('spend-based')
            if 'activity_data' in available_data:
                factors.append('activity-based')
            if 'supplier_data' in available_data:
                factors.append('supplier-specific')
                
        return list(set(factors))  # Remove duplicates

    def _determine_methodology(
        self,
        category: str,
        context: Dict[str, Any]
    ) -> str:
        """Determine best calculation methodology"""
        if category not in self.category_expertise:
            return 'general'
            
        # Check available data
        if 'data_available' in context:
            data = context['data_available']
            
            # Prefer supplier-specific when available
            if 'supplier_data' in data:
                return 'supplier_specific'
                
            # Use activity-based if possible
            if 'activity_data' in data:
                return 'activity_based'
                
            # Fallback to spend-based
            if 'spend_data' in data:
                return 'spend_based'
                
        # Default to category's first methodology
        return self.category_expertise[category][0]

    def _generate_recommendations(
        self,
        category: str,
        context: Dict[str, Any],
        factors: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate category-specific recommendations"""
        recommendations = []
        
        # Add methodology-specific recommendations
        if 'spend_based' in factors:
            recommendations.append({
                'type': 'data_quality',
                'description': 'Consider collecting activity data for more accuracy',
                'priority': 'High'
            })
            
        # Add reduction strategies
        for strategy, details in self.reduction_strategies.items():
            if category in details['applicable_categories']:
                recommendations.append({
                    'type': 'reduction_strategy',
                    'strategy': strategy,
                    'description': details['description'],
                    'impact': details['potential_impact'],
                    'complexity': details['implementation_complexity']
                })
                
        return recommendations

    def _find_references(
        self,
        category: str,
        methodology: str
    ) -> List[str]:
        """Find relevant documentation references"""
        references = []
        
        # Add methodology documentation
        if methodology in self.methodologies:
            references.append(f"Methodology Guide: {methodology}")
            
        # Add category-specific guidance
        if category in self.category_expertise:
            references.append(f"Category Guidance: {category}")
            
        # Add general references
        references.extend([
            "GHG Protocol Scope 3 Standard",
            "Technical Guidance for Calculating Scope 3 Emissions"
        ])
        
        return references

    def _calculate_confidence(
        self,
        category: str,
        context: Dict[str, Any],
        factors: List[str]
    ) -> float:
        """Calculate confidence score for the analysis"""
        score = 0.0
        
        # Category expertise
        if category in self.category_expertise:
            score += 0.3
            
        # Data quality
        if 'data_available' in context:
            data = context['data_available']
            if 'supplier_data' in data:
                score += 0.3
            elif 'activity_data' in data:
                score += 0.2
            elif 'spend_data' in data:
                score += 0.1
                
        # Factor coverage
        factor_score = len(factors) / len(self.category_expertise.get(category, [1]))
        score += factor_score * 0.2
        
        return min(score, 1.0)

    def _get_fallback_analysis(self, category: str) -> Scope3Analysis:
        """Provide fallback analysis when errors occur"""
        return Scope3Analysis(
            category=category,
            confidence=0.3,
            factors=['general'],
            methodology='general',
            recommendations=[{
                'type': 'data_collection',
                'description': 'Collect more detailed data for accurate analysis',
                'priority': 'High'
            }],
            references=[
                "GHG Protocol Scope 3 Standard",
                "Technical Guidance for Calculating Scope 3 Emissions"
            ]
        )

    def get_expertise_summary(self) -> Dict[str, Any]:
        """Get summary of agent's expertise"""
        return {
            'categories': list(self.category_expertise.keys()),
            'methodologies': list(self.methodologies.keys()),
            'reduction_strategies': list(self.reduction_strategies.keys())
        }

    def get_state(self) -> Dict[str, Any]:
        """Get current state of the expert"""
        base_state = super().get_state()
        expert_state = {
            'active_categories': list(self.category_expertise.keys()),
            'available_methodologies': list(self.methodologies.keys()),
            'strategy_count': len(self.reduction_strategies)
        }
        return {**base_state, **expert_state}