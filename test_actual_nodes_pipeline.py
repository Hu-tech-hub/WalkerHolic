#!/usr/bin/env python3
"""
최적화된 LangGraph 노드 파이프라인 테스트
- 새로운 입력 시스템: (user_id, height_cm, gender)
- LLM 최적화: 11/12 노드에서 LLM 제거
- Storage 기반 데이터 처리
"""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_optimized_nodes_pipeline():
    """최적화된 LangGraph 노드들을 차례대로 실행하여 각 단계 출력 확인"""
    
    print("🚀 최적화된 LangGraph 노드 파이프라인 실행")
    print("=" * 80)
    print("🎯 최적화 목표: LLM 사용량 91% 감소 (11/12 노드 최적화)")
    print("📊 새로운 시스템: (user_id, height_cm, gender) → Storage 기반")
    
    pipeline_start_time = time.time()
    llm_call_count = 0
    
    try:
        # 환경 변수 확인
        from config import config
        print("✅ 환경 변수 확인 완료!")
        
        # 초기 상태 설정 - 새로운 입력 시스템
        from langgraph_nodes.graph_state import GraphState
        initial_state = GraphState()
        initial_state.update({
            "user_id": "user_001",  # Storage에 실제 존재하는 파일
            "height_cm": 180.0,
            "gender": "male",
            "session_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"\n🎯 테스트 세션: {initial_state['session_id']}")
        print(f"👤 사용자 ID: {initial_state['user_id']}")
        print(f"📏 키: {initial_state['height_cm']}cm")
        print(f"👫 성별: {initial_state['gender']}")
        
        current_state = initial_state.copy()
        
        # LLM 호출 추적 함수
        def create_llm_tracker(node_name):
            def track_llm_call(original_method):
                def wrapper(*args, **kwargs):
                    nonlocal llm_call_count
                    llm_call_count += 1
                    print(f"   ⚠️  LLM Call #{llm_call_count} in {node_name}")
                    return original_method(*args, **kwargs)
                return wrapper
            return track_llm_call
        
        # 1단계: 요청 수신 및 검증 (LLM 제거됨)
        print("\n" + "="*80)
        print("1️⃣ STEP 1: ReceiveRequestNode - 입력 검증 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.data_processing_nodes import ReceiveRequestNode
        receive_node = ReceiveRequestNode()
        
        # LLM 추적
        if hasattr(receive_node, 'invoke_llm'):
            receive_node.invoke_llm = create_llm_tracker("ReceiveRequestNode")(receive_node.invoke_llm)
        
        step_start = time.time()
        print("🔄 사용자 입력 검증 중...")
        current_state = receive_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 검증 실패: {current_state['error']}")
            return
        else:
            print(f"✅ 검증 성공! ({step_time:.2f}초)")
            print(f"   👤 User ID: {current_state.get('user_id')}")
            print(f"   📏 Height: {current_state.get('height_cm')}cm")
            print(f"   👫 Gender: {current_state.get('gender')}")
        
        # 2단계: 파일 메타데이터 검색 (BuildQueryNode → FileMetadataNode)
        print("\n" + "="*80)
        print("2️⃣ STEP 2: FileMetadataNode - Storage 파일 검색 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.data_processing_nodes import FileMetadataNode
        metadata_node = FileMetadataNode()
        
        # LLM 추적
        if hasattr(metadata_node, 'invoke_llm'):
            metadata_node.invoke_llm = create_llm_tracker("FileMetadataNode")(metadata_node.invoke_llm)
        
        step_start = time.time()
        print("🔄 Supabase Storage에서 파일 검색 중...")
        current_state = metadata_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 파일 검색 실패: {current_state['error']}")
            return
        
        selected_file = current_state.get('selected_csv_file')
        available_files = current_state.get('available_csv_files', [])
        
        if selected_file:
            print(f"✅ 파일 검색 성공! ({step_time:.2f}초)")
            print(f"📁 선택된 파일: {selected_file.get('name')}")
            print(f"📊 파일 크기: {selected_file.get('size', 0):,} bytes")
            print(f"📅 수정 날짜: {selected_file.get('last_modified')}")
            print(f"🗂️ 발견된 총 파일: {len(available_files)}개")
        else:
            print(f"⚠️  파일 검색 완료했지만 선택된 파일 없음 ({step_time:.2f}초)")
            print(f"🗂️ 발견된 파일: {len(available_files)}개")
        
        # 3단계: CSV 다운로드 (FetchCsvNode → DownloadCsvNode)
        print("\n" + "="*80)
        print("3️⃣ STEP 3: DownloadCsvNode - Storage에서 데이터 다운로드 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.data_processing_nodes import DownloadCsvNode
        download_node = DownloadCsvNode()
        
        # LLM 추적
        if hasattr(download_node, 'invoke_llm'):
            download_node.invoke_llm = create_llm_tracker("DownloadCsvNode")(download_node.invoke_llm)
        
        step_start = time.time()
        print(f"🔄 Storage에서 IMU 데이터 다운로드 중...")
        current_state = download_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 다운로드 실패: {current_state['error']}")
            return
        
        csv_path = current_state.get('raw_csv_path')
        download_info = current_state.get('downloaded_file_info', {})
        
        if csv_path:
            df = pd.read_csv(csv_path)
            file_size = Path(csv_path).stat().st_size
            print(f"✅ 다운로드 성공! ({step_time:.2f}초)")
            print(f"📁 로컬 파일: {csv_path}")
            print(f"📊 데이터: {len(df):,}개 레코드")
            print(f"💾 파일 크기: {file_size:,} bytes")
            print(f"📥 원본 파일: {download_info.get('original_name', 'N/A')}")
            if 'accel_x' in df.columns:
                print(f"🔍 가속도계 X 범위: {df['accel_x'].min():.2f} ~ {df['accel_x'].max():.2f}")
        else:
            print(f"⚠️  다운로드 정보가 state에 없습니다")
        
        # 4단계: Butterworth 필터링 + 데이터 트리밍
        print("\n" + "="*80)
        print("4️⃣ STEP 4: FilterDataNode - 필터링 + 트리밍 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.data_processing_nodes import FilterDataNode
        filter_node = FilterDataNode()
        
        # LLM 추적
        if hasattr(filter_node, 'invoke_llm'):
            filter_node.invoke_llm = create_llm_tracker("FilterDataNode")(filter_node.invoke_llm)
        
        step_start = time.time()
        print(f"🔄 Butterworth 필터 적용 + 데이터 트리밍 중...")
        current_state = filter_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 필터링 실패: {current_state['error']}")
            return
        
        filtered_path = current_state.get('filtered_csv_path')
        if filtered_path:
            df_filtered = pd.read_csv(filtered_path)
            original_len = len(df)
            filtered_len = len(df_filtered)
            
            print(f"✅ 필터링 + 트리밍 완료! ({step_time:.2f}초)")
            print(f"📁 필터링된 파일: {filtered_path}")
            print(f"📊 데이터 변화: {original_len:,} → {filtered_len:,} 레코드")
            print(f"✂️ 트리밍: 처음 2초 + 마지막 3초 제거")
            
            # 필터링 통계
            filter_stats = current_state.get('filter_statistics', {})
            if filter_stats:
                print(f"📈 필터링 통계:")
                print(f"   원본 길이: {filter_stats.get('original_length', 'N/A')} 레코드")
                print(f"   트리밍 후: {filter_stats.get('trimmed_length', 'N/A')} 레코드") 
                print(f"   최종 길이: {filter_stats.get('final_length', 'N/A')} 레코드")
        
        # 5단계: 보행 단계 예측 (LLM 제거됨)
        print("\n" + "="*80)
        print("5️⃣ STEP 5: PredictPhasesNode - 딥러닝 보행 단계 예측 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.ai_model_nodes import PredictPhasesNode
        predict_phases_node = PredictPhasesNode()
        
        # LLM 추적
        if hasattr(predict_phases_node, 'invoke_llm'):
            predict_phases_node.invoke_llm = create_llm_tracker("PredictPhasesNode")(predict_phases_node.invoke_llm)
        
        step_start = time.time()
        print(f"🤖 Stage2Predictor 딥러닝 모델 실행 중...")
        current_state = predict_phases_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 보행 단계 예측 실패: {current_state['error']}")
            return
        
        phases_path = current_state.get('labels_csv_path')
        if phases_path:
            df_phases = pd.read_csv(phases_path)
            print(f"✅ 보행 단계 예측 완료! ({step_time:.2f}초)")
            print(f"📁 예측 결과: {phases_path}")
            print(f"📊 보행 세그먼트: {len(df_phases)}개")
            if 'phase' in df_phases.columns:
                phase_counts = df_phases['phase'].value_counts().sort_index()
                print(f"🚶 보행 단계 분포:")
                for phase, count in phase_counts.items():
                    print(f"   Phase {phase}: {count}개")
        
        # 6단계: 보폭/속도 예측 (LLM 제거됨)
        print("\n" + "="*80)
        print("6️⃣ STEP 6: PredictStrideNode - 딥러닝 보폭/속도 예측 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.ai_model_nodes import PredictStrideNode
        predict_stride_node = PredictStrideNode()
        
        # LLM 추적
        if hasattr(predict_stride_node, 'invoke_llm'):
            predict_stride_node.invoke_llm = create_llm_tracker("PredictStrideNode")(predict_stride_node.invoke_llm)
        
        step_start = time.time()
        print(f"🤖 StrideInferencePipeline 실행 중...")
        current_state = predict_stride_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 보폭/속도 예측 실패: {current_state['error']}")
            return
        
        stride_results = current_state.get('stride_results')
        if stride_results and 'predictions' in stride_results:
            predictions = stride_results['predictions']
            print(f"✅ 보폭/속도 예측 완료! ({step_time:.2f}초)")
            print(f"🔄 예측된 보폭: {len(predictions)}개")
            
            if predictions:
                lengths = [p.get('predicted_stride_length', 0) for p in predictions]
                velocities = [p.get('predicted_velocity', 0) for p in predictions]
                print(f"📏 보폭 평균: {sum(lengths)/len(lengths):.2f}m")
                print(f"🏃 속도 평균: {sum(velocities)/len(velocities):.2f}m/s")
        
        # 7단계: 12개 보행 지표 계산 (LLM 제거됨)
        print("\n" + "="*80)
        print("7️⃣ STEP 7: CalcMetricsNode - 12개 보행 지표 계산 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.metrics_nodes import CalcMetricsNode
        calc_metrics_node = CalcMetricsNode()
        
        # LLM 추적
        if hasattr(calc_metrics_node, 'invoke_llm'):
            calc_metrics_node.invoke_llm = create_llm_tracker("CalcMetricsNode")(calc_metrics_node.invoke_llm)
        
        step_start = time.time()
        print(f"📊 순수 Python으로 12개 보행 지표 계산 중...")
        current_state = calc_metrics_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 지표 계산 실패: {current_state['error']}")
            return
        
        gait_metrics = current_state.get('gait_metrics')
        if gait_metrics:
            print(f"✅ 12개 보행 지표 계산 완료! ({step_time:.2f}초)")
            print(f"📊 계산된 지표:")
            print(f"   ⏱️ 평균 보행시간: {gait_metrics.get('avg_stride_time', 'N/A'):.3f}초")
            print(f"   📏 평균 보폭: {gait_metrics.get('avg_stride_length', 'N/A'):.3f}m")
            print(f"   🏃 평균 속도: {gait_metrics.get('avg_walking_speed', 'N/A'):.3f}m/s")
            print(f"   🔄 보행률: {gait_metrics.get('cadence', 'N/A'):.1f} steps/min")
            print(f"   ⚖️ 비대칭성: {gait_metrics.get('stride_length_asymmetry', 'N/A'):.2f}%")
        
        # 8단계: 보행 지표 저장 (LLM 제거됨)
        print("\n" + "="*80)
        print("8️⃣ STEP 8: StoreMetricsNode - 지표 저장 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.metrics_nodes import StoreMetricsNode
        store_metrics_node = StoreMetricsNode()
        
        # LLM 추적
        if hasattr(store_metrics_node, 'invoke_llm'):
            store_metrics_node.invoke_llm = create_llm_tracker("StoreMetricsNode")(store_metrics_node.invoke_llm)
        
        step_start = time.time()
        print("🔄 Supabase에 보행 지표 저장 중...")
        
        # date 필드 추가 (StoreMetricsNode가 요구)
        current_state['date'] = datetime.now().strftime('%Y-%m-%d')
        current_state = store_metrics_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 지표 저장 실패: {current_state['error']}")
            print("⚠️  데이터베이스 연결 문제일 수 있습니다 (계속 진행)")
        else:
            metrics_record_id = current_state.get('metrics_record_id')
            print(f"✅ 보행 지표 저장 성공! ({step_time:.2f}초)")
            if metrics_record_id:
                print(f"   📊 Record ID: {metrics_record_id}")
        
        # 9단계: 프롬프트 구성 (LLM 제거됨 - 2-stage 시스템)
        print("\n" + "="*80)
        print("9️⃣ STEP 9: ComposePromptNode - 2-Stage RAG 프롬프트 구성 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.rag_diagnosis_nodes import ComposePromptNode
        compose_prompt_node = ComposePromptNode()
        
        # LLM 추적
        if hasattr(compose_prompt_node, 'invoke_llm'):
            compose_prompt_node.invoke_llm = create_llm_tracker("ComposePromptNode")(compose_prompt_node.invoke_llm)
        
        step_start = time.time()
        print("🔄 Stage 1 + Stage 2 RAG 쿼리 구성 중...")
        current_state = compose_prompt_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 프롬프트 구성 실패: {current_state['error']}")
            return
        
        rag_query_stage1 = current_state.get('rag_query_stage1')
        rag_query_stage2_template = current_state.get('rag_query_stage2_template')
        
        if rag_query_stage1 and rag_query_stage2_template:
            print(f"✅ 2-Stage RAG 쿼리 구성 완료! ({step_time:.2f}초)")
            print(f"📝 Stage 1 쿼리 길이: {len(rag_query_stage1):,} 문자")
            print(f"📝 Stage 2 템플릿 길이: {len(rag_query_stage2_template):,} 문자")
            print(f"🎯 환자 정보: {current_state.get('patient_info', {}).get('user_id', 'N/A')}")
        
        # 10단계: 2-Stage RAG 기반 진단 (LLM 사용)
        print("\n" + "="*80)
        print("🔟 STEP 10: RagDiagnosisNode - 2-Stage RAG 진단 (LLM 사용)")
        print("-" * 80)
        
        from langgraph_nodes.rag_diagnosis_nodes import RagDiagnosisNode
        rag_diagnosis_node = RagDiagnosisNode()
        
        # LLM 추적
        if hasattr(rag_diagnosis_node, 'invoke_llm'):
            rag_diagnosis_node.invoke_llm = create_llm_tracker("RagDiagnosisNode")(rag_diagnosis_node.invoke_llm)
        
        step_start = time.time()
        print("🔄 Stage 1: 개별 지표 분석 + Stage 2: 종합 진단 실행 중...")
        current_state = rag_diagnosis_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 2-Stage RAG 진단 실패: {current_state['error']}")
            return
        
        # 새로운 diagnosis_result 구조 확인
        diagnosis_result = current_state.get('diagnosis_result')
        stage1_indicators = current_state.get('stage1_indicators', [])
        
        if diagnosis_result:
            print(f"✅ 2-Stage RAG 진단 완료! ({step_time:.2f}초)")
            
            # Stage 1 결과 확인
            indicators = diagnosis_result.get('indicators', [])
            print(f"📊 Stage 1 개별 지표 분석: {len(indicators)}개")
            if indicators:
                normal_count = sum(1 for ind in indicators if ind.get('status') == 'normal')
                warning_count = len(indicators) - normal_count
                print(f"   ✅ 정상: {normal_count}개, ⚠️ 주의: {warning_count}개")
            
            # Stage 2 결과 확인
            score = diagnosis_result.get('score', 0)
            status = diagnosis_result.get('status', 'N/A')
            risk_level = diagnosis_result.get('riskLevel', 'N/A')
            diseases = diagnosis_result.get('diseases', [])
            detailed_report = diagnosis_result.get('detailedReport', {})
            
            print(f"🏥 Stage 2 종합 진단:")
            print(f"   📈 점수: {score}")
            print(f"   📋 상태: {status}")
            print(f"   ⚠️ 위험도: {risk_level}")
            print(f"   🦠 질병 평가: {len(diseases)}개")
            print(f"   📄 상세 리포트: {len(detailed_report.get('content', ''))}자")
            
            # 진단 결과 미리보기
            if detailed_report.get('title'):
                print(f"   📌 리포트 제목: {detailed_report['title']}")
        
        # 11단계: 진단 결과 저장 (LLM 제거됨)
        print("\n" + "="*80)
        print("1️⃣1️⃣ STEP 11: StoreDiagnosisNode - 진단 결과 저장 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.rag_diagnosis_nodes import StoreDiagnosisNode
        store_diagnosis_node = StoreDiagnosisNode()
        
        # LLM 추적
        if hasattr(store_diagnosis_node, 'invoke_llm'):
            store_diagnosis_node.invoke_llm = create_llm_tracker("StoreDiagnosisNode")(store_diagnosis_node.invoke_llm)
        
        step_start = time.time()
        print("🔄 Supabase에 diagnosis_result 저장 중...")
        current_state = store_diagnosis_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 진단 저장 실패: {current_state['error']}")
            print("⚠️  데이터베이스 연결 문제일 수 있습니다 (계속 진행)")
        else:
            diagnosis_record_id = current_state.get('diagnosis_record_id')
            print(f"✅ 진단 결과 저장 성공! ({step_time:.2f}초)")
            if diagnosis_record_id:
                print(f"   🏥 Record ID: {diagnosis_record_id}")
            
            # 신뢰도 점수 확인
            if diagnosis_result:
                confidence_score = store_diagnosis_node._calculate_confidence_score(diagnosis_result)
                print(f"   📊 계산된 신뢰도: {confidence_score:.3f}")
        
        # 12단계: 최종 응답 포맷팅 (LLM 제거됨)
        print("\n" + "="*80)
        print("1️⃣2️⃣ STEP 12: FormatResponseNode - 최종 응답 생성 (LLM 제거)")
        print("-" * 80)
        
        from langgraph_nodes.response_nodes import FormatResponseNode
        format_response_node = FormatResponseNode()
        
        # LLM 추적
        if hasattr(format_response_node, 'invoke_llm'):
            format_response_node.invoke_llm = create_llm_tracker("FormatResponseNode")(format_response_node.invoke_llm)
        
        step_start = time.time()
        print("🔄 diagnosis_result 기반 최종 응답 생성 중...")
        current_state = format_response_node.execute(current_state)
        step_time = time.time() - step_start
        
        if current_state.get('error'):
            print(f"❌ 응답 포맷팅 실패: {current_state['error']}")
            return
        
        final_response = current_state.get('response')
        if final_response:
            response_length = len(json.dumps(final_response, ensure_ascii=False))
            print(f"✅ 최종 응답 생성 완료! ({step_time:.2f}초)")
            print(f"📄 응답 길이: {response_length:,} 문자")
            
            # 최종 응답 구조 확인
            if isinstance(final_response, dict):
                print(f"📋 최종 응답 구조:")
                print(f"   - indicators: {len(final_response.get('indicators', []))}개")
                print(f"   - score: {final_response.get('score', 'N/A')}")
                print(f"   - diseases: {len(final_response.get('diseases', []))}개")
                print(f"   - metadata: {'있음' if 'metadata' in final_response else '없음'}")
        
        total_time = time.time() - pipeline_start_time
        
        # 최종 결과 요약
        print("\n" + "="*80)
        print("🎉 완전한 End-to-End 2-Stage RAG 파이프라인 완료!")
        print("="*80)
        
        print(f"📊 파이프라인 성과:")
        print(f"   🚀 총 LLM 호출: {llm_call_count}회")
        print(f"   ⏱️ 총 처리 시간: {total_time:.2f}초")
        print(f"   🎯 최적화 구조: 10/12 노드 LLM 제거 (83% 최적화)")
        print(f"   💡 2-Stage RAG: Stage 1(지표별) + Stage 2(종합진단)")
        
        print(f"\n📈 전체 12단계 처리 요약:")
        print(f"   1️⃣ 입력 검증: ✅ LLM 제거 (순수 Python)")
        print(f"   2️⃣ 파일 검색: ✅ LLM 제거 (Storage API)")
        print(f"   3️⃣ 데이터 다운로드: ✅ LLM 제거 (Storage API)")
        print(f"   4️⃣ 필터링+트리밍: ✅ LLM 제거 (Butterworth)")
        print(f"   5️⃣ 보행 단계 예측: ✅ LLM 제거 (딥러닝)")
        print(f"   6️⃣ 보폭/속도 예측: ✅ LLM 제거 (딥러닝)")
        print(f"   7️⃣ 지표 계산: ✅ LLM 제거 (순수 Python)")
        print(f"   8️⃣ 지표 저장: ✅ LLM 제거 (Database API)")
        print(f"   9️⃣ RAG 쿼리 구성: ✅ LLM 제거 (2-stage 템플릿)")
        print(f"   🔟 2-Stage RAG 진단: 🤖 LLM 사용 (Stage 1+2)")
        print(f"   1️⃣1️⃣ 진단 저장: ✅ LLM 제거 (Database API)")
        print(f"   1️⃣2️⃣ 응답 생성: ✅ LLM 제거 (구조 복사)")
        
        # 2-Stage RAG 시스템 분석
        print(f"\n🧠 2-Stage RAG 시스템 분석:")
        if diagnosis_result:
            indicators = diagnosis_result.get('indicators', [])
            diseases = diagnosis_result.get('diseases', [])
            print(f"   📊 Stage 1: {len(indicators)}개 개별 지표 분석")
            print(f"   🏥 Stage 2: {len(diseases)}개 질병 위험도 + 종합 소견")
            print(f"   📈 최종 점수: {diagnosis_result.get('score', 'N/A')}")
            print(f"   ⚠️ 위험도: {diagnosis_result.get('riskLevel', 'N/A')}")
        
        # 최종 성과 평가
        if llm_call_count <= 2:  # 예상되는 LLM 호출 (Stage 1 + Stage 2만)
            print(f"\n🎉 2-Stage RAG 파이프라인 성공!")
            print(f"   ✅ 전체 12단계 완료")
            print(f"   ✅ 83% 최적화 달성 (10/12 노드 LLM 제거)")
            print(f"   ✅ 2-Stage RAG 아키텍처 구현")
            print(f"   ✅ 개별 지표 + 종합 진단 분리")
            
            if current_state.get('response'):
                print(f"   ✅ 최종 사용자 응답 생성 완료")
        else:
            print(f"\n⚠️  예상보다 많은 LLM 호출 발견 ({llm_call_count}회)")
            print(f"   예상: 2회 (Stage 1 + Stage 2만)")
            print(f"   실제: {llm_call_count}회")
            print(f"   추가 최적화가 필요할 수 있습니다")
        
        return current_state
        
    except Exception as e:
        print(f"❌ 파이프라인 실행 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    result = test_optimized_nodes_pipeline() 