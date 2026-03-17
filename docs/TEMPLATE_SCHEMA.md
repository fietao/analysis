# ANALYSIS TEMPLATE SCHEMA v1.0

## Overview

This document defines the formal structure for **Analysis Templates** — pluggable analysis styles that can be added to Jarvis without changing core code.

Each template is a **JSON configuration** that describes:
- What data sections to fetch/calculate
- How to organize and present them
- What narrative/commentary to generate
- Which charts to show for each metric

The **Calculation Engine** (WACC, ROIC, DCF, MOS, etc.) is **decoupled from templates**. Multiple templates share the same calculations but present them differently.

---

## Core Concept: Template as Blueprint

```
Template = {
  metadata: (info about the template)
  data_requirements: (what to fetch/calculate)
  sections: (how to organize output)
  narrative: (how to tell the story)
  charts: (which metrics get graphed)
}
```

When a user requests an analysis:
```
1. Load template by name (default: "damodaran_jet")
2. Fetch all required data
3. Run all required calculations
4. Render sections in order
5. Generate narratives
6. Return structured JSON with text + charts + data
```

---

## TEMPLATE SCHEMA (JSON Format)

### Root Level

```json
{
  "template_id": "damodaran_jet",
  "template_name": "Damodaran Value Analysis (Thai)",
  "template_version": "1.0.0",
  "author": "JET / Damodaran Framework",
  "description": "Professional valuation report using Damodaran's intrinsic value methodology with Thai narrative",
  "created_date": "2026-03-16",
  "updated_date": "2026-03-16",
  "language": "th",
  "output_format": "pdf|json|html",
  "estimated_build_time_seconds": 45,
  "is_public": true,
  "tags": ["valuation", "fundamental", "thai", "professional"],
  
  "metadata": { ... },
  "data_requirements": { ... },
  "sections": [ ... ],
  "narrative_config": { ... },
  "charts_config": { ... },
  "styling": { ... }
}
```

---

### 1. METADATA

```json
"metadata": {
  "template_id": "damodaran_jet",
  "display_name": "Damodaran Value Analysis (Thai)",
  
  "suitability": {
    "asset_types": ["stock", "etf"],
    "markets": ["us", "thai"],
    "minimum_history_years": 5,
    "requires_earnings_guidance": false,
    "requires_consensus_estimates": true
  },
  
  "dependencies": {
    "calculations": [
      "wacc",
      "fcff",
      "roic",
      "roe",
      "dividend_discount_model",
      "multiple_analysis",
      "margin_of_safety"
    ],
    "data_sources": ["finnhub", "sec_edgar", "bloomberg", "yahoo_finance"],
    "external_apis": ["openai_gpt4_for_narrative"]  // optional for AI generation
  },
  
  "author_info": {
    "name": "JET (Damodaran Framework)",
    "methodology_reference": "Damodaran NYU (Chapter: Valuation)",
    "customization_level": 0  // 0=fixed, 1=user can tweak, 2=fully editable
  }
}
```

---

### 2. DATA REQUIREMENTS

Specifies exactly what data the template needs. The **Data Fetcher** reads this and pulls everything upfront.

```json
"data_requirements": {
  "price_data": {
    "lookback_years": 10,
    "frequency": "daily",
    "fields": ["date", "close", "volume", "adjusted_close"],
    "normalization": "split_adjusted"
  },
  
  "fundamentals": {
    "annual_income_statement": {
      "fields": [
        "revenue",
        "operating_income",
        "net_income",
        "ebit",
        "interest_expense",
        "tax_expense"
      ],
      "years_required": 5
    },
    "annual_balance_sheet": {
      "fields": [
        "total_assets",
        "total_liabilities",
        "shareholders_equity",
        "cash",
        "debt",
        "shares_outstanding"
      ],
      "years_required": 5
    },
    "annual_cash_flow": {
      "fields": [
        "operating_cash_flow",
        "investing_cash_flow",
        "free_cash_flow",
        "capex"
      ],
      "years_required": 5
    }
  },
  
  "market_data": {
    "risk_free_rate": {
      "source": "us_10yr_treasury",
      "refresh_frequency": "daily"
    },
    "market_risk_premium": {
      "source": "damodaran_historical",
      "value": 5.5
    },
    "sector_average": {
      "fields": ["pe_ratio", "price_to_book", "roe", "debt_to_equity"],
      "group_by": "industry"
    },
    "index_benchmarks": {
      "indices": ["SPY", "QQQ", "DIA"],
      "lookback_years": 5
    }
  },
  
  "estimates": {
    "consensus_estimates": {
      "fields": ["eps_current_year", "eps_next_year", "revenue_growth"],
      "source": "yahoo_finance|finnhub"
    },
    "analyst_ratings": {
      "fields": ["rating", "target_price", "rating_count"],
      "required": false
    }
  },
  
  "sec_filings": {
    "latest_forms": ["10-K", "10-Q"],
    "extract_keywords": [
      "risk_factors",
      "competitive_advantages",
      "segment_revenue",
      "management_discussion_analysis"
    ],
    "years_required": 2
  },
  
  "custom_inputs": {
    "allows_user_override": true,
    "override_fields": [
      "long_term_growth_rate",
      "wacc",
      "terminal_multiple"
    ]
  }
}
```

