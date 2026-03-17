"""
Core Calculation Engine for Stock Analysis

This module contains all calculation functions (WACC, DCF, ROI, etc.)
that are shared across all analysis templates.

Every calculation:
- Takes normalized data as input
- Returns result + source metadata
- Handles null values gracefully
- Documents assumptions
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CalculationResult:
    """Result of any calculation with metadata"""
    value: Optional[float]
    formula: str
    inputs: Dict[str, any]
    source: str
    fetch_timestamp: str
    error: Optional[str] = None
    
    def to_dict(self):
        return {
            "value": self.value,
            "formula": self.formula,
            "inputs": self.inputs,
            "source": self.source,
            "fetch_timestamp": self.fetch_timestamp,
            "error": self.error
        }


class CalculationEngine:
    """Central calculation engine for all valuation methods"""
    
    def __init__(self, data_store: Dict):
        """
        Initialize calculation engine with normalized data.
        
        Args:
            data_store: Dict containing all required financial data
        """
        self.data = data_store
        self.timestamp = datetime.utcnow().isoformat()
    
    # ============================================================================
    # CORE FINANCIAL METRICS
    # ============================================================================
    
    def calculate_wacc(self,
                      cost_of_equity: float,
                      cost_of_debt: float,
                      market_cap: float,
                      total_debt: float,
                      tax_rate: float) -> CalculationResult:
        """
        Calculate Weighted Average Cost of Capital (WACC).
        
        Formula: WACC = (E/V × Re) + (D/V × Rd × (1 - Tc))
        where:
          E = market value of equity
          D = market value of debt
          V = E + D (total value)
          Re = cost of equity
          Rd = cost of debt
          Tc = corporate tax rate
        """
        try:
            E = market_cap
            D = total_debt
            V = E + D
            
            if V == 0:
                return CalculationResult(
                    value=None,
                    formula="WACC = (E/V × Re) + (D/V × Rd × (1 - Tc))",
                    inputs={"market_cap": market_cap, "total_debt": total_debt, "V_total": V},
                    source="internal_calculation",
                    fetch_timestamp=self.timestamp,
                    error="Total value (E+D) is zero"
                )
            
            weight_equity = E / V
            weight_debt = D / V
            
            wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt * (1 - tax_rate))
            
            return CalculationResult(
                value=wacc,
                formula="WACC = (E/V × Re) + (D/V × Rd × (1 - Tc))",
                inputs={
                    "cost_of_equity": cost_of_equity,
                    "cost_of_debt": cost_of_debt,
                    "market_cap": market_cap,
                    "total_debt": total_debt,
                    "tax_rate": tax_rate,
                    "weight_equity": weight_equity,
                    "weight_debt": weight_debt
                },
                source="Damodaran methodology",
                fetch_timestamp=self.timestamp
            )
        except Exception as e:
            return CalculationResult(
                value=None,
                formula="WACC = (E/V × Re) + (D/V × Rd × (1 - Tc))",
                inputs={},
                source="internal_calculation",
                fetch_timestamp=self.timestamp,
                error=str(e)
            )
    
    def calculate_roe(self, net_income: float, shareholders_equity: float) -> CalculationResult:
        """
        Calculate Return on Equity (ROE).
        
        Formula: ROE = Net Income / Shareholders' Equity
        """
        try:
            if shareholders_equity is None or shareholders_equity <= 0:
                return CalculationResult(
                    value=None,
                    formula="ROE = Net Income / Shareholders' Equity",
                    inputs={"net_income": net_income, "equity": shareholders_equity},
                    source="internal_calculation",
                    fetch_timestamp=self.timestamp,
                    error="Shareholders' equity is zero or negative"
                )
            
            roe = net_income / shareholders_equity
            
            return CalculationResult(
                value=roe,
                formula="ROE = Net Income / Shareholders' Equity",
                inputs={"net_income": net_income, "shareholders_equity": shareholders_equity},
                source="fundamental_analysis",
                fetch_timestamp=self.timestamp
            )
        except Exception as e:
            return CalculationResult(
                value=None,
                formula="ROE = Net Income / Shareholders' Equity",
                inputs={},
                source="internal_calculation",
                fetch_timestamp=self.timestamp,
                error=str(e)
            )
    
    def calculate_roic(self,
                      nopat: float,
                      invested_capital: float) -> CalculationResult:
        """
        Calculate Return on Invested Capital (ROIC).
        
        Formula: ROIC = NOPAT / Invested Capital
        where NOPAT = EBIT × (1 - Tax Rate)
        """
        try:
            if invested_capital is None or invested_capital <= 0:
                return CalculationResult(
                    value=None,
                    formula="ROIC = NOPAT / Invested Capital",
                    inputs={"nopat": nopat, "invested_capital": invested_capital},
                    source="internal_calculation",
                    fetch_timestamp=self.timestamp,
                    error="Invested capital is zero or negative"
                )
            
            roic = nopat / invested_capital
            
            return CalculationResult(
                value=roic,
                formula="ROIC = NOPAT / Invested Capital",
                inputs={"nopat": nopat, "invested_capital": invested_capital},
                source="Damodaran framework",
                fetch_timestamp=self.timestamp
            )
        except Exception as e:
            return CalculationResult(
                value=None,
                formula="ROIC = NOPAT / Invested Capital",
                inputs={},
                source="internal_calculation",
                fetch_timestamp=self.timestamp,
                error=str(e)
            )
    
    # ============================================================================
    # VALUATION METHODS
    # ============================================================================
    
    def calculate_dcf_intrinsic_value(self,
                                     fcff_projections: List[float],
                                     terminal_fcff: float,
                                     wacc: float,
                                     terminal_growth_rate: float,
                                     shares_outstanding: float) -> CalculationResult:
        """
        Calculate intrinsic value using Discounted Cash Flow (DCF) method.
        
        Formula:
        Intrinsic Value = Σ(FCFF_t / (1+WACC)^t) + (Terminal FCFF / ((WACC - g) × (1+WACC)^n))
        Per Share = Enterprise Value / Shares Outstanding
        """
        try:
            if wacc is None or wacc <= terminal_growth_rate or shares_outstanding is None:
                return CalculationResult(
                    value=None,
                    formula="PV of projected FCFFs + PV of terminal value",
                    inputs={"fcff_projections": fcff_projections, "terminal_fcff": terminal_fcff, "wacc": wacc, "terminal_growth": terminal_growth_rate},
                    source="DCF_analysis",
                    fetch_timestamp=self.timestamp,
                    error="Invalid inputs: WACC must be > terminal_growth_rate and shares_outstanding > 0"
                )
            
            # Present value of projected FCFFs
            pv_fcff = 0
            for i, fcff in enumerate(fcff_projections):
                if fcff is not None:
                    pv_fcff += fcff / ((1 + wacc) ** (i + 1))
            
            # Terminal value
            terminal_value = (terminal_fcff * (1 + terminal_growth_rate)) / (wacc - terminal_growth_rate)
            pv_terminal_value = terminal_value / ((1 + wacc) ** len(fcff_projections))
            
            # Enterprise value
            enterprise_value = pv_fcff + pv_terminal_value
            
            # Intrinsic value per share
            intrinsic_value_per_share = enterprise_value / shares_outstanding
            
            return CalculationResult(
                value=intrinsic_value_per_share,
                formula="DCF: PV(FCFF) + PV(Terminal Value) / Shares Outstanding",
                inputs={
                    "pv_fcff": pv_fcff,
                    "pv_terminal_value": pv_terminal_value,
                    "enterprise_value": enterprise_value,
                    "shares_outstanding": shares_outstanding,
                    "wacc": wacc,
                    "terminal_growth_rate": terminal_growth_rate
                },
                source="Damodaran DCF methodology",
                fetch_timestamp=self.timestamp
            )
        except Exception as e:
            return CalculationResult(
                value=None,
                formula="DCF methodology",
                inputs={},
                source="DCF_calculation",
                fetch_timestamp=self.timestamp,
                error=str(e)
            )
    
    def calculate_margin_of_safety(self,
                                  intrinsic_value: float,
                                  current_price: float) -> CalculationResult:
        """
        Calculate Margin of Safety (MOS).
        
        Formula: MOS = (Intrinsic Value - Current Price) / Intrinsic Value
        """
        try:
            if intrinsic_value is None or intrinsic_value <= 0:
                return CalculationResult(
                    value=None,
                    formula="MOS = (Intrinsic Value - Current Price) / Intrinsic Value",
                    inputs={"intrinsic_value": intrinsic_value, "current_price": current_price},
                    source="value_investing",
                    fetch_timestamp=self.timestamp,
                    error="Intrinsic value is zero or negative"
                )
            
            mos = (intrinsic_value - current_price) / intrinsic_value
            upside_downside = (intrinsic_value - current_price) / current_price if current_price > 0 else None
            
            return CalculationResult(
                value=mos,
                formula="MOS = (Intrinsic Value - Current Price) / Intrinsic Value",
                inputs={
                    "intrinsic_value": intrinsic_value,
                    "current_price": current_price,
                    "upside_downside_percent": upside_downside
                },
                source="Value investing framework",
                fetch_timestamp=self.timestamp
            )
        except Exception as e:
            return CalculationResult(
                value=None,
                formula="MOS calculation",
                inputs={},
                source="value_investing",
                fetch_timestamp=self.timestamp,
                error=str(e)
            )
    
    # ============================================================================
    # MULTIPLES & COMPARISONS
    # ============================================================================
    
    def calculate_pe_ratio(self, current_price: float, eps: float) -> CalculationResult:
        """Calculate Price-to-Earnings (P/E) ratio"""
        try:
            if eps is None or eps <= 0:
                return CalculationResult(
                    value=None,
                    formula="P/E = Current Price / EPS",
                    inputs={"price": current_price, "eps": eps},
                    source="market_data",
                    fetch_timestamp=self.timestamp,
                    error="EPS is zero or negative"
                )
            
            pe = current_price / eps
            
            return CalculationResult(
                value=pe,
                formula="P/E = Current Price / EPS",
                inputs={"current_price": current_price, "eps": eps},
                source="market_metrics",
                fetch_timestamp=self.timestamp
            )
        except Exception as e:
            return CalculationResult(
                value=None,
                formula="P/E ratio",
                inputs={},
                source="market_data",
                fetch_timestamp=self.timestamp,
                error=str(e)
            )
    
    def calculate_volatility(self, returns: List[float]) -> CalculationResult:
        """
        Calculate annualized volatility from daily returns.
        
        Formula: Volatility = StdDev(daily_returns) × √252
        """
        try:
            if not returns or len(returns) < 2:
                return CalculationResult(
                    value=None,
                    formula="Volatility = StdDev(returns) × √252",
                    inputs={"return_count": len(returns) if returns else 0},
                    source="technical_analysis",
                    fetch_timestamp=self.timestamp,
                    error="Insufficient return data (need at least 2 data points)"
                )
            
            returns_array = np.array([r for r in returns if r is not None and not np.isnan(r)])
            
            if len(returns_array) < 2:
                return CalculationResult(
                    value=None,
                    formula="Volatility = StdDev(returns) × √252",
                    inputs={"valid_returns": len(returns_array)},
                    source="technical_analysis",
                    fetch_timestamp=self.timestamp,
                    error="Insufficient valid return data"
                )
            
            daily_volatility = np.std(returns_array)
            annualized_volatility = daily_volatility * np.sqrt(252)
            
            return CalculationResult(
                value=annualized_volatility,
                formula="Volatility = StdDev(daily_returns) × √252",
                inputs={
                    "daily_volatility": daily_volatility,
                    "data_points": len(returns_array)
                },
                source="statistical_analysis",
                fetch_timestamp=self.timestamp
            )
        except Exception as e:
            return CalculationResult(
                value=None,
                formula="Volatility calculation",
                inputs={},
                source="technical_analysis",
                fetch_timestamp=self.timestamp,
                error=str(e)
            )
    
    def calculate_sharpe_ratio(self,
                             returns: List[float],
                             risk_free_rate: float) -> CalculationResult:
        """
        Calculate Sharpe Ratio (risk-adjusted return).
        
        Formula: Sharpe = (Return - Risk-Free Rate) / Volatility
        """
        try:
            # Calculate volatility
            vol_result = self.calculate_volatility(returns)
            if vol_result.value is None:
                return CalculationResult(
                    value=None,
                    formula="Sharpe = (Return - RFR) / Volatility",
                    inputs={},
                    source="risk_metrics",
                    fetch_timestamp=self.timestamp,
                    error="Cannot calculate volatility for Sharpe ratio"
                )
            
            # Calculate average return
            valid_returns = [r for r in returns if r is not None and not np.isnan(r)]
            avg_return = np.mean(valid_returns) * 252  # Annualize
            
            volatility = vol_result.value
            
            if volatility == 0:
                return CalculationResult(
                    value=None,
                    formula="Sharpe = (Return - RFR) / Volatility",
                    inputs={"return": avg_return, "rfr": risk_free_rate, "volatility": volatility},
                    source="risk_metrics",
                    fetch_timestamp=self.timestamp,
                    error="Volatility is zero (division by zero)"
                )
            
            sharpe = (avg_return - risk_free_rate) / volatility
            
            return CalculationResult(
                value=sharpe,
                formula="Sharpe = (Annualized Return - RFR) / Annualized Volatility",
                inputs={
                    "annualized_return": avg_return,
                    "risk_free_rate": risk_free_rate,
                    "annualized_volatility": volatility
                },
                source="Sharpe ratio framework",
                fetch_timestamp=self.timestamp
            )
        except Exception as e:
            return CalculationResult(
                value=None,
                formula="Sharpe ratio",
                inputs={},
                source="risk_metrics",
                fetch_timestamp=self.timestamp,
                error=str(e)
            )
