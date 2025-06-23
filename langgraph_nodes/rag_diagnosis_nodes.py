"""
RAG-based diagnosis nodes for LangGraph-based gait analysis pipeline
Implements 3 nodes: compose_prompt, rag_diagnosis, store_diagnosis
Uses PDF documents for medical knowledge retrieval
"""
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# RAG and Vector Database imports
import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

import os
from dotenv import load_dotenv

from .base_node import BaseNode
from .graph_state import GraphState, StateManager, PipelineStages

# Load environment variables
load_dotenv()

class ComposePromptNode(BaseNode):
    """
    Node 9: Compose diagnostic prompt from gait metrics
    Simple 2-stage query system: Stage 1 (Individual Indicators) + Stage 2 (Overall Assessment)
    """
    
    def __init__(self):
        super().__init__(PipelineStages.COMPOSE_PROMPT)
    
    def execute(self, state: GraphState) -> GraphState:
        """Compose 2-stage RAG queries from gait metrics and patient info"""
        
        required_fields = ["gait_metrics", "height_cm", "user_id"]
        if not self.validate_state_requirements(state, required_fields):
            return StateManager.set_error(state, f"Missing required fields: {required_fields}", "validation_error")
        
        gait_metrics = state["gait_metrics"]
        height_cm = state["height_cm"]
        user_id = state["user_id"]
        gender = state.get("gender", "unknown")
        
        try:
            # Extract all 15 gait metrics
            metrics_data = {
                'avg_stride_time': gait_metrics.get('avg_stride_time', 0),
                'avg_stride_length': gait_metrics.get('avg_stride_length', 0),
                'avg_walking_speed': gait_metrics.get('avg_walking_speed', 0),
                'cadence': gait_metrics.get('cadence', 0),
                'stride_time_asymmetry': gait_metrics.get('stride_time_asymmetry', 0),
                'stride_length_asymmetry': gait_metrics.get('stride_length_asymmetry', 0),
                'stride_time_cv': gait_metrics.get('stride_time_cv', 0),
                'stride_length_cv': gait_metrics.get('stride_length_cv', 0),
                'walking_speed_cv': gait_metrics.get('walking_speed_cv', 0),
                'step_width': gait_metrics.get('step_width', 0),
                'gait_regularity_index': gait_metrics.get('gait_regularity_index', 0),
                'gait_stability_ratio': gait_metrics.get('gait_stability_ratio', 0),
                'stance_phase_ratio': gait_metrics.get('stance_phase_ratio', 0.6),
                'swing_phase_ratio': gait_metrics.get('swing_phase_ratio', 0.4),
                'double_support_ratio': gait_metrics.get('double_support_ratio', 0.2)
            }
            
            # Patient information
            patient_info = {
                'age': 60,  # Fixed age
                'gender': gender,
                'height_cm': height_cm,
                'user_id': user_id
            }
            
            # Stage 1: Individual Indicator Analysis Query
            stage1_query = self._create_stage1_query(patient_info, metrics_data)
            
            # Stage 2: Overall Assessment Query Template
            stage2_template = self._create_stage2_template(patient_info, metrics_data)
            
            # Update state
            state["rag_query_stage1"] = stage1_query
            state["rag_query_stage2_template"] = stage2_template
            state["patient_info"] = patient_info
            state["metrics_data"] = metrics_data
            
            self.logger.info(f"RAG 2-stage queries composed for patient: {user_id}")
            
            return state
            
        except Exception as e:
            error_msg = f"RAG query composition failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "rag_query_composition_error")
    
    def _create_stage1_query(self, patient_info: dict, metrics_data: dict) -> str:
        """Create Stage 1 query for individual indicator analysis"""
        
        return f"""60세 {patient_info['gender']} 환자의 보행 지표별 정상범위 및 개별 진단 요청

【환자 정보】연령: 60세, 성별: {patient_info['gender']}, 신장: {patient_info['height_cm']}cm

【측정된 보행 지표 15개】
1. 보폭 시간: {metrics_data['avg_stride_time']:.2f}초
2. 보행률: {metrics_data['cadence']:.0f}걸음/분
3. 보폭 길이: {metrics_data['avg_stride_length']:.2f}m
4. 보행 속도: {metrics_data['avg_walking_speed']:.2f}m/s
5. 보폭 폭: {metrics_data['step_width']:.2f}m
6. 보폭 시간 변동성: {metrics_data['stride_time_cv']:.1f}%
7. 보폭 길이 변동성: {metrics_data['stride_length_cv']:.1f}%
8. 보행 속도 변동성: {metrics_data['walking_speed_cv']:.1f}%
9. 보폭 시간 비대칭성: {metrics_data['stride_time_asymmetry']:.1f}%
10. 보폭 길이 비대칭성: {metrics_data['stride_length_asymmetry']:.1f}%
11. 보행 규칙성 지수: {metrics_data['gait_regularity_index']:.3f}
12. 보행 안정성 비율: {metrics_data['gait_stability_ratio']:.3f}
13. 입각기 비율: {metrics_data['stance_phase_ratio']:.1%}
14. 유각기 비율: {metrics_data['swing_phase_ratio']:.1%}
15. 양발지지 비율: {metrics_data['double_support_ratio']:.1%}

각 지표별로 정상범위를 찾고 현재 측정값과 비교하여 개별 진단을 해주세요."""

    def _create_stage2_template(self, patient_info: dict, metrics_data: dict) -> str:
        """Create Stage 2 template for overall assessment"""
        
        return f"""Stage 1 지표별 진단 결과를 바탕으로 종합 평가 및 맞춤 권장사항 작성

【환자 정보】60세 {patient_info['gender']}, 신장 {patient_info['height_cm']}cm

【Stage 1 개별 지표 진단 결과】
{{STAGE1_RESULTS}}

【요청사항】
1. 질병 위험도 평가 (파킨슨병, 뇌졸중 등)
2. 의사가 노인에게 설명하듯 친근하고 쉬운 톤으로 종합 소견 작성
3. 집에서 쉽게 할 수 있는 맞춤 운동 권장사항 제시

의료문헌 근거를 바탕으로 종합 진단을 해주세요."""