---

### 3. SECTIONS

Defines how output is organized. Each section specifies:
- What calculations it needs
- What data to display
- How to format and narrate

```json
"sections": [
  {
    "section_id": "decision_card",
    "section_name": "การตัดสินใจ (Decision Card)",
    "order": 1,
    "display_type": "card",  // card | table | text | chart | gallery
    
    "description": "Quick buy/hold/sell recommendation with valuation summary",
    
    "required_calculations": {
      "intrinsic_value": {
        "method": "damodaran_dcf",  // Specific calculation method
        "inputs": ["wacc", "fcff_projection", "terminal_growth_rate"]
      },
      "current_price": {
        "method": "live_market_price"
      },
      "margin_of_safety": {
        "method": "intrinsic_minus_price_percent",
        "inputs": ["intrinsic_value", "current_price"]
      }
    },
    
    "display_fields": [
      {
        "field_name": "stock_ticker",
        "display_as": "text",
        "label": "บริษัท (Stock)"
      },
      {
        "field_name": "intrinsic_value",
        "display_as": "currency_large",
        "label": "มูลค่าที่แท้จริง (Intrinsic Value)",
        "precision": 2,
        "currency": "USD"
      },
      {
        "field_name": "current_price",
        "display_as": "currency_large",
        "label": "ราคาตลาดปัจจุบัน (Current Price)",
        "precision": 2,
        "currency": "USD"
      },
      {
        "field_name": "upside_downside",
        "display_as": "percentage_colored",
        "label": "ศักยภาพเพิ่มขึ้น/ลดลง (Upside/Downside)",
        "color_logic": "upside > 20 ? green : upside > 0 ? yellow : red"
      },
      {
        "field_name": "margin_of_safety_percent",
        "display_as": "percentage_colored",
        "label": "ส่วนเสริมความปลอดภัย (Margin of Safety)",
        "color_logic": "mos > 30 ? green : mos > 15 ? yellow : mos > 0 ? orange : red"
      },
      {
        "field_name": "recommendation",
        "display_as": "badge",
        "label": "คำแนะนำ (Recommendation)",
        "badge_logic": {
          "rule_if_upside_gt_30": { "text": "BUY", "color": "green" },
          "rule_if_upside_gt_0": { "text": "HOLD", "color": "yellow" },
          "rule_default": { "text": "SELL", "color": "red" }
        }
      }
    ],
    
    "chart_references": [
      {
        "chart_id": "valuation_comparison",
        "metric": "intrinsic_value",
        "chart_type": "waterfall",  // Shows components of valuation
        "show_in_section": true
      }
    ],
    
    "narrative_requirements": {
      "must_include": [
        "Why we think intrinsic value is X",
        "What must be proven for this thesis to work",
        "Key risks if price doesn't converge"
      ],
      "tone": "professional",
      "language": "thai",
      "length_words": 150
    }
  },
  
  {
    "section_id": "valuation_summary",
    "section_name": "สรุปการประเมินมูลค่า (Valuation Summary)",
    "order": 2,
    "display_type": "table",
    
    "description": "Detailed breakdown of valuation methods and outputs",
    
    "required_calculations": {
      "dcf_intrinsic_value": {
        "method": "damodaran_dcf_full",
        "inputs": [
          "fcff_projection_10Y",
          "terminal_fcff",
          "wacc",
          "terminal_growth_rate"
        ]
      },
      "comparable_company_valuation": {
        "method": "ev_to_ebitda_multiple",
        "inputs": ["sector_peer_multiples", "company_ebitda"]
      },
      "precedent_transaction_valuation": {
        "method": "historical_acquisition_multiples",
        "inputs": ["company_metrics"],
        "required": false
      }
    },
    
    "display_fields": [
      {
        "field_name": "valuation_method",
        "display_as": "text"
      },
      {
        "field_name": "implied_value",
        "display_as": "currency"
      },
      {
        "field_name": "valuation_weight",
        "display_as": "percentage",
        "note": "How we blend methods"
      },
      {
        "field_name": "weighted_intrinsic_value",
        "display_as": "currency",
        "highlight": true
      }
    ],
    
    "narrative_requirements": {
      "must_include": [
        "Why we chose these specific valuation methods",
        "Key assumptions in each method",
        "Why we weight them this way",
        "Sensitivity of DCF to key variables"
      ],
      "length_words": 300
    }
  },
  
  {
    "section_id": "financial_metrics",
    "section_name": "ตัวชี้วัดทางการเงินประวัติศาสตร์ (Historical Financials)",
    "order": 3,
    "display_type": "table",
    
    "required_calculations": [
      "roe",
      "roic",
      "profit_margin",
      "revenue_growth",
      "fcf_margin",
      "debt_to_equity"
    ],
    
    "display_fields": [
      {
        "field_name": "year",
        "display_as": "text"
      },
      {
        "field_name": "revenue",
        "display_as": "currency"
      },
      {
        "field_name": "revenue_growth",
        "display_as": "percentage_delta"
      },
      {
        "field_name": "operating_income",
        "display_as": "currency"
      },
      {
        "field_name": "net_income",
        "display_as": "currency"
      },
      {
        "field_name": "roe",
        "display_as": "percentage"
      },
      {
        "field_name": "roic",
        "display_as": "percentage"
      }
    ],
    
    "chart_references": [
      {
        "chart_id": "revenue_trend",
        "metric": "revenue",
        "chart_type": "line_with_trend"
      },
      {
        "chart_id": "margins_evolution",
        "metrics": ["gross_margin", "operating_margin", "net_margin"],
        "chart_type": "stacked_area"
      }
    ]
  },
  
  {
    "section_id": "why_priced_that_way",
    "section_name": "ทำไมตลาดจึงให้ราคาที่เป็นอย่างนี้ (Market Rationale)",
    "order": 4,
    "display_type": "text",
    
    "description": "Narrative explaining current valuation vs historical and peers",
    
    "required_calculations": [
      "pe_ratio_current",
      "pe_ratio_historical_avg",
      "pe_ratio_sector_avg",
      "forward_pe",
      "peg_ratio"
    ],
    
    "narrative_requirements": {
      "must_include": [
        "Current P/E vs historical: why higher or lower?",
        "Current P/E vs peers: is market pricing growth premium?",
        "Implied growth expectations from current valuation",
        "Market sentiment signals (analyst ratings, insider trading)",
        "What would need to change for re-rating?"
      ],
      "tone": "analytical",
      "length_words": 400
    }
  },
  
  {
    "section_id": "what_must_be_proven",
    "section_name": "สิ่งที่ต้องพิสูจน์ (Bull Case + Bear Case)",
    "order": 5,
    "display_type": "comparison_cards",
    
    "description": "Key assumptions that must hold for thesis to succeed",
    
    "bull_case": {
      "title": "ข้อโต้แย้งแบบขาขึ้น (Bull Case)",
      "narrative_requirements": {
        "must_include": [
          "3-5 reasons stock will outperform",
          "How company can achieve higher margins",
          "Market expansion opportunities",
          "Catalysts in next 12-24 months"
        ],
        "length_words": 250
      }
    },
    
    "bear_case": {
      "title": "ข้อโต้แย้งแบบขาลง (Bear Case)",
      "narrative_requirements": {
        "must_include": [
          "3-5 risks that could break the thesis",
          "Competitive threats",
          "Macro headwinds",
          "Key metrics to watch (if these break, sell)"
        ],
        "length_words": 250
      }
    }
  },
  
  {
    "section_id": "appendix_detailed_metrics",
    "section_name": "ภาคผนวก: รายละเอียดสูตรคำนวณ (Appendix: Detailed Calculations)",
    "order": 99,
    "display_type": "table",
    
    "description": "Transparency: show all calculations with sources",
    
    "required_calculations": [
      "wacc_components",
      "fcff_projection_table",
      "terminal_value_calculation",
      "sensitivity_analysis_table"
    ],
    
    "display_fields": [
      {
        "field_name": "calculation_name",
        "label": "Metric"
      },
      {
        "field_name": "formula",
        "label": "Formula"
      },
      {
        "field_name": "inputs",
        "label": "Inputs Used"
      },
      {
        "field_name": "result",
        "label": "Result"
      },
      {
        "field_name": "source",
        "label": "Data Source & Date"
      }
    ]
  },
  
  {
    "section_id": "sources_citations",
    "section_name": "แหล่งข้อมูล (Sources & Citations)",
    "order": 100,
    "display_type": "list",
    
    "description": "Every number traces back to a source",
    
    "required_fields": [
      {
        "field_name": "source_name",
        "label": "Source"
      },
      {
        "field_name": "url",
        "label": "Link"
      },
      {
        "field_name": "fetch_timestamp",
        "label": "Fetched On"
      },
      {
        "field_name": "data_point",
        "label": "What Data"
      }
    ]
  }
]
```

