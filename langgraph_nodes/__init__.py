"""
LangGraph nodes package for gait analysis pipeline

This package contains all the nodes used in the LangGraph-based
gait analysis workflow, including data processing, AI models,
metrics calculation, and error handling.
"""

from .base_node import BaseNode
from .graph_state import GraphState, StateManager, PipelineStages
from .error_handlers import (
    ErrorHandlerNode, 
    NoDataHandlerNode,
    should_go_to_error_handler,
    should_go_to_no_data_handler
)
from .data_processing_nodes import ReceiveRequestNode, FileMetadataNode, DownloadCsvNode, FilterDataNode
from .ai_model_nodes import PredictPhasesNode, PredictStrideNode
from .metrics_nodes import CalcMetricsNode, StoreMetricsNode
from .rag_diagnosis_nodes import ComposePromptNode, RagDiagnosisNode, StoreDiagnosisNode
from .response_nodes import FormatResponseNode, ErrorHandlerNode, NoDataHandlerNode

__all__ = [
    "BaseNode",
    "GraphState",
    "StateManager",
    "PipelineStages",
    
    # Conditional functions
    "should_go_to_error_handler",
    "should_go_to_no_data_handler",
    
    # Data processing nodes
    "ReceiveRequestNode",
    "BuildQueryNode",
    "FetchCsvNode",
    "FilterDataNode",
    
    # AI model nodes
    "PredictPhasesNode",
    "PredictStrideNode",
    
    # Metrics nodes
    "CalcMetricsNode",
    "StoreMetricsNode",
    
    # RAG and diagnosis nodes
    "ComposePromptNode",
    "RagDiagnosisNode",
    "StoreDiagnosisNode",
    "FormatResponseNode",
    
    # Response and error handler nodes
    "ErrorHandlerNode",
    "NoDataHandlerNode"
]

__version__ = "1.0.0" 