# 프로젝트 설명서: EDR AI 트리아지 에이전트 실습

> 이 문서는 "이 프로젝트가 대체 무엇이고, 어떤 부품이 있고, 문서와 코드가 어떻게 연결되는지"를 한곳에 모은 설명서입니다.
> **무엇을 어떤 순서로 할지**는 [`START_HERE.md`](START_HERE.md)에 있습니다. 이 문서는 막힐 때 돌아와서 보는 지도입니다.

---

## 1. 한 문장 요약

회사 PC에서 수상한 일이 생겨 **경보(알림)** 가 울리면, **AI 에이전트가 PC 기록을 조사하고 회사 매뉴얼을 찾아본 뒤, 판정과 대응 권고를 쓰고, 위험한 조치는 사람의 승인을 기다리는** 서비스를 2인 1조로 3일 동안 만들고, 서버(k3s)에 직접 올려 일부러 고장 내 보며 운영까지 해 보는 실습입니다.

## 2. 왜 이런 걸 만드나 (배경 3줄)

- 보안관제센터(SOC)에는 알림이 하루 수천 건 오고, **대부분은 오탐**(정상인데 잘못 울린 것)입니다.
- 분석가는 매번 같은 조사를 반복합니다: 누가 실행했나 보기, 무엇을 남겼나 보기, 매뉴얼 찾기, 보고서 쓰기.
- 이 반복 조사를 AI가 1차로 하면 사람은 애매한 건과 승인에만 집중할 수 있습니다. 대신 AI는 틀릴 수 있으니 **근거 확인(가드레일), 사람 승인, 점수 측정** 세 가지 안전장치를 함께 만듭니다.

## 3. 부품: 비유와 실제 프로그램

| 비유 (01 문서) | 실제 부품 | 하는 일 | 코드 위치 |
|---|---|---|---|
| CCTV 녹화 | **시뮬레이터** | 가상 회사 PC 10대와 서버 2대(WS-001~010, SRV-DB-01, SRV-FILE-01)의 활동 기록을 만들어 냄 | `src/soc/simulator/` |
| 경보 규칙 | **탐지 룰** | 기록을 보다가 규칙에 걸리면 알림을 만듦 | `src/soc/detection/rules.py` |
| 녹화 보관함 | OpenSearch `edr-events-날짜` 인덱스 | 기록 저장, 검색 | `src/soc/telemetry/index_template.py` |
| 경보함 | OpenSearch `edr-alerts` 인덱스 | 처리를 기다리는 알림 (`status` 칸이 대기열 역할) | `src/soc/alerts.py` |
| 경비원 | **워커** (LangGraph 에이전트) | 알림을 하나씩 꺼내 조사, 판정, 권고 | `src/soc/worker.py`, `src/soc/agent/` |
| 경비 매뉴얼 | OpenSearch `kb-playbooks` 인덱스 | PDF 9종을 잘게 나눠 검색할 수 있게 넣어 둔 곳 | `src/soc/kb/` |
| 경비원의 수첩 | **Postgres** | 에이전트가 "어디까지 했는지" 저장. 승인을 기다렸다가 이어서 할 때 필요 | `src/soc/agent/checkpoint.py` |
| 팀장의 승인 창구 | **API** (FastAPI) | 승인, 거절, 알림·리포트 조회, Dify 연결 | `src/soc/api/` |

> **헷갈리기 쉬운 점:** 그림에는 "시뮬레이터"와 "탐지 프로그램"이 따로 그려져 있지만, 코드에서는 **한 프로그램**(`python -m soc.simulator.run`)이 기록을 넣고 바로 탐지까지 합니다. 서버에서도 `generator` Deployment 하나가 둘 다 합니다.

## 4. 알림 하나가 지나가는 길