---

### 4. NARRATIVE CONFIG

Defines how the template generates story-like commentary.

```json
"narrative_config": {
  "language": "th",
  "tone": "professional_analytical",
  
  "generation_mode": "rule_based|ai_assisted|fully_ai",
  
  "rule_based_narratives": {
    "decision_rationale": {
      "if_mos_great_20": "มูลค่าที่แท้จริงสูงกว่าราคาตลาดอย่างน้อย 20% เราจึงเห็นว่านี่เป็นโอกาสที่ดี...",
      "if_mos_gt_0_lt_20": "หุ้นนี้มีมูลค่าที่แท้จริงสูงกว่าราคาตลาดเล็กน้อย จึงเหมาะสำหรับผู้ลงทุนที่...",
      "if_mos_lt_0": "ตามการวิเคราะห์ของเรา ราคาตลาดสูงกว่ามูลค่าที่แท้จริง เราจึง..."
    },
    
    "growth_story": {
      "if_revenue_cagr_gt_15": "บริษัทได้แสดงการเติบโตของรายได้อย่างรวดเร็วที่ {cagr}% ต่อปี...",
      "if_margin_expanding": "มาร์จิ้นกำไรได้ขยายตัวจาก {margin_2020}% เป็น {margin_2025}% ซึ่งบ่งชี้ถึง..."
    },
    
    "risk_assessment": {
      "if_debt_to_equity_high": "บริษัทนี้มี leverage สูง ที่ {de_ratio} ซึ่งเพิ่มความเสี่ยงต่อ...",
      "if_roic_below_wacc": "ROIC ของบริษัทต่ำกว่า WACC ซึ่งหมายความว่า..."
    }
  },
  
  "ai_assisted": {
    "enabled": false,  // Set true if OpenAI integration available
    "model": "gpt-4",
    "max_tokens": 1000,
    "temperature": 0.5,
    "system_prompt_template": "You are a professional stock analyst using Damodaran's methodology. Write in Thai. Be concise, data-driven, and professional. Cite specific numbers. Do not use emoji.",
    "sections_to_generate": [
      "why_priced_that_way",
      "bull_case",
      "bear_case"
    ]
  },
  
  "mandatory_inclusions": {
    "every_narrative_must_have": [
      "Reference to specific calculations (WACC, ROIC, etc.)",
      "Comparison to historical avg or peers",
      "Clear conditions under which thesis changes",
      "Specific metrics to monitor"
    ]
  }
}
```

