"""
Template Engine for Stock Analysis

Loads and renders analysis templates (Damodaran, Buffett, etc.)
All templates are style-agnostic - they share the same calculation engine.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class TemplateMetadata:
    """Template metadata"""
    template_id: str
    template_name: str
    template_version: str
    author: str
    description: str
    language: str
    output_format: List[str]
    is_public: bool


class TemplateRegistry:
    """Central registry for all available templates"""
    
    def __init__(self, templates_dir: str = "./config/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, Dict] = {}
        self._load_all_templates()
    
    def _load_all_templates(self):
        """Load all template JSON files from config/templates/"""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory {self.templates_dir} does not exist")
            return
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    template_id = template.get('template_id')
                    self.templates[template_id] = template
                    logger.info(f"Loaded template: {template_id}")
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")
    
    def get_template(self, template_id: str = "damodaran_jet") -> Optional[Dict]:
        """Get a template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[str]:
        """List all available template IDs"""
        return list(self.templates.keys())
    
    def validate_template(self, template: Dict) -> tuple[bool, str]:
        """Validate template structure against schema"""
        required_fields = [
            'template_id', 'template_name', 'template_version',
            'metadata', 'data_requirements', 'sections',
            'narrative_config', 'charts_config'
        ]
        
        for field in required_fields:
            if field not in template:
                return False, f"Missing required field: {field}"
        
        return True, "Template is valid"


class TemplateRenderer:
    """Renders analysis template with calculated data"""
    
    def __init__(self, template: Dict, calculation_results: Dict, raw_data: Dict):
        """
        Initialize renderer.
        
        Args:
            template: Template JSON config
            calculation_results: Dict of CalculationResult objects
            raw_data: Raw normalized data (prices, financials, etc.)
        """
        self.template = template
        self.calculations = calculation_results
        self.data = raw_data
    
    def render(self) -> Dict[str, Any]:
        """
        Render template into structured output.
        
        Returns:
            Dict with all rendered sections, narratives, charts
        """
        try:
            rendered_sections = []
            
            for section_config in self.template.get('sections', []):
                rendered_section = self._render_section(section_config)
                if rendered_section:
                    rendered_sections.append(rendered_section)
            
            output = {
                'template_id': self.template['template_id'],
                'template_name': self.template['template_name'],
                'ticker': self.data.get('ticker'),
                'analysis_timestamp': self._get_timestamp(),
                'sections': rendered_sections,
                'sources': self._compile_sources()
            }
            
            return output
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return {'error': str(e)}
    
    def _render_section(self, section_config: Dict) -> Optional[Dict]:
        """Render a single section of the template"""
        try:
            section_id = section_config.get('section_id')
            display_fields = section_config.get('display_fields', [])
            
            # Get data for this section
            section_data = {}
            for field_config in display_fields:
                field_name = field_config.get('field_name')
                
                # Try to get from calculated results first
                if field_name in self.calculations:
                    result = self.calculations[field_name]
                    section_data[field_name] = result.to_dict() if hasattr(result, 'to_dict') else result
                # Then try raw data
                elif field_name in self.data:
                    section_data[field_name] = self.data[field_name]
            
            # Generate narrative if required
            narrative = None
            if section_config.get('narrative_requirements'):
                narrative = self._generate_narrative(section_config)
            
            # Get charts if required
            charts = []
            for chart_ref in section_config.get('chart_references', []):
                chart = self._render_chart(chart_ref)
                if chart:
                    charts.append(chart)
            
            return {
                'section_id': section_id,
                'title': section_config.get('section_name'),
                'data': section_data,
                'narrative': narrative,
                'charts': charts
            }
        except Exception as e:
            logger.error(f"Error rendering section {section_config.get('section_id')}: {e}")
            return None
    
    def _generate_narrative(self, section_config: Dict) -> str:
        """Generate narrative text for section"""
        # This will be enhanced with AI later
        # For now, return placeholder
        return f"Narrative for {section_config.get('section_name')}"
    
    def _render_chart(self, chart_config: Dict) -> Optional[Dict]:
        """Configure chart for rendering"""
        return {
            'chart_id': chart_config.get('chart_id'),
            'chart_type': chart_config.get('chart_type'),
            'metric': chart_config.get('metric'),
            'label': chart_config.get('label')
        }
    
    def _compile_sources(self) -> List[Dict]:
        """Compile all data sources"""
        sources = []
        seen = set()
        
        for calc_result in self.calculations.values():
            if hasattr(calc_result, 'source') and calc_result.source not in seen:
                sources.append({
                    'name': calc_result.source,
                    'timestamp': calc_result.fetch_timestamp
                })
                seen.add(calc_result.source)
        
        return sources
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