```
[시뮬레이터] 기록 생성 ──► OpenSearch edr-events-*
      │ (같은 프로그램 안에서)
      └► [탐지 룰] 규칙에 걸림 ──► OpenSearch edr-alerts (status=new)
                                          │
[워커] new 알림을 가져감 (status=in_progress)
   └► 에이전트 그래프
        조사 ⇄ 도구        ← 🔍 기록 담당의 조사 도구 3개 (OpenSearch에서 기록 찾기)
        → 판정 (LLM)
        → 가드레일         ← 판정이 인용한 근거가 진짜 조회한 기록인지 기계적으로 검사
        → 권고             ← 📘 문서 담당의 플레이북 검색 (RAG)
        → 승인             ← 위험한 조치(격리 등)면 여기서 멈춤 (status=pending_approval, 상태는 Postgres에)
        → 리포트           ← OpenSearch triage-reports, status=completed
                                          ▲
[API] POST /approvals/{alert_id} ── 사람이 승인/거절 → 멈춘 곳부터 이어서 실행
```

## 5. 두 역할과 공동 작업

| | 🔍 기록 담당 | 📘 문서 담당 |
|---|---|---|
| 비유 | CCTV를 돌려 보는 사람 | 경비 매뉴얼을 펴 보는 사람 |
| 다루는 자료 | PC 활동 기록 (`data/telemetry/`, 시뮬레이터) | 정책·플레이북 PDF 9종 (`data/kb/pdf/`) |
| 혼자 만드는 것 | **조사 도구 3개**: 프로세스 족보, 프로세스 활동, 시간대별 기록 | **플레이북 검색(RAG)**: 파싱 → 청킹 → 임베딩 → 하이브리드 검색 |
| 검색 방식 | 조건이 정확한 검색 (host가 정확히 WS-007, 시간이 09:00~09:30) | 뜻으로 찾는 검색 ("LSASS 덤프면 누가 승인해?") |
| 성과를 재는 법 | 테스트 통과, 결과만 보고 사람이 판정할 수 있는가 | Recall@3 (정답 문서가 검색 상위 3개 안에 드는 비율) |
| 에이전트에서 쓰이는 곳 | 조사 노드 | 권고 노드 |

**같이 만드는 것:** 두 사람의 결과를 잇는 에이전트, 서버 인프라(0~7단계), 평가.
**바꿔서 해 보는 것:** 2일차와 3일차에 상대 영역에서 작은 작업을 하나씩 합니다. 발표 때 상대 영역도 설명해야 하기 때문입니다.

### 도구 호출과 RAG의 차이 (실습의 핵심 개념)

| | 도구 호출 (🔍) | RAG (📘) |
|---|---|---|
| 질문 모양 | "WS-007의 pid 40702의 부모는?" | "LSASS 덤프가 의심되면 어떻게 대응해?" |
| 찾는 방법 | 필터, 정렬 (term, range) | 키워드 검색 + 벡터 검색을 순위로 합침 (RRF) |
| 돌려주는 것 | 기록 (사실) | 문서 조각 (규칙, 지식) |
| 꼭 붙는 칸 | `event_id` (근거 추적용) | `source` 파일 이름 (출처 표시용) |

## 6. 3일 흐름 한눈에

| | 사전 | 1일차 | 2일차 | 3일차 |
|---|---|---|---|---|
| 목표 | 개념, 역할, 고장 예상 | 계약, 각자 검색 계층, 에이전트 뼈대 | 에이전트 완성, 점수 기준점, 서버 1~5단계 | 서버 6~7단계, 고도화, 발표 |
| 혼자 | 문서 읽기, 예시 알림 조사 | 🔍 조사 도구 / 📘 플레이북 검색 | | 고도화 |
| 함께 | 역할 정하기 | 계약, 인프라 0단계(내 PC), 뼈대 | 가드레일, 사람 승인, 평가, 인프라 1~5 | 인프라 6~7, Dify, 종합 드릴, 발표 |
| 상대 영역 | | | 교차 작업 1개씩 | 고도화 1개씩 |
| 실행 장소 | | **내 PC** (docker compose) | 내 PC → **팀 서버** (k3s) | 팀 서버 |

