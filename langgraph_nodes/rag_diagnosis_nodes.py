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

# Conditional imports to handle both module and script execution
try:
    # Try relative imports first (when run as module)
    from .base_node import BaseNode
    from .graph_state import GraphState, StateManager, PipelineStages
except ImportError:
    # Fall back to absolute imports (when run as script)
    import sys
    from pathlib import Path
    
    # Add the parent directory to sys.path so we can import from langgraph_nodes
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    # Now try absolute imports
    try:
        from langgraph_nodes.base_node import BaseNode
        from langgraph_nodes.graph_state import GraphState, StateManager, PipelineStages
    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("Make sure you're running this from the correct directory or as a module.")
        sys.exit(1)

# Load environment variables
load_dotenv()

class ComposePromptNode(BaseNode):
    """
    Node 9: Compose diagnostic prompt from gait metrics
    Prepares structured prompt for RAG-based medical diagnosis
    """
    
    def __init__(self):
        super().__init__(PipelineStages.COMPOSE_PROMPT)
    
    def get_system_prompt(self) -> str:
        return """You are a medical data analyst specializing in gait analysis interpretation.
        
        Your task is to compose a comprehensive diagnostic prompt from calculated gait metrics:
        
        Prompt composition requirements:
        - Summarize all 12 gait metrics in clinical context
        - Identify abnormal values based on normative data
        - Highlight asymmetries and stability concerns
        - Structure information for medical diagnosis retrieval
        - Include patient demographics (age estimation from gait patterns)
        
        The composed prompt will be used to search medical literature for:
        - Potential pathological conditions
        - Differential diagnoses
        - Clinical recommendations
        - Rehabilitation strategies
        
        Ensure the prompt is medically accurate and comprehensive.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Compose diagnostic prompt from gait metrics"""
        
        if not self.validate_state_requirements(state, ["gait_metrics", "height_cm"]):
            return StateManager.set_error(state, "Missing required fields: gait_metrics, height_cm", "validation_error")
        
        gait_metrics = state["gait_metrics"]
        height_cm = state["height_cm"]
        date = state.get("date", "unknown")
        session_id = state.get("session_id", "unknown")
        
        try:
            # Create concise, evidence-based diagnostic prompt
            # Focus only on objective metrics, avoid lengthy LLM generation
            
            # Extract ALL 12 gait metrics with normal ranges for comparison
            avg_stride_time = gait_metrics.get('avg_stride_time', 0)
            avg_stride_length = gait_metrics.get('avg_stride_length', 0) 
            avg_walking_speed = gait_metrics.get('avg_walking_speed', 0)
            cadence = gait_metrics.get('cadence', 0)
            stride_time_asymmetry = gait_metrics.get('stride_time_asymmetry', 0)
            stride_length_asymmetry = gait_metrics.get('stride_length_asymmetry', 0)
            stride_time_cv = gait_metrics.get('stride_time_cv', 0)
            walking_speed_cv = gait_metrics.get('walking_speed_cv', 0)
            
            # Additional 4 metrics (previously missing from RAG prompt)
            stride_length_cv = gait_metrics.get('stride_length_cv', 0)
            step_width = gait_metrics.get('step_width', 0)
            gait_regularity_index = gait_metrics.get('gait_regularity_index', 0)
            gait_stability_ratio = gait_metrics.get('gait_stability_ratio', 0)
            
            # New phase ratio metrics
            stance_phase_ratio = gait_metrics.get('stance_phase_ratio', 0.6)
            swing_phase_ratio = gait_metrics.get('swing_phase_ratio', 0.4)
            double_support_ratio = gait_metrics.get('double_support_ratio', 0.2)
            
            # Create comprehensive prompt with ALL 15 metrics
            structured_prompt = f"""보행 분석 결과

환자 정보: 신장 {height_cm}cm, 날짜 {date}

전체 15개 객관적 지표:

【시간적 지표】
• 보폭 시간: {avg_stride_time:.2f}초 (정상: 1.0-1.3초)
• 보행률: {cadence:.0f}걸음/분 (정상: 100-120)
• 보폭 시간 변동성: {stride_time_cv:.1f}% (정상: <5%)

【공간적 지표】
• 보폭 길이: {avg_stride_length:.2f}m (정상: 1.2-1.6m)
• 보폭 길이 변동성: {stride_length_cv:.1f}% (정상: <5%)
• 보폭 폭: {step_width:.2f}m (정상: 0.1-0.15m)

【속도 지표】
• 보행 속도: {avg_walking_speed:.2f}m/s (정상: 1.0-1.4m/s)
• 보행 속도 변동성: {walking_speed_cv:.1f}% (정상: <5%)

【비대칭성 지표】
• 보폭 시간 비대칭성: {stride_time_asymmetry:.1f}% (정상: <5%)
• 보폭 길이 비대칭성: {stride_length_asymmetry:.1f}% (정상: <5%)

【안정성 지표】
• 보행 규칙성 지수: {gait_regularity_index:.3f} (정상: >0.8)
• 보행 안정성 비율: {gait_stability_ratio:.3f} (정상: >0.8)

【보행 주기 지표】
• 입각기 비율: {stance_phase_ratio:.1%} (정상: 60-65%)
• 유각기 비율: {swing_phase_ratio:.1%} (정상: 35-40%)
• 양발지지 비율: {double_support_ratio:.1%} (정상: 15-25%)

임상 질문: 이 15개 모든 지표를 종합적으로 분석하여 가장 가능성이 높은 임상 평가는 무엇입니까? 정상 대 병리학적 패턴만 고려하세요."""
            
            # Update state
            state["prompt_str"] = structured_prompt
            
            self.logger.info(f"Diagnostic prompt composed: {len(structured_prompt)} characters")
            
            return state
            
        except Exception as e:
            error_msg = f"Diagnostic prompt composition failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "prompt_composition_error")

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
                
                # PDF 파일 변경 감지 (선택적)
                pdf_changed = self._check_pdf_files_changed()
                if pdf_changed:
                    self.logger.info("📄 PDF 파일 변경 감지 - 재임베딩 수행")
                    return 0
                
                # 샘플 문서 정보 로그 (디버깅용)
                try:
                    sample_results = collection.peek(limit=3)
                    if sample_results and 'metadatas' in sample_results:
                        for i, metadata in enumerate(sample_results['metadatas'][:3]):
                            source_file = metadata.get('source_file', 'unknown')
                            doc_type = metadata.get('document_type', 'unknown')
                            self.logger.debug(f"   📄 샘플 {i+1}: {source_file} ({doc_type})")
                except Exception as peek_error:
                    self.logger.debug(f"샘플 문서 정보 조회 실패: {peek_error}")
                
                return document_count
            else:
                self.logger.info("📭 ChromaDB가 비어있음 - 새로운 임베딩 생성 필요")
                return 0
                
        except Exception as e:
            self.logger.warning(f"기존 임베딩 확인 중 오류: {e}")
            # 확인 실패 시 안전하게 새로 임베딩하도록 0 반환
            return 0
    
    def _check_pdf_files_changed(self) -> bool:
        """
        PDF 파일이 변경되었는지 확인 (선택적 기능)
        
        Returns:
            bool: PDF 파일이 변경되었으면 True
        """
        try:
            # 환경변수로 PDF 변경 감지 활성화 여부 확인
            check_changes = os.getenv('RAG_CHECK_PDF_CHANGES', 'false').lower() == 'true'
            if not check_changes:
                return False
            
            docs_dir = Path("docs/medical_pdfs")
            if not docs_dir.exists():
                return False
            
            # PDF 파일들의 수정 시간 확인
            pdf_files = list(docs_dir.glob("*.pdf"))
            if not pdf_files:
                return False
            
            # 가장 최근 PDF 수정 시간 찾기
            latest_pdf_time = max(f.stat().st_mtime for f in pdf_files)
            
            # ChromaDB 생성 시간과 비교
            project_root = Path(os.getenv('PROJECT_ROOT', '.'))
            chroma_db_path = project_root / "chroma_db" / "chroma.sqlite3"
            
            if chroma_db_path.exists():
                chroma_db_time = chroma_db_path.stat().st_mtime
                
                if latest_pdf_time > chroma_db_time:
                    self.logger.info(f"📄 PDF 파일이 ChromaDB보다 최신: PDF={datetime.fromtimestamp(latest_pdf_time)}, DB={datetime.fromtimestamp(chroma_db_time)}")
                    return True
                else:
                    self.logger.debug(f"📄 PDF 파일 변경 없음: PDF={datetime.fromtimestamp(latest_pdf_time)}, DB={datetime.fromtimestamp(chroma_db_time)}")
                    return False
            else:
                # ChromaDB 파일이 없으면 새로 생성 필요
                return True
                
        except Exception as e:
            self.logger.warning(f"PDF 파일 변경 감지 중 오류: {e}")
            # 오류 시 안전하게 변경 없음으로 처리
            return False
    
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
    
    def get_system_prompt(self) -> str:
        return """You are a medical AI specialist in gait analysis and movement disorders.
        
        Your task is to provide evidence-based medical diagnosis using retrieved medical knowledge:
        
        Diagnostic process:
        1. Analyze retrieved medical literature
        2. Compare patient metrics with known pathological patterns
        3. Generate differential diagnoses with confidence levels
        4. Provide clinical recommendations
        5. Suggest further evaluations if needed
        
        Output requirements:
        - Primary diagnosis with rationale
        - Differential diagnoses (2-3 alternatives)
        - Confidence level (0-100%)
        - Clinical recommendations
        - Rehabilitation suggestions
        - Red flags or urgent referrals
        
        Base all conclusions on evidence from retrieved medical sources.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Generate RAG-based medical diagnosis"""
        
        if not self.validate_state_requirements(state, ["prompt_str"]):
            return StateManager.set_error(state, "Missing required field: prompt_str", "validation_error")
        
        if self.vector_store is None:
            return StateManager.set_error(state, "RAG system not initialized", "rag_system_error")
        
        prompt_str = state["prompt_str"]
        session_id = state.get("session_id", "unknown")
        gait_metrics = state.get("gait_metrics", {})

        try:
            # Retrieve relevant medical knowledge
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
            relevant_docs = retriever.get_relevant_documents(prompt_str)
            
            # Format retrieved knowledge with source information
            retrieved_knowledge = ""
            source_info = []
            
            for i, doc in enumerate(relevant_docs, 1):
                source_file = doc.metadata.get('source_file', 'unknown_source')
                doc_type = doc.metadata.get('document_type', 'unknown_type')
                page_num = doc.metadata.get('page', '알 수 없음')
                
                # Extract relevant content snippet
                content_snippet = doc.page_content.strip()
                if len(content_snippet) > 300:
                    content_snippet = content_snippet[:300] + "..."
                
                retrieved_knowledge += f"""
=== 참조문헌 {i}: {source_file} ===
문서유형: {doc_type}
페이지: {page_num}
관련내용:
{content_snippet}

"""
                
                source_info.append({
                    "번호": i,
                    "파일명": source_file,
                    "문서유형": doc_type,
                    "페이지": page_num,
                    "내용길이": len(doc.page_content)
                })
            
            self.logger.info(f"Retrieved {len(relevant_docs)} documents for RAG diagnosis")
            
            # Create comprehensive diagnostic prompt with structured output request
            diagnostic_llm_prompt = f"""
            당신은 임상 보행 분석 전문의입니다. 아래 검색된 의료 문헌 정보를 바탕으로 환자를 진단하고 구조화된 평가를 제공하세요.
            
            === 검색된 의료 문헌 정보 ===
            {retrieved_knowledge}
            
            === 환자 보행 분석 데이터 ===
            {prompt_str}
            
            === 진단 지침 ===
            1. **오직 검색된 의료 문헌의 기준과 정보만 사용**하여 진단하세요
            2. 진단 근거를 제시할 때 **구체적인 문헌명과 내용을 인용**하세요
            3. 각 판단마다 **"참조문헌 X에 따르면..."** 형식으로 출처를 명시하세요
            4. 검색된 정보에 근거가 없으면 "추가 정보 필요"라고 명시하세요
            5. 최종 평가는 정확한 점수(0-100)와 상태를 포함하세요
            
            === 응답 형식 (정확히 이 형식으로만 응답) ===
            CLINICAL_ASSESSMENT: [정상/주의/위험 중 하나]
            SCORE: [0-100 사이의 정수]
            STATUS: [구체적인 상태 설명]
            RISK_LEVEL: [정상 단계/주의 단계/위험 단계 중 하나]
            
            임상 평가: [검색된 문헌 기준으로 상세 판정]
            
            주요 소견: [검색된 문헌에서 찾은 관련 패턴과 환자 데이터 비교]
            
            문헌 근거: 
            - 참조문헌 1 ({source_info[0]["파일명"] if source_info else "알 수 없음"}): [구체적 인용 내용]
            - 참조문헌 2 ({source_info[1]["파일명"] if len(source_info) > 1 else "알 수 없음"}): [구체적 인용 내용]
            - 참조문헌 3 ({source_info[2]["파일명"] if len(source_info) > 2 else "알 수 없음"}): [구체적 인용 내용]
            - 참조문헌 4 ({source_info[3]["파일명"] if len(source_info) > 3 else "알 수 없음"}): [구체적 인용 내용]
            
            신뢰도: [검색된 정보의 충분성과 일치성에 따른 신뢰도]
            
            진단: [검색된 문헌에 기반한 가능성 높은 진단명]
            
            권장사항: [검색된 문헌에서 제시된 치료/관리 방안]
            
            참고문헌 목록:
            {chr(10).join([f"- {info['파일명']} (페이지 {info['페이지']})" for info in source_info])}
            
            **중요: 응답 시작 부분의 CLINICAL_ASSESSMENT, SCORE, STATUS, RISK_LEVEL을 반드시 포함하고, 모든 판단은 검색된 의료 문헌 정보에만 근거하세요.**
            """
            
            # Get LLM diagnosis
            diagnosis_response = self.invoke_llm(diagnostic_llm_prompt)
            
            # Generate structured JSON diagnosis result with RAG integration
            structured_diagnosis = self._generate_structured_diagnosis(state, gait_metrics, diagnosis_response, source_info)
            
            # Update state with both formats
            state["medical_diagnosis"] = structured_diagnosis  # New JSON format
            state["diagnosis_result"] = structured_diagnosis   # Alternative key for compatibility
            
            # Keep detailed metadata separate
            state["medical_diagnosis_metadata"] = {
                "session_id": session_id,
                "diagnosis_timestamp": datetime.now().isoformat(),
                "raw_diagnosis": diagnosis_response,
                "retrieved_sources": len(relevant_docs),
                "knowledge_base_used": "medical_pdfs",
                "prompt_length": len(prompt_str),
                "response_length": len(diagnosis_response),
                "source_documents": source_info
            }
            
            self.logger.info(f"RAG diagnosis generated: {len(diagnosis_response)} characters from {len(relevant_docs)} sources")
            
            return state
            
        except Exception as e:
            error_msg = f"RAG diagnosis generation failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "rag_diagnosis_error")
    
    def _generate_structured_diagnosis(self, state: GraphState, gait_metrics: dict, raw_diagnosis: str, source_info: list) -> dict:
        """Generate structured JSON diagnosis matching API endpoint format"""
        
        try:
            # Generate indicators from gait metrics
            indicators = self._generate_indicators(gait_metrics)
            
            # Calculate disease probabilities
            diseases = self._calculate_disease_probabilities(gait_metrics)
            
            # Initial assessment calculation
            initial_score, initial_status, initial_risk_level = self._calculate_overall_assessment(gait_metrics, indicators)
            
            # Parse structured RAG assessment from LLM response
            final_score, final_status, final_risk_level = self._parse_structured_rag_assessment(
                raw_diagnosis, initial_score, initial_status, initial_risk_level
            )
            
            # Extract detailed report from raw diagnosis
            detailed_report = self._extract_detailed_report(raw_diagnosis)
            
            # Create structured JSON response with integrated assessment
            structured_result = {
                "success": True,
                "data": {
                    "userId": state.get("user_id", "unknown"),
                    "score": final_score,
                    "status": final_status,
                    "riskLevel": final_risk_level,
                    "analyzedAt": datetime.now().isoformat(),
                    "indicators": indicators,
                    "diseases": diseases,
                    "detailedReport": detailed_report
                }
            }
            
            return structured_result
            
        except Exception as e:
            self.logger.error(f"Failed to generate structured diagnosis: {str(e)}")
            # Return fallback structure
            return {
                "success": False,
                "data": {
                    "userId": "unknown",
                    "score": 50,
                    "status": "분석 중 오류 발생",
                    "riskLevel": "확인 필요",
                    "analyzedAt": datetime.now().isoformat(),
                    "indicators": [],
                    "diseases": [],
                    "detailedReport": {
                        "title": "진단 오류",
                        "content": "분석 중 오류가 발생했습니다. 다시 시도해 주세요."
                    }
                }
            }
    
    def _generate_indicators(self, gait_metrics: dict) -> list:
        """Generate indicators array from gait metrics"""
        
        indicators = []
        
        try:
            # 1. Stride Time (보폭 시간)
            stride_time = gait_metrics.get('avg_stride_time', 1.1)
            stride_time_status, stride_time_result = self._assess_stride_time(stride_time)
            indicators.append({
                "id": "stride-time",
                "name": "보폭 시간",
                "value": f"{stride_time:.2f}초",
                "status": stride_time_status,
                "description": "한쪽 발이 땅에 닿은 후, 같은 발이 다시 닿을 때까지 걸리는 시간입니다. 걸음 템포를 확인할 수 있어요.",
                "result": stride_time_result
            })
            
            # 2. Double Support (양발 지지 비율) - 실제 계산된 값 사용
            double_support_ratio = gait_metrics.get('double_support_ratio', 0.2) * 100  # Convert ratio to percentage
            ds_status, ds_result = self._assess_double_support(double_support_ratio)
            indicators.append({
                "id": "double-support", 
                "name": "양발 지지 비율",
                "value": f"{double_support_ratio:.1f}%",
                "status": ds_status,
                "description": "두 발이 동시에 땅에 닿아 있는 시간의 비율이에요. 보행 균형이 불안할수록 높아집니다.",
                "result": ds_result
            })
            
            # 3. Stride Difference (양발 보폭 차이)
            stride_asymmetry = gait_metrics.get('stride_length_asymmetry', 0.0)
            stride_diff_m = self._convert_asymmetry_to_meters(stride_asymmetry, gait_metrics.get('avg_stride_length', 1.2))
            asym_status, asym_result = self._assess_stride_asymmetry(stride_asymmetry)
            indicators.append({
                "id": "stride-difference",
                "name": "양발 보폭 차이", 
                "value": f"{stride_diff_m:.2f}m",
                "status": asym_status,
                "description": "왼발과 오른발의 걸음 길이가 얼마나 다른지를 보여줍니다. 좌우 균형 상태를 파악할 수 있어요.",
                "result": asym_result
            })
            
            # 4. Walking Speed (평균 보행 속도)
            walking_speed = gait_metrics.get('avg_walking_speed', 1.2)
            speed_status, speed_result = self._assess_walking_speed(walking_speed)
            indicators.append({
                "id": "walking-speed",
                "name": "평균 보행 속도",
                "value": f"{walking_speed:.1f}m/s", 
                "status": speed_status,
                "description": "단위 시간 동안 이동한 거리를 나타내는 지표입니다. 전체 활동성과 운동 능력을 확인할 수 있어요.",
                "result": speed_result
            })
            
            # 5. Stance Phase Ratio (입각기 비율)
            stance_phase_ratio = gait_metrics.get('stance_phase_ratio', 0.6)
            stance_status, stance_result = self._assess_stance_phase_ratio(stance_phase_ratio)
            indicators.append({
                "id": "stance-phase",
                "name": "입각기 비율",
                "value": f"{stance_phase_ratio:.1%}",
                "status": stance_status,
                "description": "보행 주기 중 발이 땅에 닿아 있는 시간의 비율입니다. 균형과 안정성을 평가할 수 있어요.",
                "result": stance_result
            })
            
        except Exception as e:
            self.logger.error(f"Error generating indicators: {str(e)}")
            
        return indicators
    
    def _calculate_disease_probabilities(self, gait_metrics: dict) -> list:
        """Calculate disease probabilities based on gait metrics"""
        
        diseases = []
        
        try:
            # Parkinson's Disease Risk
            parkinson_prob = self._calculate_parkinson_risk(gait_metrics)
            parkinson_status, parkinson_trend = self._assess_disease_risk(parkinson_prob, "parkinson")
            diseases.append({
                "id": "parkinson",
                "name": "파킨슨병",
                "probability": round(parkinson_prob, 2),
                "status": parkinson_status,
                "trend": parkinson_trend
            })
            
            # Stroke Risk
            stroke_prob = self._calculate_stroke_risk(gait_metrics)
            stroke_status, stroke_trend = self._assess_disease_risk(stroke_prob, "stroke")
            diseases.append({
                "id": "stroke", 
                "name": "뇌졸중",
                "probability": round(stroke_prob, 2),
                "status": stroke_status,
                "trend": stroke_trend
            })
            
        except Exception as e:
            self.logger.error(f"Error calculating disease probabilities: {str(e)}")
            
        return diseases
    
    def _calculate_overall_assessment(self, gait_metrics: dict, indicators: list) -> tuple:
        """Calculate overall score, status, and risk level"""
        
        try:
            # Base score starts at 100
            base_score = 100
            
            # Weight factors for different metrics
            speed_weight = 0.30
            asymmetry_weight = 0.25  
            stability_weight = 0.25
            regularity_weight = 0.20
            
            # Speed score (0-100)
            speed = gait_metrics.get('avg_walking_speed', 1.2)
            speed_score = min(100, max(0, (speed / 1.3) * 100))
            
            # Asymmetry score (inverted - lower asymmetry = higher score)
            asymmetry = gait_metrics.get('stride_length_asymmetry', 0.0)
            asymmetry_score = max(0, 100 - (asymmetry * 10))
            
            # Stability score
            stability = gait_metrics.get('gait_stability_ratio', 0.8)
            stability_score = stability * 100
            
            # Regularity score  
            regularity = gait_metrics.get('gait_regularity_index', 0.8)
            regularity_score = regularity * 100
            
            # Calculate weighted average
            overall_score = int(
                speed_score * speed_weight +
                asymmetry_score * asymmetry_weight +
                stability_score * stability_weight +
                regularity_score * regularity_weight
            )
            
            # Determine status and risk level
            if overall_score >= 80:
                status = "보행 매우 안정적"
                risk_level = "정상 단계"
            elif overall_score >= 65:
                status = "보행 안정적"  
                risk_level = "정상 단계"
            elif overall_score >= 50:
                status = "보행 주의 필요"
                risk_level = "주의 단계"
            else:
                status = "보행 불안정"
                risk_level = "위험 단계"
                
            return overall_score, status, risk_level
            
        except Exception as e:
            self.logger.error(f"Error calculating overall assessment: {str(e)}")
            return 50, "분석 오류", "확인 필요"
    
    # Helper methods for indicator assessments
    def _assess_stride_time(self, stride_time: float) -> tuple:
        """Assess stride time and return status and result"""
        if 1.0 <= stride_time <= 1.2:
            return "normal", "분석 결과 정상입니다!"
        elif 0.8 <= stride_time < 1.0 or 1.2 < stride_time <= 1.4:
            return "warning", "분석 결과 주의입니다!"
        else:
            return "danger", "분석 결과 위험입니다!"
    

    
    def _assess_double_support(self, ratio: float) -> tuple:
        """Assess double support ratio"""
        if ratio < 25.0:
            return "normal", "분석 결과 정상입니다!"
        elif 25.0 <= ratio <= 30.0:
            return "warning", "분석 결과 주의입니다!"
        else:
            return "danger", "분석 결과 위험입니다!"
    
    def _convert_asymmetry_to_meters(self, asymmetry_percent: float, avg_stride_length: float) -> float:
        """Convert stride asymmetry percentage to meter difference"""
        return (asymmetry_percent / 100.0) * avg_stride_length
    
    def _assess_stride_asymmetry(self, asymmetry: float) -> tuple:
        """Assess stride length asymmetry"""
        if asymmetry < 3.0:
            return "normal", "분석 결과 정상입니다!"
        elif 3.0 <= asymmetry <= 7.0:
            return "warning", "분석 결과 주의입니다!"
        else:
            return "danger", "분석 결과 위험입니다!"
    
    def _assess_walking_speed(self, speed: float) -> tuple:
        """Assess walking speed"""
        if speed > 1.2:
            return "normal", "분석 결과 정상입니다!"
        elif 0.9 <= speed <= 1.2:
            return "warning", "분석 결과 주의입니다!"
        else:
            return "danger", "분석 결과 위험입니다!"
    
    def _assess_stance_phase_ratio(self, ratio: float) -> tuple:
        """Assess stance phase ratio"""
        if 0.5 <= ratio <= 0.7:
            return "normal", "분석 결과 정상입니다!"
        elif 0.3 <= ratio < 0.5 or 0.7 < ratio <= 1.0:
            return "warning", "분석 결과 주의입니다!"
        else:
            return "danger", "분석 결과 위험입니다!"
    
    # Disease risk calculation methods
    def _calculate_parkinson_risk(self, gait_metrics: dict) -> float:
        """Calculate Parkinson's disease risk score"""
        # Risk factors: low cadence, high stride variability, low regularity
        cadence = gait_metrics.get('cadence', 120.0)
        stride_time_cv = gait_metrics.get('stride_time_cv', 3.0)
        regularity = gait_metrics.get('gait_regularity_index', 0.8)
        
        risk_score = 0.0
        
        # Low cadence increases risk
        if cadence < 100:
            risk_score += 3.0
        elif cadence < 110:
            risk_score += 1.5
        
        # High stride variability increases risk
        if stride_time_cv > 6.0:
            risk_score += 2.5
        elif stride_time_cv > 4.0:
            risk_score += 1.0
        
        # Low regularity increases risk
        if regularity < 0.6:
            risk_score += 2.0
        elif regularity < 0.7:
            risk_score += 1.0
        
        # Normalize to -10 to +10 scale
        return min(10.0, max(-10.0, risk_score - 5.0))
    
    def _calculate_stroke_risk(self, gait_metrics: dict) -> float:
        """Calculate stroke risk score"""
        # Risk factors: high asymmetry, slow speed, instability
        asymmetry = gait_metrics.get('stride_length_asymmetry', 0.0)
        speed = gait_metrics.get('avg_walking_speed', 1.2)
        stability = gait_metrics.get('gait_stability_ratio', 0.8)
        
        risk_score = 0.0
        
        # High asymmetry increases risk
        if asymmetry > 10.0:
            risk_score += 4.0
        elif asymmetry > 5.0:
            risk_score += 2.0
        
        # Slow speed increases risk
        if speed < 0.8:
            risk_score += 3.0
        elif speed < 1.0:
            risk_score += 1.5
        
        # Low stability increases risk
        if stability < 0.6:
            risk_score += 2.5
        elif stability < 0.7:
            risk_score += 1.0
        
        # Normalize to -10 to +10 scale
        return min(10.0, max(-10.0, risk_score - 4.0))
    
    def _assess_disease_risk(self, probability: float, disease_type: str) -> tuple:
        """Assess disease risk and determine status and trend"""
        if probability < -2.0:
            status = "정상 범위"
            trend = "down"
        elif probability < 2.0:
            status = "관찰 유지"
            trend = "stable"
        elif probability < 5.0:
            status = "주의 필요"
            trend = "up"
        else:
            status = "위험 범위"
            trend = "up"
        
        return status, trend
    
    def _parse_structured_rag_assessment(self, rag_response: str, initial_score: int, initial_status: str, initial_risk_level: str) -> tuple:
        """Parse structured assessment from RAG LLM response"""
        
        try:
            # Extract structured fields from LLM response
            lines = rag_response.strip().split('\n')
            
            rag_score = None
            rag_status = None
            rag_risk_level = None
            rag_assessment = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('CLINICAL_ASSESSMENT:'):
                    rag_assessment = line.split(':', 1)[1].strip()
                elif line.startswith('SCORE:'):
                    try:
                        rag_score = int(line.split(':', 1)[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('STATUS:'):
                    rag_status = line.split(':', 1)[1].strip()
                elif line.startswith('RISK_LEVEL:'):
                    rag_risk_level = line.split(':', 1)[1].strip()
            
            # Use RAG assessment if available and valid
            if rag_score is not None and 0 <= rag_score <= 100:
                final_score = rag_score
                self.logger.info(f"Using RAG score: {rag_score} (initial was {initial_score})")
            else:
                final_score = initial_score
                self.logger.warning(f"Invalid RAG score, using initial: {initial_score}")
            
            if rag_status:
                final_status = rag_status
                self.logger.info(f"Using RAG status: {rag_status}")
            else:
                final_status = initial_status
                self.logger.warning(f"No RAG status found, using initial: {initial_status}")
            
            if rag_risk_level and rag_risk_level in ["정상 단계", "주의 단계", "위험 단계"]:
                final_risk_level = rag_risk_level
                self.logger.info(f"Using RAG risk level: {rag_risk_level}")
            else:
                final_risk_level = initial_risk_level
                self.logger.warning(f"Invalid RAG risk level, using initial: {initial_risk_level}")
            
            # Validate consistency between score and risk level
            if final_score >= 80 and final_risk_level == "위험 단계":
                # Score too high for risk level, adjust
                final_score = min(final_score, 55)
                self.logger.info(f"Adjusted score for consistency: {final_score}")
            elif final_score <= 40 and final_risk_level == "정상 단계":
                # Score too low for normal level, adjust
                final_risk_level = "위험 단계"
                self.logger.info(f"Adjusted risk level for consistency: {final_risk_level}")
            
            return final_score, final_status, final_risk_level
            
        except Exception as e:
            self.logger.error(f"Error parsing structured RAG assessment: {str(e)}")
            # Return initial assessment on error
            return initial_score, initial_status, initial_risk_level
    
    def _extract_detailed_report(self, raw_diagnosis: str) -> dict:
        """Extract detailed report from raw diagnosis text"""
        try:
            # Try to extract title and content from diagnosis
            lines = raw_diagnosis.strip().split('\n')
            
            # Look for diagnosis or assessment line
            title = "의료 진단 결과"
            content = raw_diagnosis
            
            for line in lines:
                if "진단:" in line:
                    title = line.split(":")[-1].strip()
                    break
                elif "임상 평가:" in line:
                    title = line.split(":")[-1].strip()
                    break
            
            # Clean up content - allow full content instead of truncating
            # Remove the 500 character limit to show complete diagnosis
            # if len(content) > 500:
            #     content = content[:500] + "..."
            
            return {
                "title": title,
                "content": content
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting detailed report: {str(e)}")
            return {
                "title": "진단 결과",
                "content": "진단 결과를 처리하는 중 오류가 발생했습니다."
            }

class StoreDiagnosisNode(BaseNode):
    """
    Node 11: Store medical diagnosis to Supabase
    Saves RAG-generated diagnosis and recommendations
    """
    
    def __init__(self):
        super().__init__(PipelineStages.STORE_DIAGNOSIS)
    
    def get_system_prompt(self) -> str:
        return """You are a medical records management specialist.
        
        Your task is to store AI-generated medical diagnoses in the database:
        
        Storage requirements:
        - Store complete diagnosis with metadata
        - Link to corresponding gait metrics record
        - Include confidence levels and sources
        - Maintain audit trail for medical decisions
        
        Database validation:
        - Verify diagnosis completeness
        - Check foreign key relationships
        - Validate JSON structure
        
        Provide confirmation of successful storage with record linkage.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Store medical diagnosis to Supabase database"""
        
        required = ["medical_diagnosis", "medical_diagnosis_metadata", "user_id", "session_id"]
        if not self.validate_state_requirements(state, required):
            return StateManager.set_error(state, f"Missing required fields: {required}", "validation_error")
        
        diagnosis_result = state["medical_diagnosis"]
        diagnosis_metadata = state["medical_diagnosis_metadata"]
        user_id = state["user_id"]
        session_id = state.get("session_id")

        try:
            from supabase import create_client
            import json
            
            # Use Service Role key to bypass RLS policies
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("Supabase credentials not found in environment variables")
                
            supabase = create_client(supabase_url, supabase_key)
            
            # Handle both old format (string) and new format (structured JSON)
            if isinstance(diagnosis_result, dict) and diagnosis_result.get("success") is not None:
                # New structured JSON format
                diagnosis_content = diagnosis_result
                confidence_score = self._extract_confidence_score(diagnosis_result)
            else:
                # Legacy text format - convert to structured format for compatibility
                diagnosis_content = {
                    "success": True,
                    "data": {
                        "userId": user_id,
                        "score": 50,  # Default score for legacy data
                        "status": "Legacy 진단",
                        "riskLevel": "확인 필요",
                        "analyzedAt": diagnosis_metadata.get('diagnosis_timestamp', datetime.now().isoformat()),
                        "indicators": [],
                        "diseases": [],
                        "detailedReport": {
                            "title": "Legacy 진단 결과",
                            "content": str(diagnosis_result)[:500]
                        }
                    },
                    # Add legacy metadata for compatibility
                    "legacy_metadata": {
                        'diagnosis_text': str(diagnosis_result),
                        'diagnosis_timestamp': diagnosis_metadata.get('diagnosis_timestamp'),
                        'knowledge_base_used': diagnosis_metadata.get('knowledge_base_used'),
                        'prompt_length': diagnosis_metadata.get('prompt_length'),
                        'response_length': diagnosis_metadata.get('response_length'),
                        'diagnosis_method': 'RAG_PDF_BASED',
                        'ai_model_used': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                        'confidence_level': 'AI_GENERATED'
                    }
                }
                confidence_score = None

            storage_data = {
                'session_id': session_id,
                'user_id': user_id,
                'diagnosis_json': diagnosis_content,  # Store as JSONB directly
                'retrieved_papers': diagnosis_metadata.get('retrieved_sources', 0),
                'ai_model_used': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                'confidence_score': confidence_score,  # Numerical confidence score
                'knowledge_base_version': 'medical_pdfs_v1',
                'processing_time_seconds': None  # Could be extracted from metadata if available
            }

            # Store to Supabase in 'gait_diagnosis' table
            result = supabase.table('gait_diagnosis').insert(storage_data).execute()
            
            if result.data:
                stored_record = result.data[0]
                record_id = stored_record.get('id')
                state["diagnosis_record_id"] = record_id
                state["diagnosis_stored"] = True
                self.logger.info(f"Medical diagnosis stored successfully: Record ID {record_id}")
                return state
            else:
                error_info = getattr(result, 'error', 'Unknown error')
                return StateManager.set_error(state, f"Failed to store medical diagnosis: {error_info}", "storage_error")
            
        except Exception as e:
            error_msg = f"Medical diagnosis storage failed: {str(e)}"
            self.logger.error(error_msg)
            return StateManager.set_error(state, error_msg, "storage_execution_error")
    
    def _extract_confidence_score(self, diagnosis_result: dict) -> float:
        """Extract numerical confidence score from structured diagnosis"""
        try:
            if diagnosis_result.get("success") and "data" in diagnosis_result:
                data = diagnosis_result["data"]
                
                # Use the overall score as confidence (convert 0-100 to 0-1)
                score = data.get("score", 50)
                confidence = score / 100.0
                
                # Adjust based on risk level
                risk_level = data.get("riskLevel", "확인 필요")
                if risk_level == "정상 단계":
                    confidence = min(1.0, confidence + 0.1)
                elif risk_level == "위험 단계":
                    confidence = max(0.0, confidence - 0.2)
                
                return round(min(1.0, max(0.0, confidence)), 3)
            else:
                return 0.5  # Default confidence for failed analysis
                
        except Exception as e:
            self.logger.error(f"Error extracting confidence score: {str(e)}")
            return 0.5

class FormatResponseNode(BaseNode):
    """
    Node 12: Format final JSON response for API
    Aggregates all results into a structured output
    """
    
    def __init__(self):
        super().__init__(PipelineStages.FORMAT_RESPONSE)
    
    def get_system_prompt(self) -> str:
        return """You are an API response formatting specialist.
        Your task is to create a clean, structured, and developer-friendly JSON 
        response from the completed gait analysis pipeline state.
        
        The final JSON should include:
        - session_id for tracking
        - patient_info (date, height)
        - A summary of the gait analysis with key findings.
        - The full list of calculated gait_metrics.
        - The complete medical_diagnosis text.
        - Metadata about the diagnosis process (sources, model, etc.).
        - Clear recommendations for the user or clinician.
        """
    
    def execute(self, state: GraphState) -> GraphState:
        """Formats the final JSON response."""
        
        if not self.validate_state_requirements(state, ["session_id", "date", "height_cm", "gait_metrics", "medical_diagnosis"]):
            return StateManager.set_error(state, "Missing required fields for final response", "validation_error")
            
        start_time = state.get("start_time", datetime.now().isoformat())
        end_time = datetime.now()
        
        # Calculate processing time if start_time is a valid ISO format string
        try:
            processing_time = (end_time - datetime.fromisoformat(start_time)).total_seconds()
        except (TypeError, ValueError):
            processing_time = 0

        # Extract key findings for the summary
        gait_metrics = state.get("gait_metrics", {})
        key_findings = []
        if gait_metrics.get("avg_walking_speed", 1.2) < 1.0:
            key_findings.append("보행 속도 감소")
        if gait_metrics.get("stride_length_asymmetry", 0) > 5.0:
            key_findings.append("보폭 길이 비대칭성 증가")
        if gait_metrics.get("stride_time_cv", 0) > 5.0:
            key_findings.append("보행 안정성 저하 (시간적 변동성 증가)")
            
        if not key_findings:
            key_findings.append("전반적으로 정상 범위의 보행 패턴")

        final_response = {
            "session_id": state.get("session_id"),
            "patient_info": {
                "analysis_date": state.get("date"),
                "height_cm": state.get("height_cm")
            },
            "gait_analysis": {
                "summary": {
                    "primary_assessment": "정상 보행" if not key_findings or "정상" in key_findings[0] else "비정상 보행 패턴 감지",
                    "key_findings": key_findings,
                },
                "metrics": gait_metrics,
            },
            "medical_diagnosis": {
                "primary_diagnosis": state.get("medical_diagnosis"),
                "diagnosis_metadata": state.get("medical_diagnosis_metadata")
            },
            "recommendations": {
                "immediate_actions": ["결과를 바탕으로 전문가와 상담하세요."],
                "follow_up": ["6개월 후 정기적인 재평가 권장"]
            },
            "pipeline_metadata": {
                "processing_time_seconds": round(processing_time, 2),
                "metrics_record_id": state.get("metrics_record_id"),
                "diagnosis_record_id": state.get("diagnosis_record_id"),
            }
        }
        
        state['response'] = final_response
        state['processing_time'] = processing_time
        
        return state 