---

### 5. CHARTS CONFIG

Specifies which metrics get graphed and how.

```json
"charts_config": {
  "available_chart_types": [
    "line_with_trend",
    "waterfall",
    "stacked_area",
    "bar_comparison",
    "scatter_vs_peers",
    "heatmap_sensitivity",
    "histogram_distribution",
    "gauge_vs_target"
  ],
  
  "charts": [
    {
      "chart_id": "revenue_trend",
      "metric": "revenue",
      "label": "รายได้ประวัติศาสตร์ (Historical Revenue)",
      "chart_type": "line_with_trend",
      "data": {
        "x_axis": "year",
        "y_axis": "revenue",
        "lookback_years": 10,
        "include_projection_years": 3
      },
      "styling": {
        "color_scheme": "professional",
        "unit": "millions_USD"
      },
      "interactivity": {
        "hover_shows": ["exact_value", "yoy_change", "margin"],
        "click_drills_to": "detailed_revenue_segment_table"
      }
    },
    
    {
      "chart_id": "valuation_waterfall",
      "metric": "intrinsic_value_components",
      "label": "ประเมินวิธีการคำนวณมูลค่า (DCF Valuation Build-up)",
      "chart_type": "waterfall",
      "data": {
        "components": [
          "projected_fcff_sum",
          "terminal_value",
          "discount_adjustment",
          "net_debt_adjustment",
          "intrinsic_value_per_share"
        ]
      },
      "styling": {
        "positive_color": "green",
        "negative_color": "red",
        "total_color": "blue"
      }
    },
    
    {
      "chart_id": "vs_peers_scatter",
      "metric": "pe_ratio_vs_growth",
      "label": "เทียบเคียงกับสมทบ (Valuation vs Peers)",
      "chart_type": "scatter_vs_peers",
      "data": {
        "x_metric": "revenue_growth_rate",
        "y_metric": "pe_ratio",
        "peer_group": "sector_industry"
      },
      "styling": {
        "highlight_company": "large_blue_dot",
        "peer_averages": "red_line",
        "quadrants": true
      }
    },
    
    {
      "chart_id": "sensitivity_dcf",
      "metric": "dcf_sensitivity_analysis",
      "label": "ความอ่อนไหวของมูลค่าส่วนแบ่ง (DCF Sensitivity: WACC vs Terminal Growth)",
      "chart_type": "heatmap_sensitivity",
      "data": {
        "x_variable": "wacc",
        "x_range": [0.07, 0.10, 0.13],
        "y_variable": "terminal_growth_rate",
        "y_range": [0.02, 0.025, 0.03, 0.035],
        "output_metric": "intrinsic_value_per_share"
      },
      "styling": {
        "color_scale": "red_white_green",
        "show_values": true
      }
    },
    
    {
      "chart_id": "historical_vs_target_price",
      "metric": "intrinsic_vs_market_price",
      "label": "เป้าหมายราคา vs ราคาตลาด (Intrinsic Value vs Market Price History)",
      "chart_type": "line_with_bands",
      "data": {
        "lines": [
          {
            "name": "Intrinsic Value",
            "metric": "intrinsic_value_historical_chart",
            "color": "blue"
          },
          {
            "name": "Current Market Price",
            "metric": "stock_price_history",
            "color": "black"
          }
        ],
        "bands": [
          {
            "name": "Safety Margin (MOS +30%)",
            "upper_value": "intrinsic_value * 0.7",
            "color": "green_transparent"
          }
        ],
        "lookback_years": 5
      }
    }
  ]
}
```