## 7. 코드에서 직접 채우는 곳 (TODO 전체 목록)

코드는 거의 다 만들어져 있고, 아래 자리만 `raise NotImplementedError("TODO[번호]")` 상태로 비어 있습니다. 파일을 열어 `TODO[`를 검색하면 채울 곳과 힌트가 나옵니다.
**이 TODO가 비어 있는 동안은 그 함수를 부르는 명령이 모두 `NotImplementedError`로 멈춥니다.** 이게 정상입니다.

| 번호 | 누가 | 언제 | 파일 | 내용 | 확인 방법 |
|---|---|---|---|---|---|
| REC-1 | 🔍 | 1일차 | `telemetry/index_template.py` | `edr-events-*` 인덱스 매핑 | 기록 적재가 성공, `test_mapping_types` |
| REC-2 | 🔍 | 1일차 | `telemetry/tools.py` | `get_process_tree` | `pytest tests/test_telemetry_tools.py` |
| REC-3 | 🔍 | 1일차 | 〃 | `get_process_activity` | 〃 |
| REC-4 | 🔍 | 1일차 | 〃 | `get_host_timeline` | 〃 |
| DOC-1 | 📘 | 1일차 | `kb/parse.py` | `partition()` 호출 | `python -m soc.kb.inspect` 가 돌아감 |
| DOC-2 | 📘 | 1일차 | 〃 | 머리말, 꼬리말 제거 | `ingest --dry-run`에 "대외비"가 안 보임 |
| DOC-3 | 📘 | 1일차 | `kb/chunk.py` | `chunk_by_title()` 호출 | `ingest --dry-run`이 돌아감 |
| DOC-4 | 📘 | 1일차 | `kb/index.py` | `kb-playbooks` 매핑 | `python -m soc.kb.ingest`가 저장까지 성공 |
| DOC-5 | 📘 | 1일차 | `kb/search.py` | RRF 결합 | `python -m soc.eval.rag_eval --mode all` |
| **AG-1** | 👥 운전 📘 | 1일차 | `agent/nodes.py` | 조사 노드 (🔍 도구를 LLM에 연결) | `pytest tests/test_graph_skeleton.py` |
| **AG-2** | 👥 운전 🔍 | 1일차 | 〃 | 권고 노드 (📘 검색 결과로 권고) | 〃 |
| **AG-3** | 👥 | 1일차 | `agent/graph.py` | 노드를 엣지로 잇기 | 〃, `python -m soc.agent.graph` |
| G-1 | 👥 운전 📘 | 2일차 | `agent/guardrail.py` | 인용한 근거가 실제 조회한 기록인가 | `pytest tests/test_guardrail.py` |
| G-2 | 👥 운전 📘 | 2일차 | 〃 | 악성 판정에 근거 2개 이상 | 〃 |
| H-1 | 👥 운전 🔍 | 2일차 | `agent/nodes.py` | 위험한 조치면 `interrupt()`로 멈춤 | `pytest tests/test_approval.py` |
| H-2 | 👥 운전 🔍 | 2일차 | `agent/checkpoint.py` | Postgres에 상태 저장 | API를 껐다 켜도 승인 후 이어짐 |
| DIFY-1 | 👥 | 3일차 | `api/dify.py` | 점수를 0~1로 바꾸기 | `pytest tests/test_dify.py` |

> AG-1~3은 원래 안내 문서(DAY1, 00_overview, WORK_SPEC) 표에 빠져 있었습니다. 코드와 테스트에는 있으므로 1일차 뼈대 단계에서 반드시 채워야 합니다.

## 8. 폴더 지도

