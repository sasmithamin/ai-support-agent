"""Agents module exports"""
from src.agents.support_agent import get_support_agent
from src.agents.sentiment_agent import get_sentiment_agent
from src.agents.escalation_agent import get_escalation_agent

__all__ = [
    'get_support_agent',
    'get_sentiment_agent',
    'get_escalation_agent'
]