---

### 6. STYLING

Controls look and feel (for PDF, HTML exports).

```json
"styling": {
  "theme": "professional_dark",  // or "light", "minimal"
  
  "colors": {
    "primary": "#1f77b4",
    "accent": "#ff7f0e",
    "positive": "#2ca02c",
    "negative": "#d62728",
    "neutral": "#7f7f7f",
    "background": "#ffffff",
    "text": "#000000"
  },
  
  "typography": {
    "language": "th",
    "font_thai": "Sarabun, Prompt",
    "font_english": "Lato, Roboto",
    "heading_size": 24,
    "body_size": 12
  },
  
  "layout": {
    "page_orientation": "portrait",
    "margins_mm": [15, 15, 15, 15],
    "column_count": 1,
    "section_break": "new_page"  // after each section
  },
  
  "tables": {
    "header_bg": "#1f77b4",
    "header_text": "white",
    "row_striping": true,
    "alternating_row_bg": "#f0f0f0"
  }
}
```

---

## TEMPLATE INSTANCES

Now we show how **specific templates** use this schema.

### Example 1: DAMODARAN_JET Template

```json
{
  "template_id": "damodaran_jet",
  "template_name": "Damodaran Value Analysis (Thai)",
  "language": "th",
  "metadata": { ... (as shown above) ... },
  "data_requirements": { ... (as shown above) ... },
  "sections": [ 
    "decision_card",
    "valuation_summary",
    "financial_metrics",
    "why_priced_that_way",
    "what_must_be_proven",
    "appendix_detailed_metrics",
    "sources_citations"
  ],
  "narrative_config": { ... (uses rule_based + AI for best sections) ... },
  "charts_config": { ... (shows all charts) ... }
}
```