```
edr-ai-triage-lab/
├─ START_HERE.md            ← 순서대로 따라 하는 단일 계획표 (새로 만듦)
├─ PROJECT_GUIDE.md         ← 이 문서 (새로 만듦)
├─ CHANGES.md               ← 원래 문서의 문제점과 바꾼 내용 (새로 만듦)
├─ README.md / README_CODE.md   원래 입구 문서, 코드 실행 안내
├─ .env.example             설정 견본 → 복사해서 .env로
├─ Dockerfile, Dockerfile.kb    앱 이미지, PDF 적재 전용 이미지 (2~3일차)
├─ data/
│  ├─ telemetry/sample_events.jsonl   🔍 샘플 기록 24줄 (WS-007 예시 알림 포함)
│  └─ kb/pdf/*.pdf, eval_questions.jsonl, README.md   📘 PDF 9종, 평가 질문 21개
├─ docs/
│  ├─ prep/      사전 자료 01, 01b, 02, 03
│  ├─ guide/     00_overview, DAY1~3, INFRA_STAGES(0~7단계), WORK_SPEC(체크리스트)
│  ├─ teachback/ 매일 마지막 서로 설명한 기록
│  └─ CONTRACT, ARCHITECTURE, DECISIONS, RUNBOOK, CAPACITY, DEPLOYMENT, POSTMORTEM   팀이 채우는 문서
├─ src/soc/      코드 (7장의 TODO 외에는 완성돼 있음)
└─ tests/        TODO마다 확인하는 테스트
```

**아직 없는 것 (직접 만드는 것):** `docker-compose.yml`(1일차), `infra/`(2~3일차 쿠버네티스 설정), `.github/workflows/ci.yml`(3일차).

## 9. 문서 지도: 무엇을 언제 보나

| 문서 | 성격 | 언제 보나 |
|---|---|---|
| `START_HERE.md` | **따라 하기** (한 장 계획표) | 항상 이것부터 |
| `docs/prep/01` | 개념: EDR, 용어 10개, 예시 알림 | 사전 |
| `docs/prep/01b` | 개념: 비유를 부품으로, 고장 나는 곳 | 사전 |
| `docs/prep/02` | 개념: 트러블슈팅 순서, 깨 보기 규칙, 런북 형식, 고장 예상표 | 사전, 장애 날 때마다 |
| `docs/prep/03` | 참고 링크와 "읽고 답할 질문" | 사전, 막힐 때 |
| `docs/guide/DAY1~3` | 원래 일차별 설명 (왜 하는지가 자세함) | START_HERE에서 "왜?"가 궁금할 때 |
| `docs/guide/INFRA_STAGES` | 인프라 단계별 요구사항과 깨 보기 문제 목록 | 인프라 단계마다 (가장 잘 정리된 문서) |
| `docs/guide/WORK_SPEC` | 작업 번호(P-1, D1-3 …)와 완료 기준 | 체크할 때 |
| `data/kb/README.md` | PDF 9종의 함정 설명 | 📘 1일차 |
| `README_CODE.md` | 명령 모음, `.env` 스위치 | 명령이 기억 안 날 때 |

## 10. `.env` 스위치: 언제 무엇으로

| 값 | 뜻 | 언제 바꾸나 |
|---|---|---|
| `BACKEND` | `memory`: OpenSearch, Postgres 없이 메모리 흉내 / `real`: 진짜 연결 | 내 PC: 인프라 0단계가 뜬 뒤 `real`. 서버: 1단계 첫 배포만 `memory`, 3단계부터 `real` |
| `TELEMETRY_TOOLS`, `KB_TOOLS` | `mock`: 가짜 도구 / `real`: 직접 만든 도구 | 2일차 D2-2에서 완성된 쪽부터 `real` |
| `FAKE_LLM` | `true`면 API 키 없이 가짜 LLM, 가짜 임베딩 | 흐름만 볼 때. **📘의 벡터 검색 점수는 가짜 임베딩이면 의미가 없습니다** |
| `OPENAI_API_KEY` | 진짜 LLM, 임베딩 | 📘 적재(`kb.ingest`)와 에이전트 실행부터 필요 |
| `CHECKPOINTER` | `auto`: BACKEND=real이면 Postgres / `memory` / `postgres` | 2일차 승인 실험. H-2 전에는 `auto`여도 경고를 찍고 메모리를 씁니다 |
| `GUARDRAIL_ON_FAIL` | `retry`: 한 번 더 조사 / `downgrade`: 바로 '의심'으로 | 2일차 D2-3에서 둘이 정함 |