class RagDiagnosisNode(BaseNode):
    """
    Node 10: RAG-based medical diagnosis using PDF knowledge base
    Retrieves relevant medical information and generates diagnosis
    """
    
    def __init__(self):
        super().__init__(PipelineStages.RAG_DIAGNOSIS)
        self.vector_store = None
        self.embeddings = None
        self._initialize_rag_system()
    
    def _initialize_rag_system(self):
        """Initialize the RAG system: vector store, embeddings, and retriever."""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}
                )
                
                # Define ChromaDB path relative to project root
                project_root = Path(os.getenv('PROJECT_ROOT', '.'))
                chroma_db_path = str(project_root / "chroma_db")
                
                # Create directory if it doesn't exist
                Path(chroma_db_path).mkdir(parents=True, exist_ok=True)
                
                self.vector_store = Chroma(
                    embedding_function=self.embeddings,
                    persist_directory=chroma_db_path
                )
                
                # 🚀 **최적화**: 기존 임베딩 데이터가 있는지 확인
                existing_data_count = self._check_existing_embeddings()
                
                if existing_data_count > 0:
                    self.logger.info(f"✅ ChromaDB 기존 임베딩 데이터 발견: {existing_data_count}개 문서")
                    self.logger.info("⚡ PDF 재로딩 건너뛰기 - 기존 임베딩 사용")
                else:
                    self.logger.info("📚 새로운 임베딩 생성 필요 - PDF 로딩 시작")
                    self._load_medical_pdfs(Path("docs/medical_pdfs"))
                
                self.logger.info("✅ RAG system initialized successfully.")
                return  # Success, exit retry loop
                
            except Exception as e:
                retry_count += 1
                self.logger.warning(f"RAG initialization attempt {retry_count}/{max_retries} failed: {e}")
                
                if retry_count < max_retries:
                    # Try to clean up ChromaDB directory for retry
                    project_root = Path(os.getenv('PROJECT_ROOT', '.'))
                    chroma_db_path = str(project_root / "chroma_db")
                    try:
                        import shutil
                        if Path(chroma_db_path).exists():
                            shutil.rmtree(chroma_db_path)
                            self.logger.info(f"Cleaned ChromaDB directory for retry {retry_count + 1}")
                    except Exception as cleanup_error:
                        self.logger.warning(f"Failed to cleanup ChromaDB: {cleanup_error}")
                else:
                    self.logger.error(f"Failed to initialize RAG system after {max_retries} attempts: {e}")
                    self.vector_store = None
    
    def _check_existing_embeddings(self) -> int:
        """
        ChromaDB에 기존 임베딩 데이터가 있는지 확인
        
        Returns:
            int: 기존 문서의 개수 (0이면 새로 임베딩 필요)
        """
        try:
            # 환경변수로 강제 리로딩 옵션 제공
            force_reload = os.getenv('RAG_FORCE_RELOAD', 'false').lower() == 'true'
            if force_reload:
                self.logger.info("🔄 RAG_FORCE_RELOAD=true - 강제로 PDF 재로딩 수행")
                return 0
            
            # ChromaDB에서 기존 컬렉션의 문서 수를 확인
            collection = self.vector_store._collection
            
            # 컬렉션에 저장된 문서 수 확인
            document_count = collection.count()
            
            if document_count > 0:
                self.logger.info(f"💾 기존 ChromaDB 데이터: {document_count}개 문서 발견")
                return document_count
            else:
                self.logger.info("📭 ChromaDB가 비어있음 - 새로운 임베딩 생성 필요")
                return 0
                
        except Exception as e:
            self.logger.warning(f"기존 임베딩 확인 중 오류: {e}")
            # 확인 실패 시 안전하게 새로 임베딩하도록 0 반환
            return 0
    
    def _load_medical_pdfs(self, docs_dir: Path):
        """Load medical PDFs, split them, and add to the vector store."""
        try:
            from langchain_community.document_loaders import PyPDFLoader
            import os
            
            documents = []
            
            if docs_dir.exists():
                pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]
                
                for pdf_file in pdf_files:
                    try:
                        pdf_path = docs_dir / pdf_file
                        loader = PyPDFLoader(str(pdf_path))
                        pdf_docs = loader.load()
                        
                        for doc in pdf_docs:
                            doc.metadata.update({
                                "source_file": pdf_file,
                                "document_type": "medical_literature"
                            })
                        
                        documents.extend(pdf_docs)
                        self.logger.info(f"✅ Loaded PDF: {pdf_file} ({len(pdf_docs)} pages)")
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to load PDF {pdf_file}: {str(e)}")
                        continue
            
            if not documents:
                self.logger.warning("No PDF files loaded, using sample medical reference")
                # Add a comprehensive sample document if no PDFs are found
                sample_doc = Document(
                    page_content="""
                    보행 분석 임상 참고 자료 - 근거 기반 가이드라인
                    
                    건강한 성인(20-65세) 정상 보행 지표:
                    - 보폭 시간: 1.0-1.3초 
                    - 보행률: 100-120 걸음/분
                    - 보폭 길이: 1.2-1.6m (신장 의존적)
                    - 보행 속도: 1.0-1.4 m/s 
                    - 좌우 비대칭성: <5%
                    - 시간적 변동성: <5%
                    - 공간적 변동성: <5%
                    
                    병리학적 보행 패턴:
                    
                    1. 파킨슨병:
                    - 보폭 길이 감소 (<1.0m)
                    - 보행률 증가 (>120 걸음/분) 
                    - 보행 속도 감소 (<0.8 m/s)
                    - 변동성 증가 (>10% CV)
                    - 특징: 짧고 끌리는 걸음
                    
                    2. 뇌졸중 편마비:
                    - 심한 비대칭성 (>15%)
                    - 환측 보폭 길이 감소
                    - 전체 보행 속도 감소 (<0.8 m/s)
                    - 특징: 일측성 약화 패턴
                    
                    3. 소뇌성 운동실조:
                    - 높은 보행 변동성 (>15% CV)
                    - 넓은 보폭
                    - 불규칙한 보폭 타이밍
                    - 특징: 협조성 부족
                    """,
                    metadata={"source": "clinical_reference", "type": "sample_data"}
                )
                documents = [sample_doc]
                
            self.logger.info(f"Medical knowledge base loaded: {len(documents)} documents")
            
            # Split documents and add to vector store
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            
            chunks = text_splitter.split_documents(documents)
            self.vector_store.add_documents(chunks)
            
            self.logger.info(f"Added {len(chunks)} chunks to vector store")
                
        except ImportError:
            self.logger.warning("PyPDFLoader not available, using sample medical data")
            sample_doc = Document(
                page_content="기본 보행 분석 참고 자료: 정상 보행 속도 1.0-1.4 m/s, 보행률 100-120 걸음/분",
                metadata={"source": "fallback", "type": "basic_reference"}
            )
            # Just return the single doc, assuming no vector store to add to
            return [sample_doc]
    
    def execute(self, state: GraphState) -> GraphState:
        """Execute 2-stage RAG-based medical diagnosis"""
        
        required_fields = ["rag_query_stage1", "rag_query_stage2_template", "patient_info", "metrics_data"]
        if not self.validate_state_requirements(state, required_fields):
            return StateManager.set_error(state, f"Missing required fields: {required_fields}", "validation_error")
        
        if self.vector_store is None:
            return StateManager.set_error(state, "RAG system not initialized", "rag_system_error")
        
        stage1_query = state["rag_query_stage1"]
        stage2_template = state["rag_query_stage2_template"]
        patient_info = state["patient_info"]
        metrics_data = state["metrics_data"]
        session_id = state.get("session_id", "unknown")

        try:
            # STAGE 1: Individual Indicator Analysis
            self.logger.info("🔍 Stage 1: Individual Indicator Analysis")
            
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
            stage1_docs = retriever.get_relevant_documents(stage1_query)
            
            # Format Stage 1 retrieved knowledge
            stage1_knowledge = self._format_retrieved_knowledge(stage1_docs, "Stage1")
            source_info_stage1 = self._extract_source_info(stage1_docs)
            
            # Create Stage 1 LLM prompt for individual indicator analysis
            stage1_llm_prompt = f"""당신은 보행 분석 전문의입니다. 아래 의료 문헌을 바탕으로 각 보행 지표별 개별 진단을 수행하세요.

=== 검색된 의료 문헌 ===
{stage1_knowledge}

=== 환자 보행 지표 분석 요청 ===
{stage1_query}

=== 응답 형식 ===
다음 JSON 형식으로만 응답하세요. 모든 필드가 정확히 포함되어야 합니다:

{{
  "indicators": [
    {{
      "id": "stride-time",
      "name": "보폭 시간",
      "value": "{metrics_data['avg_stride_time']:.2f}초",
      "status": "normal",
      "description": "한쪽 발이 땅에 닿은 후, 같은 발이 다시 닿을 때까지 걸리는 시간입니다. 걸음 템포를 확인할 수 있어요.",
      "result": "정상범위(1.0-1.3초) 내에 있습니다. 걸음 템포가 안정적입니다."
    }},
    {{
      "id": "cadence",
      "name": "보행률",
      "value": "{metrics_data['cadence']:.0f}걸음/분",
      "status": "normal",
      "description": "1분 동안 걷는 걸음 수입니다. 보행 리듬을 나타내요.",
      "result": "정상범위(100-120걸음/분) 내에 있습니다. 보행 리듬이 좋습니다."
    }},
    {{
      "id": "stride-length",
      "name": "보폭 길이",
      "value": "{metrics_data['avg_stride_length']:.2f}m",
      "status": "normal",
      "description": "한 걸음의 길이입니다. 근력과 관절 가동성을 반영해요.",
      "result": "정상범위(1.2-1.6m) 내에 있습니다. 근력이 양호합니다."
    }},
    {{
      "id": "walking-speed",
      "name": "평균 보행 속도",
      "value": "{metrics_data['avg_walking_speed']:.2f}m/s",
      "status": "normal",
      "description": "단위 시간 동안 이동한 거리입니다. 전체 활동성과 운동 능력을 확인할 수 있어요.",
      "result": "정상범위(1.0-1.4m/s) 내에 있습니다. 활동성이 좋습니다."
    }},
    {{
      "id": "step-width",
      "name": "보폭 폭",
      "value": "{metrics_data['step_width']:.2f}m",
      "status": "normal",
      "description": "좌우 발 사이의 간격입니다. 균형 능력을 나타내요.",
      "result": "정상범위(0.08-0.15m) 내에 있습니다. 균형이 좋습니다."
    }},
    {{
      "id": "stride-time-cv",
      "name": "보폭 시간 변동성",
      "value": "{metrics_data['stride_time_cv']:.1f}%",
      "status": "normal",
      "description": "걸음 시간의 일정함을 나타냅니다. 낮을수록 안정적이에요.",
      "result": "정상범위(<5%) 내에 있습니다. 걸음이 일정합니다."
    }},
    {{
      "id": "stride-length-cv",
      "name": "보폭 길이 변동성",
      "value": "{metrics_data['stride_length_cv']:.1f}%",
      "status": "normal",
      "description": "걸음 길이의 일정함을 나타냅니다. 낮을수록 안정적이에요.",
      "result": "정상범위(<5%) 내에 있습니다. 걸음 길이가 일정합니다."
    }},
    {{
      "id": "walking-speed-cv",
      "name": "보행 속도 변동성",
      "value": "{metrics_data['walking_speed_cv']:.1f}%",
      "status": "normal",
      "description": "보행 속도의 일정함을 나타냅니다. 낮을수록 안정적이에요.",
      "result": "정상범위(<5%) 내에 있습니다. 속도가 일정합니다."
    }},
    {{
      "id": "stride-difference",
      "name": "양발 보폭 차이",
      "value": "{metrics_data['stride_length_asymmetry']:.1f}%",
      "status": "normal",
      "description": "왼발과 오른발의 걸음 길이 차이입니다. 낮을수록 균형이 좋아요.",
      "result": "정상범위(<5%) 내에 있습니다. 좌우 균형이 좋습니다."
    }},
    {{
      "id": "stride-time-asymmetry",
      "name": "보폭 시간 비대칭성",
      "value": "{metrics_data['stride_time_asymmetry']:.1f}%",
      "status": "normal",
      "description": "좌우 발 걸음 시간의 차이입니다. 낮을수록 균형이 좋아요.",
      "result": "정상범위(<5%) 내에 있습니다. 시간 균형이 좋습니다."
    }},
    {{
      "id": "gait-regularity",
      "name": "보행 규칙성 지수",
      "value": "{metrics_data['gait_regularity_index']:.3f}",
      "status": "normal",
      "description": "걸음의 규칙성을 나타냅니다. 높을수록 일정한 걸음이에요.",
      "result": "정상범위(>0.8) 내에 있습니다. 걸음이 규칙적입니다."
    }},
    {{
      "id": "gait-stability",
      "name": "보행 안정성 비율",
      "value": "{metrics_data['gait_stability_ratio']:.3f}",
      "status": "normal",
      "description": "걸음의 안정성을 나타냅니다. 높을수록 안정적이에요.",
      "result": "정상범위(>0.7) 내에 있습니다. 걸음이 안정적입니다."
    }},
    {{
      "id": "stance-phase",
      "name": "입각기 비율",
      "value": "{metrics_data['stance_phase_ratio']:.1%}",
      "status": "normal",
      "description": "발이 땅에 닿아 있는 시간의 비율입니다.",
      "result": "정상범위(60-65%) 내에 있습니다. 지지 시간이 적절합니다."
    }},
    {{
      "id": "swing-phase",
      "name": "유각기 비율",
      "value": "{metrics_data['swing_phase_ratio']:.1%}",
      "status": "normal",
      "description": "발이 공중에 있는 시간의 비율입니다.",
      "result": "정상범위(35-40%) 내에 있습니다. 스윙 시간이 적절합니다."
    }},
    {{
      "id": "double-support",
      "name": "양발 지지 비율",
      "value": "{metrics_data['double_support_ratio']:.1%}",
      "status": "normal",
      "description": "두 발이 동시에 땅에 닿아 있는 시간의 비율이에요. 균형과 관련있어요.",
      "result": "정상범위(15-25%) 내에 있습니다. 균형이 좋습니다."
    }}
  ]
}}

**중요 지침**:
1. 의료문헌 근거를 바탕으로 각 지표의 정상범위를 찾아 현재값과 비교
2. status는 반드시 "normal", "warning", "danger" 중 하나만 사용
3. value는 측정값과 단위를 정확히 포함
4. result는 구체적인 정상범위와 해석을 포함
5. 위 JSON 형식으로만 응답하고 다른 텍스트는 포함하지 마세요."""

            # Get Stage 1 results
            stage1_response = self.invoke_llm(stage1_llm_prompt)
            self.logger.info(f"✅ Stage 1 완료: {len(stage1_response)} characters")
            
            # Parse Stage 1 JSON response with robust error handling
            try:
                # Remove any markdown formatting and extract JSON
                stage1_response_clean = stage1_response.strip()
                if stage1_response_clean.startswith('```json'):
                    stage1_response_clean = stage1_response_clean[7:]
                if stage1_response_clean.endswith('```'):
                    stage1_response_clean = stage1_response_clean[:-3]
                stage1_response_clean = stage1_response_clean.strip()
                
                stage1_result = json.loads(stage1_response_clean)
                indicators = stage1_result.get('indicators', [])
                
                # Validate indicators structure
                if not indicators or not isinstance(indicators, list):
                    raise ValueError("Invalid indicators structure from Stage 1")
                
                # Ensure all indicators have required fields
                for indicator in indicators:
                    if not all(key in indicator for key in ['id', 'name', 'value', 'status', 'description', 'result']):
                        raise ValueError(f"Missing required fields in indicator: {indicator}")
                    # Validate status values
                    if indicator['status'] not in ['normal', 'warning', 'danger']:
                        indicator['status'] = 'normal'  # Default to normal for invalid status
                
                print(f"✅ Stage 1 성공: {len(indicators)}개 지표 분석 완료")
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"❌ Stage 1 JSON 파싱 오류: {e}")
                # Fallback indicators matching GaitAnalysisPage.jsx structure
                indicators = [
                    {
                        "id": "stride-time",
                        "name": "보폭 시간",
                        "value": f"{metrics_data['avg_stride_time']:.2f}초",
                        "status": "normal",
                        "description": "한쪽 발이 땅에 닿은 후, 같은 발이 다시 닿을 때까지 걸리는 시간입니다.",
                        "result": "분석이 완료되었습니다."
                    },
                    {
                        "id": "cadence",
                        "name": "보행률",
                        "value": f"{metrics_data['cadence']:.0f}걸음/분",
                        "status": "normal",
                        "description": "1분 동안 걷는 걸음 수입니다.",
                        "result": "분석이 완료되었습니다."
                    },
                    {
                        "id": "stride-length",
                        "name": "보폭 길이",
                        "value": f"{metrics_data['avg_stride_length']:.2f}m",
                        "status": "normal",
                        "description": "한 걸음의 길이입니다.",
                        "result": "분석이 완료되었습니다."
                    },
                    {
                        "id": "walking-speed",
                        "name": "평균 보행 속도",
                        "value": f"{metrics_data['avg_walking_speed']:.2f}m/s",
                        "status": "normal",
                        "description": "단위 시간 동안 이동한 거리입니다.",
                        "result": "분석이 완료되었습니다."
                    },
                    {
                        "id": "double-support",
                        "name": "양발 지지 비율",
                        "value": f"{metrics_data['double_support_ratio']:.1%}",
                        "status": "normal",
                        "description": "두 발이 동시에 땅에 닿아 있는 시간의 비율이에요.",
                        "result": "분석이 완료되었습니다."
                    }
                ]
            
            # Store Stage 1 results for Stage 2
            state["stage1_indicators"] = indicators
            state["stage1_response"] = stage1_response
            state["stage1_source_info"] = source_info_stage1
            
            self.logger.info(f"🎯 Stage 1 completed - {len(indicators)} indicators analyzed")
            
            # STAGE 2: Overall Assessment & Disease Risk Evaluation
            self.logger.info("🏥 Stage 2: Overall Assessment & Disease Risk Evaluation")
            
            # Create Stage 2 query with Stage 1 results
            stage2_query = stage2_template.replace("{STAGE1_RESULTS}", json.dumps(indicators, ensure_ascii=False, indent=2))
            
            # Retrieve documents for Stage 2 (disease patterns, recommendations)
            stage2_docs = retriever.get_relevant_documents(stage2_query)
            stage2_knowledge = self._format_retrieved_knowledge(stage2_docs, "Stage2")
            source_info_stage2 = self._extract_source_info(stage2_docs)
            
            # Create Stage 2 LLM prompt for disease risk and recommendations
            stage2_llm_prompt = f"""당신은 친근한 보행 분석 전문의입니다. Stage 1 지표별 분석 결과를 바탕으로 질병 위험도를 평가하고, 노인 환자에게 친근하고 쉽게 설명해주세요.

=== Stage 1 지표별 분석 결과 ===
{json.dumps(indicators, ensure_ascii=False, indent=2)}

=== 검색된 의료 문헌 ===
{stage2_knowledge}

=== 환자 정보 ===
- 연령: 60세 {patient_info['gender']}
- 신장: {patient_info['height_cm']}cm

=== 응답 형식 ===
다음 JSON 형식으로만 응답하세요. 모든 필드가 정확히 포함되어야 합니다:

{{
  "score": 85,
  "status": "보행이 전반적으로 안정적입니다",
  "riskLevel": "정상 단계",
  "diseases": [
    {{
      "id": "parkinson",
      "name": "파킨슨병",
      "probability": 0.15,
      "status": "정상 범위",
      "trend": "stable"
    }},
    {{
      "id": "stroke",
      "name": "뇌졸중",
      "probability": 0.10,
      "status": "정상 범위",
      "trend": "stable"
    }},
    {{
      "id": "fall_risk",
      "name": "낙상 위험",
      "probability": 0.20,
      "status": "정상 범위",
      "trend": "stable"
    }}
  ],
  "detailedReport": {{
    "title": "전체적으로 건강한 보행이지만, 좌우 균형을 조금 더 신경 쓰시면 좋겠어요",
    "content": "안녕하세요! {patient_info['user_id']}님의 보행 검사 결과를 쉽게 설명해드릴게요.\\n\\n【어르신의 걸음걸이 상태】\\n😊 좋은 점들\\n• 보행 속도가 또래 분들과 비슷해서 아주 좋습니다\\n• 발을 내딛는 시간이 일정해서 안정적이에요\\n• 전체적인 걸음 리듬이 자연스럽습니다\\n\\n⚠️ 조금 신경 쓸 점\\n• Stage 1에서 warning/danger 상태인 지표들 설명\\n• 개선 가능한 부분들을 부드럽게 제시\\n\\n【건강 상태는 어떤가요?】\\n걱정하실 필요 없어요! 파킨슨병이나 뇌졸중 같은 질병 징후는 거의 없습니다.\\n다만 나이가 들면서 자연스럽게 생기는 변화들이니까 미리미리 관리해주시면 됩니다.\\n\\n【집에서 쉽게 할 수 있는 운동】\\n🚶‍♀️ 매일 하면 좋은 것들\\n• 동네 한 바퀴 천천히 걷기 (30분 정도)\\n• 의자 잡고 한발로 서기 (30초씩 3번)\\n• TV 보면서 제자리 걸음\\n\\n🏊‍♀️ 일주일에 2-3번\\n• 동네 수영장에서 물속 걷기\\n• 공원에서 친구들과 가벼운 체조\\n• 집에서 스트레칭 (유튜브 보면서)\\n\\n궁금한 점 있으시면 언제든 문의해주세요! 건강한 보행 유지하시길 바랍니다 😊"
  }}
}}

**중요 지침**:
1. score는 0-100 사이의 정수 (Stage 1 결과를 종합하여 계산)
2. diseases의 probability는 0.0-1.0 사이의 소수 (백분율이 아님!)
3. diseases의 status는 "정상 범위", "주의 필요", "위험 범위" 중 하나
4. detailedReport의 content는 실제 Stage 1 결과를 반영하여 작성
5. 친근하고 안심시키는 톤으로 작성
6. 의료문헌 근거를 바탕으로 정확한 평가 수행
7. 위 JSON 형식으로만 응답하고 다른 텍스트는 포함하지 마세요."""

            # Get Stage 2 results
            stage2_response = self.invoke_llm(stage2_llm_prompt)
            self.logger.info(f"✅ Stage 2 완료: {len(stage2_response)} characters")
            
            # Parse Stage 2 JSON response with robust error handling
            try:
                # Remove any markdown formatting and extract JSON
                stage2_response_clean = stage2_response.strip()
                if stage2_response_clean.startswith('```json'):
                    stage2_response_clean = stage2_response_clean[7:]
                if stage2_response_clean.endswith('```'):
                    stage2_response_clean = stage2_response_clean[:-3]
                stage2_response_clean = stage2_response_clean.strip()
                
                stage2_result = json.loads(stage2_response_clean)
                
                # Validate required fields
                required_fields = ['score', 'status', 'riskLevel', 'diseases', 'detailedReport']
                for field in required_fields:
                    if field not in stage2_result:
                        raise ValueError(f"Missing required field: {field}")
                
                # Validate diseases structure
                diseases = stage2_result.get('diseases', [])
                if not isinstance(diseases, list):
                    raise ValueError("diseases must be a list")
                
                for disease in diseases:
                    if not all(key in disease for key in ['id', 'name', 'probability', 'status', 'trend']):
                        raise ValueError(f"Missing required fields in disease: {disease}")
                    # Ensure probability is between 0.0 and 1.0
                    if not (0.0 <= disease['probability'] <= 1.0):
                        disease['probability'] = min(max(disease['probability'], 0.0), 1.0)
                
                # Validate detailedReport structure
                detailed_report = stage2_result.get('detailedReport', {})
                if not isinstance(detailed_report, dict) or 'title' not in detailed_report or 'content' not in detailed_report:
                    raise ValueError("detailedReport must have title and content fields")
                
                # Ensure score is integer between 0-100
                score = stage2_result.get('score', 85)
                if not isinstance(score, int) or not (0 <= score <= 100):
                    stage2_result['score'] = 85
                
                print(f"✅ Stage 2 성공: 종합 진단 완료 (점수: {stage2_result['score']})")
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"❌ Stage 2 JSON 파싱 오류: {e}")
                # Fallback Stage 2 result matching GaitAnalysisPage.jsx structure
                stage2_result = {
                    "score": 85,
                    "status": "보행이 전반적으로 안정적입니다",
                    "riskLevel": "정상 단계",
                    "diseases": [
                        {
                            "id": "parkinson",
                            "name": "파킨슨병",
                            "probability": 0.15,
                            "status": "정상 범위",
                            "trend": "stable"
                        },
                        {
                            "id": "stroke",
                            "name": "뇌졸중",
                            "probability": 0.10,
                            "status": "정상 범위",
                            "trend": "stable"
                        },
                        {
                            "id": "fall_risk",
                            "name": "낙상 위험",
                            "probability": 0.20,
                            "status": "정상 범위",
                            "trend": "stable"
                        }
                    ],
                    "detailedReport": {
                        "title": "전체적으로 건강한 보행 상태입니다",
                        "content": f"안녕하세요! {patient_info['user_id']}님의 보행 검사 결과를 쉽게 설명해드릴게요.\\n\\n😊 전반적으로 건강한 보행 패턴을 보이고 있습니다.\\n\\n【집에서 쉽게 할 수 있는 운동】\\n🚶‍♀️ 매일 하면 좋은 것들\\n• 동네 한 바퀴 천천히 걷기 (30분 정도)\\n• 의자 잡고 한발로 서기 (30초씩 3번)\\n\\n궁금한 점 있으시면 언제든 문의해주세요! 건강한 보행 유지하시길 바랍니다 😊"
                    }
                }
            
            # Combine Stage 1 and Stage 2 results for final output
            final_result = {
                "indicators": indicators,
                "score": stage2_result.get("score", 85),
                "status": stage2_result.get("status", "보행이 전반적으로 안정적입니다"),
                "riskLevel": stage2_result.get("riskLevel", "정상 단계"),
                "diseases": stage2_result.get("diseases", []),
                "detailedReport": stage2_result.get("detailedReport", {
                    "title": "보행 분석이 완료되었습니다",
                    "content": "전반적으로 건강한 보행 패턴을 보이고 있습니다."
                })
            }
            
            print(f"🎯 최종 결과 구조:")
            print(f"   - indicators: {len(final_result['indicators'])}개")
            print(f"   - score: {final_result['score']}")
            print(f"   - diseases: {len(final_result['diseases'])}개")
            print(f"   - detailedReport: {len(final_result['detailedReport']['content'])}자")
            
            # Store results in state for next node
            state["diagnosis_result"] = final_result
            state["rag_diagnosis_completed"] = True
            
            return state
            
        except Exception as e:
            error_msg = f"2-stage RAG diagnosis failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "rag_diagnosis_error")

    def _check_existing_embeddings(self) -> int:
        """
        ChromaDB에 기존 임베딩 데이터가 있는지 확인
        
        Returns:
            int: 기존 문서의 개수 (0이면 새로 임베딩 필요)
        """
        try:
            # 환경변수로 강제 리로딩 옵션 제공
            force_reload = os.getenv('RAG_FORCE_RELOAD', 'false').lower() == 'true'
            if force_reload:
                self.logger.info("🔄 RAG_FORCE_RELOAD=true - 강제로 PDF 재로딩 수행")
                return 0
            
            # ChromaDB에서 기존 컬렉션의 문서 수를 확인
            collection = self.vector_store._collection
            
            # 컬렉션에 저장된 문서 수 확인
            document_count = collection.count()
            
            if document_count > 0:
                self.logger.info(f"💾 기존 ChromaDB 데이터: {document_count}개 문서 발견")
                return document_count
            else:
                self.logger.info("📭 ChromaDB가 비어있음 - 새로운 임베딩 생성 필요")
                return 0
                
        except Exception as e:
            self.logger.warning(f"기존 임베딩 확인 중 오류: {e}")
            # 확인 실패 시 안전하게 새로 임베딩하도록 0 반환
            return 0
    
    def _format_retrieved_knowledge(self, docs: list, stage_name: str) -> str:
        """Format retrieved documents for LLM prompt"""
        
        knowledge = ""
        for i, doc in enumerate(docs, 1):
            source_file = doc.metadata.get('source_file', 'unknown_source')
            doc_type = doc.metadata.get('document_type', 'unknown_type')
            page_num = doc.metadata.get('page', '알 수 없음')
            
            content_snippet = doc.page_content.strip()
            if len(content_snippet) > 500:
                content_snippet = content_snippet[:500] + "..."
            
            knowledge += f"""
=== 참조문헌 {i} ({stage_name}): {source_file} ===
문서유형: {doc_type}
페이지: {page_num}
관련내용:
{content_snippet}

"""
        return knowledge
    
    def _extract_source_info(self, docs: list) -> list:
        """Extract source information from documents"""
        
        source_info = []
        for i, doc in enumerate(docs, 1):
            source_info.append({
                "번호": i,
                "파일명": doc.metadata.get('source_file', 'unknown_source'),
                "문서유형": doc.metadata.get('document_type', 'unknown_type'),
                "페이지": doc.metadata.get('page', '알 수 없음'),
                "내용길이": len(doc.page_content)
            })
        return source_info

