"""
Base node implementation for LangGraph-based gait analysis pipeline
All nodes inherit from BaseNode which provides LLM integration
"""
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

import os
from dotenv import load_dotenv
from .graph_state import GraphState, StateManager, PipelineStages

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
logger = logging.getLogger(__name__)

class LLMManager:
    """Manages LLM instances and common operations"""
    
    def __init__(self):
        self.llm = self._create_llm()
    
    def _create_llm(self) -> ChatOpenAI:
        """Create and configure the LLM instance"""
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        return ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.1')),
            api_key=openai_api_key,
            max_retries=3,
            request_timeout=60
        )
    
    def invoke_with_system_prompt(self, 
                                 system_prompt: str, 
                                 user_prompt: str) -> str:
        """Invoke LLM with system and user prompts"""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"LLM invocation failed: {str(e)}")
            raise

# Global LLM manager instance
llm_manager = LLMManager()

class BaseNode(ABC):
    """
    Abstract base class for all LangGraph nodes
    Provides common functionality including LLM integration and error handling
    """
    
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.llm = llm_manager.llm
        self.logger = logging.getLogger(f"{__name__}.{node_name}")
    
    def __call__(self, state: GraphState) -> GraphState:
        """
        Main entry point for node execution
        Handles timing, error catching, and state management
        """
        start_time = time.time()
        
        try:
            # Update stage in state
            state = StateManager.update_stage(state, self.node_name)
            
            self.logger.info(f"Starting {self.node_name} - Session: {state.get('session_id')}")
            
            # Check for existing errors - if error exists, skip and return state as-is
            if StateManager.is_error_state(state):
                self.logger.warning(f"Skipping {self.node_name} due to existing error: {state.get('error', 'Unknown error')}")
                return state
            
            # Execute the node logic safely
            result_state = self.execute(state)
            
            # Ensure we return valid state
            if result_state is None:
                self.logger.error(f"{self.node_name} execute method returned None")
                return StateManager.set_error(
                    state, 
                    f"{self.node_name} execute method returned None", 
                    "node_execution_null"
                )
            
            # Update processing time
            end_time = time.time()
            processing_time = result_state.get("processing_time", 0.0) or 0.0
            result_state["processing_time"] = processing_time + (end_time - start_time)
            
            self.logger.info(f"Completed {self.node_name} - Duration: {end_time - start_time:.2f}s")
            
            return result_state
            
        except Exception as e:
            self.logger.error(f"Error in {self.node_name}: {str(e)}")
            return StateManager.set_error(
                state, 
                f"Error in {self.node_name}: {str(e)}", 
                "node_execution"
            )
    
    @abstractmethod
    def execute(self, state: GraphState) -> GraphState:
        """
        Abstract method that each node must implement
        Contains the core logic of the node
        """
        pass
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this node's LLM interactions
        Override this method to customize the system prompt
        """
        return f"""You are an expert AI assistant specialized in processing gait analysis data.
        
        You are currently executing the '{self.node_name}' step of a 12-stage pipeline that analyzes human walking patterns from IMU sensor data.
        
        Your task is to process the current state information and execute the specific logic required for this step.
        
        Always provide accurate, precise, and actionable outputs based on the input data.
        
        Current stage: {self.node_name}
        """
    
    def invoke_llm(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Invoke LLM with appropriate prompts
        Uses default system prompt if none provided
        """
        if system_prompt is None:
            system_prompt = self.get_system_prompt()
        
        return llm_manager.invoke_with_system_prompt(system_prompt, user_prompt)
    
    def create_llm_prompt(self, state: GraphState, task_description: str) -> str:
        """
        Create a standardized prompt for LLM interaction
        Includes current state context and specific task
        """
        prompt = f"""
        Current State Information:
        - Session ID: {state.get('session_id')}
        - Stage: {state.get('stage')}
        - Date: {state.get('date')}
        - Height: {state.get('height_cm')} cm
        
        Task: {task_description}
        
        State Details:
        """
        
        # Add relevant state fields based on current stage
        stage = state.get('stage')
        if stage in [PipelineStages.BUILD_QUERY, PipelineStages.FETCH_CSV]:
            prompt += f"- SQL Query: {state.get('sql', 'Not set')}\n"
        
        if stage in [PipelineStages.FILTER_DATA, PipelineStages.PREDICT_PHASES]:
            prompt += f"- Raw CSV Path: {state.get('raw_csv_path', 'Not set')}\n"
            prompt += f"- Filtered CSV Path: {state.get('filtered_csv_path', 'Not set')}\n"
        
        if stage in [PipelineStages.PREDICT_STRIDE, PipelineStages.CALC_METRICS]:
            prompt += f"- Labels CSV Path: {state.get('labels_csv_path', 'Not set')}\n"
            stride_results = state.get('stride_results') or []
            prompt += f"- Stride Results Count: {len(stride_results)}\n"
        
        if stage in [PipelineStages.STORE_METRICS, PipelineStages.COMPOSE_PROMPT]:
            gait_metrics = state.get('gait_metrics') or {}
            prompt += f"- Gait Metrics: {len(gait_metrics)} metrics calculated\n"
        
        if stage in [PipelineStages.RAG_DIAGNOSIS, PipelineStages.STORE_DIAGNOSIS]:
            prompt_str = state.get('prompt_str') or ''
            prompt += f"- Prompt String Length: {len(prompt_str)}\n"
            prompt += f"- Medical Diagnosis: {'Present' if state.get('medical_diagnosis') else 'Not set'}\n"
        
        return prompt
    
    def validate_state_requirements(self, state: GraphState, required_fields: list) -> bool:
        """
        Validate that required fields are present in state
        Returns True if all required fields are present and non-empty
        """
        for field in required_fields:
            value = state.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                self.logger.error(f"Required field '{field}' is missing or empty")
                return False
        return True 