---

### Example 2: BUFFETT_MOAT Template

A simpler, moat-focused style.

```json
{
  "template_id": "buffett_moat",
  "template_name": "Buffett Economic Moat Analysis",
  "language": "en",
  
  "metadata": {
    "description": "Focus on competitive advantages, management quality, and long-term compounding",
    "tags": ["moat", "competitive_advantage", "management"]
  },
  
  "data_requirements": {
    // Simplified vs Damodaran: no terminal value, focus on roic + growth sustainability
    "fundamentals": {
      "annual_income_statement": { "years_required": 10 },  // Longer history
      "annual_cash_flow": { ... }
    },
    "sec_filings": {
      "extract_keywords": [
        "competitive_advantages",
        "moat_sources",
        "market_share",
        "management_tenure",
        "capital_allocation"
      ]
    }
  },
  
  "sections": [
    {
      "section_id": "moat_assessment",
      "section_name": "Competitive Moat Assessment",
      "order": 1,
      "display_type": "scorecard",
      "required_calculations": [
        "roic_vs_wacc_gap",  // Moat strength indicator
        "roic_consistency",  // Moat durability
        "market_share_stability",
        "roe_trend"
      ]
    },
    {
      "section_id": "management_quality",
      "section_name": "Management & Capital Allocation",
      "order": 2
    },
    {
      "section_id": "simple_valuation",
      "section_name": "Fair Value (Simple DCF)",
      "order": 3,
      "required_calculations": [
        "conservative_growth_rate",
        "wacc",
        "simple_dcf_10yr"
      ]
    }
    // Fewer sections, simpler narratives
  ]
}
```

---

### Example 3: TECHNICAL_SWING Template

Price-action focused.

```json
{
  "template_id": "technical_swing",
  "template_name": "Technical Swing Analysis",
  "language": "en",
  
  "data_requirements": {
    "price_data": {
      "frequency": "daily",
      "lookback_years": 2  // Recent history
    },
    "fundamentals": {
      "minimal": true  // Only need latest metrics
    }
  },
  
  "sections": [
    {
      "section_id": "price_pattern",
      "section_name": "Price Pattern Recognition",
      "required_calculations": [
        "support_resistance_levels",
        "moving_averages",
        "rsi",
        "macd"
      ],
      "chart_references": [
        {
          "chart_id": "price_with_ma",
          "chart_type": "candlestick_with_moving_averages"
        }
      ]
    },
    {
      "section_id": "entry_exit_signals",
      "section_name": "Entry/Exit Signals",
      "required_calculations": ["momentum_indicators", "volatility_breakout"]
    }
  ]
}
```

---

### Example 4: SIMPLE_ONE_PAGE Template

For quick analysis.

```json
{
  "template_id": "simple_one_page",
  "template_name": "Quick 1-Page Summary",
  "language": "en",
  
  "metadata": {
    "estimated_build_time_seconds": 5,
    "output_format": ["json", "html"],  // No PDF for this one
    "customization_level": 0  // Fixed, cannot edit
  },
  
  "sections": [
    {
      "section_id": "snapshot",
      "section_name": "Snapshot",
      "display_fields": [
        "ticker",
        "price",
        "pe_ratio",
        "52_week_high_low",
        "dividend_yield"
      ]
    },
    {
      "section_id": "quick_call",
      "section_name": "Call",
      "display_fields": [
        "recommendation",
        "target_price",
        "upside_downside"
      ]
    }
  ]
}
```

---

## DATA FLOW: How a Template Gets Used

