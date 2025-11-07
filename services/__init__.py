"""
Services Package
"""

from .receptionist import AIReceptionist
from .topic_controller import TopicController
from .response_selector import ResponseSelector

# Backward compatibility alias
ReceptionistService = AIReceptionist

__all__ = [
    'AIReceptionist',
    'ReceptionistService',  # Starý název pro kompatibilitu
    'TopicController',
    'ResponseSelector'
]