## 11. 용어집 (실습에서 쓰는 말)

| 말 | 뜻 |
|---|---|
| 알림, 트리아지 | 경보, 그리고 그 경보가 진짜인지 1차로 가르는 일 |
| 오탐 | 정상인데 공격으로 잘못 울린 알림 |
| 텔레메트리 | PC가 남긴 활동 기록 (프로세스 실행, 통신, 파일, 레지스트리, 스크립트) |
| 프로세스 트리, 족보 | 누가 누구를 실행했는지 (`pid`가 자기 번호, `ppid`가 부모 번호) |
| 계약 | 두 사람이 정한 도구의 이름, 입력, 출력 모양. 지키면 서로 기다리지 않고 동시에 개발 가능 |
| mock, 가짜 도구 | 계약 모양대로 정해진 값만 돌려주는 대역 (`src/soc/mocks.py`) |
| 파싱, 청킹, 임베딩 | PDF를 글 조각으로 읽기, 검색 단위로 묶기, 숫자 벡터로 바꾸기 |
| RRF | 키워드 검색과 벡터 검색의 순위를 `1/(60+순위)`로 합치는 방법 |
| Recall@3 | 평가 질문 21개 중 정답 문서가 검색 상위 3개 안에 든 비율 |
| 가드레일 | LLM의 판정을 그대로 믿지 않고 코드로 검사하는 장치 |
| interrupt, 체크포인터 | 그래프를 멈추는 함수, 멈춘 상태를 저장하는 곳 (= 수첩, Postgres) |
| `thread_id` | 체크포인터 안에서 "어느 알림의 수첩 페이지인지" 구분하는 번호 (= 알림 id) |
| 운전 | 키보드를 잡는 사람. 깨 보기에서는 운전자가 **진단자** |
| 출제자, 진단자 | 깨 보기에서 장애를 몰래 넣는 사람, 찾는 사람 |
| 진단 후 나눔 | 깨 보기가 끝난 뒤 "어디서 오래 걸렸나, 나라면 어디부터, 다음엔 처음 칠 명령" 이야기하기 |
| 중간 나눔 | 1일차 개인 작업 절반쯤에서 서로 결과를 보여 주고 계약을 바꿀지 정하기 |
| 티치백 | 매일 마지막에 자기 영역을 상대에게 설명하고 질문 3개 받기 |
| 고장 예상표 | 사전에 "어디가 어떻게 망가질지" 미리 적어 두고, 실습 중 맞았는지 확인하는 표 |
| 런북 | 장애가 났을 때 증상, 확인 명령, 원인, 조치를 적은 기록 (`docs/RUNBOOK.md`) |
| 👤 👥 🔁 🔥 | 혼자, 짝과 함께, 상대 영역, 깨 보기 |

## 12. 평가 숫자의 뜻 (2일차 기준점, 3일차 최종)

| 숫자 | 명령 | 뜻 |
|---|---|---|
| RAG Recall@3 | `python -m soc.eval.rag_eval` | 검색이 정답 문서를 상위 3개 안에 가져왔나 |
| 판정 정확도 | `python -m soc.eval.agent_eval --n 12` | 에이전트 판정이 시뮬레이터 정답 라벨과 맞나 |
| 지어낸 근거 비율 | 〃 | 가드레일이 잡은 "조회하지 않은 근거" 비율 |
| 응답 속도, 알림당 비용 | 〃 | 알림 하나 처리 시간, 토큰 비용(USD) |

1일차에는 스캔본(k10), 차트(k12), 09번 복잡한 표(k15~k21) 문항이 틀리는 게 정상입니다. 3일차 고도화 과제입니다.