```
1. USER REQUEST
   GET /api/v1/analyze/AAPL?template=damodaran_jet

2. SYSTEM LOADS TEMPLATE
   template = load_template("damodaran_jet")

3. DATA FETCHER READS data_requirements
   → Fetch 10 years historical prices
   → Fetch 5 years fundamentals from SEC
   → Fetch current market data (risk-free rate, etc.)
   → All data comes back with SOURCES & TIMESTAMPS

4. CALCULATION ENGINE RUNS
   For each calculation in template.sections:
     → Call calculation function with normalized data
     → Store result + source citation
     → Handle null gracefully

5. TEMPLATE RENDERER
   For each section in template.sections:
     → Gather required calculations
     → Format display_fields per style
     → Generate narrative (rule-based or AI)
     → Render charts
     → Compile into JSON response

6. OUTPUT
   {
     "template_id": "damodaran_jet",
     "ticker": "AAPL",
     "analysis_timestamp": "2026-03-16T14:30:00Z",
     "sections": [
       {
         "section_id": "decision_card",
         "title": "Decision Card",
         "data": { ... },
         "narrative": "Thai text here...",
         "charts": [ ... ]
       }
     ],
     "sources": [
       { "name": "SEC EDGAR", "url": "...", "data_points": [...], "fetch_time": "..." },
       { "name": "Yahoo Finance", "url": "...", ... }
     ]
   }

7. FRONTEND RENDERS
   → PDF export (using PDF library)
   → HTML display
   → Or just return JSON for app to render
```

---

## KEY DESIGN PRINCIPLES

### 1. **Decoupling**: Calculations ≠ Presentation
- Same `calculate_wacc()` used by Damodaran, Buffett, and Technical templates
- Each template chooses which calculations to show and how
- New calculation function = automatically available to all templates

### 2. **Extensibility**: Add New Template = JSON Config
- New template style doesn't require code changes
- Just define new `.json` file with schema
- System automatically loads and runs it

### 3. **Data Reuse**: Fetch Once, Use Everywhere
- Template declares all data needs upfront
- System fetches all data once
- Each calculation reuses cached data
- Reduces API calls massively

### 4. **Source Transparency**: Every Number Has a Link
- Every calculation result stores source
- Output includes full citations
- User can verify or update source if needed

### 5. **Null Safety**: Graceful Degradation
- Template specifies `required: true|false` for each calculation
- If a calculation fails, skip that section or show fallback
- Don't crash, just warn

---

## IMPLEMENTATION CHECKLIST

**Phase 0 (Stability)**: Implement this schema validation + one template loader
**Phase 1 (Engine)**: Build calculation engine to feed all templates
**Phase 2 (Damodaran)**: Implement damodaran_jet template fully
**Phase 3 (Extensibility)**: Add Template Studio UI
**Phase 4 (Growth)**: Add buffett_moat, technical_swing, simple_one_page templates

---

## NEXT STEPS

Once this schema is approved:

1. **Code Patterns** needed:
   - `Template` class (loads from JSON, validates schema)
   - `TemplateRegistry` (manages all loaded templates)
   - `TemplateRenderer` (renders template → output)
   - `CalculationEngine` (pluggable functions for each calc)

2. **Data Models** needed:
   - `AnalysisResult` (structured output)
   - `SourceCitation` (URL + timestamp + data point)
   - `NormalizedMetrics` (standardized column names)

3. **API Changes**:
   - Replace 5 endpoints with single `/api/v1/analyze/{ticker}?template=X`
   - Return fully structured JSON
   - Include sources + timestamp

4. **Frontend Changes**:
   - Template selector dropdown
   - Render sections dynamically based on template
   - Display source citations
   - Clickable charts

---

## QUESTIONS FOR YOU

Before we code:

1. **Schema approval**: Does this structure make sense? Any changes needed?
2. **Narrative generation**: Should we use rule-based (predictable) or AI (better) for Thai narratives initially? (I recommend rule-based first for control)
3. **Template versioning**: If users edit a template, track as new version (e.g. "damodaran_jet_v1.1_user_custom")?
4. **Export formats**: PDF, HTML, JSON only, or also Excel/PowerPoint?
5. **Caching**: Should we cache template definitions in memory or reload from disk each request?

Let me know and we can move to **Phase 0 implementation plan** next.