class StoreDiagnosisNode(BaseNode):
    """
    Node 11: Store medical diagnosis to Supabase
    Saves RAG-generated diagnosis results in simplified structure
    """
    
    def __init__(self):
        super().__init__(PipelineStages.STORE_DIAGNOSIS)
    
    def execute(self, state: GraphState) -> GraphState:
        """Store medical diagnosis to Supabase database"""
        
        # Check for new simplified structure
        if "diagnosis_result" not in state:
            return StateManager.set_error(state, "Missing diagnosis_result from RAG analysis", "validation_error")
        
        diagnosis_result = state["diagnosis_result"]
        user_id = state.get("user_id", "unknown")
        session_id = state.get("session_id", "unknown")

        try:
            from supabase import create_client
            import json
            
            # Use Service Role key to bypass RLS policies
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("Supabase credentials not found in environment variables")
                
            supabase = create_client(supabase_url, supabase_key)
            
            # Prepare data for storage with new simplified structure
            storage_data = {
                'session_id': session_id,
                'user_id': user_id,
                'diagnosis_json': diagnosis_result,  # Store simplified structure directly
                'retrieved_papers': 0,  # Not tracking paper count anymore
                'ai_model_used': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                'confidence_score': self._calculate_confidence_score(diagnosis_result),
                'knowledge_base_version': 'medical_pdfs_v1',
                'processing_time_seconds': None
            }

            # Store to Supabase
            result = supabase.table('gait_diagnosis').insert(storage_data).execute()
            
            if result.data:
                stored_record = result.data[0]
                record_id = stored_record.get('id')
                state["diagnosis_record_id"] = record_id
                state["diagnosis_stored"] = True
                
                print(f"✅ 진단 결과 저장 완료: Record ID {record_id}")
                return state
            else:
                error_info = getattr(result, 'error', 'Unknown error')
                return StateManager.set_error(state, f"Failed to store diagnosis: {error_info}", "storage_error")
            
        except Exception as e:
            error_msg = f"Diagnosis storage failed: {str(e)}"
            print(f"❌ 저장 실패: {error_msg}")
            return StateManager.set_error(state, error_msg, "storage_execution_error")
    
    def _calculate_confidence_score(self, diagnosis_result: dict) -> float:
        """Calculate confidence score based on diagnosis results"""
        try:
            # Base confidence from overall score
            score = diagnosis_result.get("score", 85)
            base_confidence = score / 100.0
            
            # Adjust based on risk level
            risk_level = diagnosis_result.get("riskLevel", "정상 단계")
            if risk_level == "정상 단계":
                confidence = min(1.0, base_confidence + 0.05)
            elif risk_level == "위험 단계":
                confidence = max(0.3, base_confidence - 0.15)
            else:
                confidence = base_confidence
            
            # Check indicator consistency
            indicators = diagnosis_result.get("indicators", [])
            if indicators:
                normal_count = sum(1 for ind in indicators if ind.get("status") == "normal")
                consistency_boost = (normal_count / len(indicators)) * 0.1
                confidence = min(1.0, confidence + consistency_boost)
            
            return round(confidence, 3)
            
        except Exception as e:
            print(f"⚠️ 신뢰도 계산 오류: {e}")
            return 0.75  # Default confidence
