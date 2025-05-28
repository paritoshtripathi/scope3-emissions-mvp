"""
Data Insight Expert for dynamic dashboard visualization and analysis
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import numpy as np
from src.rag.agents.base_agent import BaseAgent

@dataclass
class VisualizationUpdate:
    component_id: str
    update_type: str  # 'data', 'filter', 'highlight', 'zoom'
    data: Dict[str, Any]
    animation: Optional[Dict[str, Any]] = None

@dataclass
class DataInsight:
    insight_type: str
    description: str
    confidence: float
    visualization_updates: List[VisualizationUpdate]
    related_metrics: List[str]

class DataInsightExpert(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DataInsightExpert",
            description="Specialized in data analysis and dynamic dashboard visualization"
        )
        
        # Dashboard components mapping
        self.dashboard_components = {
            'emissions_trend': {
                'type': 'line_chart',
                'metrics': ['total_emissions', 'category_emissions'],
                'update_types': ['data', 'highlight', 'filter']
            },
            'category_distribution': {
                'type': 'pie_chart',
                'metrics': ['category_breakdown'],
                'update_types': ['data', 'highlight']
            },
            'reduction_progress': {
                'type': 'bar_chart',
                'metrics': ['reduction_targets', 'actual_reduction'],
                'update_types': ['data', 'highlight', 'filter']
            },
            'hotspot_analysis': {
                'type': 'heat_map',
                'metrics': ['emission_intensity', 'category_impact'],
                'update_types': ['data', 'zoom', 'highlight']
            }
        }
        
        # Analysis capabilities
        self.analysis_types = {
            'trend_analysis': {
                'description': 'Analyze temporal patterns and trends',
                'required_data': ['time_series', 'metric_values'],
                'visualization': ['emissions_trend']
            },
            'distribution_analysis': {
                'description': 'Analyze category distributions and proportions',
                'required_data': ['category_data', 'values'],
                'visualization': ['category_distribution']
            },
            'comparison_analysis': {
                'description': 'Compare different metrics or periods',
                'required_data': ['comparison_metrics', 'time_periods'],
                'visualization': ['reduction_progress']
            },
            'hotspot_analysis': {
                'description': 'Identify high-impact areas',
                'required_data': ['impact_metrics', 'categories'],
                'visualization': ['hotspot_analysis']
            }
        }

    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data and determine required dashboard updates
        
        Args:
            context: Current context including query and data
            
        Returns:
            Analysis results and visualization updates
        """
        try:
            # Extract query intent and data
            query = context.get('query', '').lower()
            data = context.get('data', {})
            
            # Determine required analysis types
            required_analysis = self._determine_analysis_types(query, data)
            
            # Perform analysis
            insights = []
            visualization_updates = []
            
            for analysis_type in required_analysis:
                if analysis_type in self.analysis_types:
                    # Perform specific analysis
                    analysis_result = await self._perform_analysis(
                        analysis_type,
                        data,
                        context
                    )
                    
                    if analysis_result:
                        insights.append(analysis_result)
                        visualization_updates.extend(
                            analysis_result.visualization_updates
                        )
            
            # Update context with results
            return {
                **context,
                'data_insights': insights,
                'visualization_updates': visualization_updates,
                'metrics_analyzed': self._get_analyzed_metrics(insights)
            }
            
        except Exception as e:
            return {
                **context,
                'error': str(e),
                'fallback_visualization': self._get_fallback_visualization()
            }

    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate visualization updates and insights
        
        Args:
            context: Current context including analysis results
            
        Returns:
            Dashboard updates and insight descriptions
        """
        try:
            insights = context.get('data_insights', [])
            visualization_updates = context.get('visualization_updates', [])
            
            # Prepare dashboard updates
            dashboard_updates = {
                'updates': [
                    {
                        'component': update.component_id,
                        'type': update.update_type,
                        'data': update.data,
                        'animation': update.animation
                    }
                    for update in visualization_updates
                ],
                'insights': [
                    {
                        'type': insight.insight_type,
                        'description': insight.description,
                        'confidence': insight.confidence,
                        'related_metrics': insight.related_metrics
                    }
                    for insight in insights
                ]
            }
            
            return {
                'dashboard_updates': dashboard_updates,
                'confidence': np.mean([i.confidence for i in insights]) if insights else 0.5,
                'metadata': {
                    'components_updated': list(set(u.component_id for u in visualization_updates)),
                    'metrics_analyzed': context.get('metrics_analyzed', [])
                }
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'fallback_response': self._get_fallback_response()
            }

    def _determine_analysis_types(
        self,
        query: str,
        data: Dict[str, Any]
    ) -> List[str]:
        """Determine required types of analysis based on query"""
        required_analysis = []
        
        # Check for temporal analysis needs
        if any(term in query for term in ['trend', 'over time', 'historical']):
            required_analysis.append('trend_analysis')
            
        # Check for distribution analysis needs
        if any(term in query for term in ['distribution', 'breakdown', 'proportion']):
            required_analysis.append('distribution_analysis')
            
        # Check for comparison needs
        if any(term in query for term in ['compare', 'difference', 'versus']):
            required_analysis.append('comparison_analysis')
            
        # Check for hotspot analysis needs
        if any(term in query for term in ['hotspot', 'highest', 'major']):
            required_analysis.append('hotspot_analysis')
            
        return required_analysis

    async def _perform_analysis(
        self,
        analysis_type: str,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Optional[DataInsight]:
        """Perform specific type of analysis"""
        analysis_config = self.analysis_types[analysis_type]
        
        # Check data availability
        required_data = analysis_config['required_data']
        if not all(key in data for key in required_data):
            return None
            
        # Perform analysis based on type
        if analysis_type == 'trend_analysis':
            return await self._analyze_trends(data, context)
            
        elif analysis_type == 'distribution_analysis':
            return await self._analyze_distribution(data, context)
            
        elif analysis_type == 'comparison_analysis':
            return await self._analyze_comparison(data, context)
            
        elif analysis_type == 'hotspot_analysis':
            return await self._analyze_hotspots(data, context)
            
        return None

    async def _analyze_trends(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> DataInsight:
        """Analyze temporal trends in data"""
        # Implement trend analysis logic
        visualization_updates = [
            VisualizationUpdate(
                component_id='emissions_trend',
                update_type='data',
                data={
                    'series': data.get('time_series', []),
                    'metrics': data.get('metric_values', [])
                },
                animation={'duration': 500, 'easing': 'easeInOut'}
            )
        ]
        
        return DataInsight(
            insight_type='trend_analysis',
            description='Temporal analysis of emissions data',
            confidence=0.8,
            visualization_updates=visualization_updates,
            related_metrics=['total_emissions', 'category_emissions']
        )

    async def _analyze_distribution(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> DataInsight:
        """Analyze category distributions"""
        visualization_updates = [
            VisualizationUpdate(
                component_id='category_distribution',
                update_type='data',
                data={
                    'categories': data.get('category_data', []),
                    'values': data.get('values', [])
                },
                animation={'duration': 500, 'easing': 'easeInOut'}
            )
        ]
        
        return DataInsight(
            insight_type='distribution_analysis',
            description='Distribution analysis of emissions by category',
            confidence=0.85,
            visualization_updates=visualization_updates,
            related_metrics=['category_breakdown']
        )

    async def _analyze_comparison(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> DataInsight:
        """Analyze metric comparisons"""
        visualization_updates = [
            VisualizationUpdate(
                component_id='reduction_progress',
                update_type='data',
                data={
                    'metrics': data.get('comparison_metrics', []),
                    'periods': data.get('time_periods', [])
                },
                animation={'duration': 500, 'easing': 'easeInOut'}
            )
        ]
        
        return DataInsight(
            insight_type='comparison_analysis',
            description='Comparative analysis of reduction progress',
            confidence=0.75,
            visualization_updates=visualization_updates,
            related_metrics=['reduction_targets', 'actual_reduction']
        )

    async def _analyze_hotspots(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> DataInsight:
        """Analyze emission hotspots"""
        visualization_updates = [
            VisualizationUpdate(
                component_id='hotspot_analysis',
                update_type='data',
                data={
                    'intensity': data.get('impact_metrics', []),
                    'categories': data.get('categories', [])
                },
                animation={'duration': 500, 'easing': 'easeInOut'}
            )
        ]
        
        return DataInsight(
            insight_type='hotspot_analysis',
            description='Analysis of high-impact emission areas',
            confidence=0.9,
            visualization_updates=visualization_updates,
            related_metrics=['emission_intensity', 'category_impact']
        )

    def _get_analyzed_metrics(
        self,
        insights: List[DataInsight]
    ) -> List[str]:
        """Get list of all analyzed metrics"""
        metrics = []
        for insight in insights:
            metrics.extend(insight.related_metrics)
        return list(set(metrics))

    def _get_fallback_visualization(self) -> List[VisualizationUpdate]:
        """Get fallback visualization updates"""
        return [
            VisualizationUpdate(
                component_id='emissions_trend',
                update_type='data',
                data={'error': 'Data unavailable'},
                animation=None
            )
        ]

    def _get_fallback_response(self) -> Dict[str, Any]:
        """Get fallback response"""
        return {
            'dashboard_updates': {
                'updates': [],
                'insights': [{
                    'type': 'error',
                    'description': 'Unable to analyze data',
                    'confidence': 0.0,
                    'related_metrics': []
                }]
            },
            'confidence': 0.0,
            'metadata': {
                'error': True,
                'components_updated': []
            }
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get expert capabilities summary"""
        return {
            'dashboard_components': list(self.dashboard_components.keys()),
            'analysis_types': list(self.analysis_types.keys()),
            'update_types': ['data', 'filter', 'highlight', 'zoom']
        }