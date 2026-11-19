# 🔍 기록 담당 인수인계와 발표 노트

> 🔍 김진홍이 2·3일차에 결석한다. 📘 최재우가 🔍 영역을 이어 가고 발표에서 대신 설명할 수 있게 11-19에 정리했다.
> 숫자는 모두 11-19 김진홍 Mac(docker compose의 OpenSearch·Postgres, 실습 데이터 3,161건)에서 잰 것이다.

## 1. 지금 상태 한눈에

| 작업 | 상태 | 어디에 |
|---|---|---|
| REC-1 인덱스 템플릿 | 끝 | `src/soc/telemetry/index_template.py`, `DECISIONS.md` "text vs keyword" |
| REC-2~4 조사 도구 3개 | 끝. 진짜 OpenSearch에서 테스트 8개 통과 | `src/soc/telemetry/tools.py` |
| AG-2 권고 노드 | 끝. 진짜 LLM과 진짜 검색으로 확인 | `src/soc/agent/nodes.py` `recommend()` |
| H-1 사람 승인 / H-2 Postgres 저장 | 끝. 테스트 3개 통과, 프로세스를 바꿔 이어 가는 실험까지 | `nodes.py` `approval()`, `src/soc/agent/checkpoint.py`, `DECISIONS.md` "사람 승인과 상태 저장" |
| D2-2 진짜 도구 연결 (🔍 쪽) | 확인. 판정 근거에 실제 event_id가 들어감 | `DECISIONS.md` 같은 절 |
| D2-8 청킹 교차 실험 | 끝. **최종 값은 📘가 정할 차례** | `DECISIONS.md` "청킹 값" 표 |
| D2-11 용량 산정 | 초안. **서버 실측과 📘 검토가 남음** | `docs/CAPACITY.md` |
| D3-4 고도화 후보 3개 | 준비 끝 | `DECISIONS.md` "고도화 선정"의 각자 후보 |
| 고장 예상표 | 1일차 확인까지 | `teachback/day1_step0_notes.md` 3장 |
| RUNBOOK [0-2] | 끝 (재발 방지, 고장 예상표 비교는 같이 검토 필요) | `docs/RUNBOOK.md` |

전체 테스트(11-19): **14개 통과, 5개 실패.** 실패는 가드레일 G-1·G-2(3개, 📘 운전)와 DIFY-1(2개, 👥)뿐이다.

## 2. 📘 최재우가 정하거나 해야 할 것

- [ ] **계약 변경 안건 4개** (D1-8 중간 나눔에서 못 정함). 정하면 `CONTRACT.md` 변경 이력에 적는다. "변경 없음"도 기록한다.
  1. `get_process_tree`의 자식 목록 상한 20개 (`CHILDREN_LIMIT`). explorer.exe처럼 자식이 많은 프로세스 대비
  2. `get_process_activity`에 `truncated` 칸 추가 (50건이 넘었는지 알려 줌)
  3. `get_host_timeline` 기본 창 10분 → 2~3분 (알림 하나 비용의 대부분이 이것. 아래 4장)
  4. 요약에 `parent_name` 추가 (WS-002 같은 오탐 판정의 핵심 근거)
- [ ] **청킹 최종 값:** `DECISIONS.md` 청킹 표의 "최종 결정 (📘)" 칸. 내 의견은 500이지만 결정은 📘
- [ ] **가드레일(G-1·G-2)과 실패 처리 방식:** 📘 운전. 주의할 점: 타임라인을 10분으로 부르면 `seen_event_ids`가 100개라, G-1을 만들어도 타임라인에 스쳐 간 기록을 근거로 대면 통과한다
- [ ] **용량 산정 확인:** 서버에서 `nproc`, `free -h`, `kubectl top nodes`를 재서 `CAPACITY.md`의 OS 칸과 vCPU 가정(4개)을 고치고 검토란에 이름
- [ ] **D2-7 `get_network_connections` 리뷰:** 원래 🔍가 리뷰하는데 내가 없다. 아래 체크리스트를 스스로 확인하거나 강사에게 리뷰를 부탁한다
  - 모든 검색에 `host` 조건이 있나 (다른 PC에 같은 IP·pid가 있다)
  - 결과의 기록마다 `event_id`가 있나 (가드레일이 씀)
  - 결과 개수 상한이 있고, 넘으면 알려 주나 (`truncated`)
  - docstring에 "언제 이 도구를 고르는지"가 있나 (주기적인 외부 통신이 의심될 때)
  - `CONTRACT.md` 표와 변경 이력, `src/soc/mocks.py`에 같이 추가했나
  - 실습 데이터로 돌려 보기: `phishing_macro_powershell`(sc-001 WS-010, sc-002 WS-009)이 주기적으로 외부와 통신하는 시나리오다

## 3. 인프라에서 🔍가 운전하던 단계 주의점

| 단계 | 주의점 |
|---|---|
| 2단계 OpenSearch | 힙과 메모리 limit은 `CAPACITY.md`(힙 2g, limit 4Gi). 힙 = limit이면 OOMKilled(깨 보기 2-2). 템플릿은 `python -m soc.telemetry.index_template`로 넣는다. 인덱스가 매핑 없이 만들어지면 host 검색이 0건이 된다 |
| 4단계 워커·생성기·프로브 | **워커와 API 모두 `CHECKPOINTER=postgres`여야 승인이 된다.** 워커가 멈춘 알림을 API가 이어 가는데, 둘은 다른 파드다(실험: memory면 410). 워커 liveness는 `/healthz`(하트비트, 9100 포트). 생성기를 켜 두면 2분마다 알림이 생겨 LLM 비용이 든다(하루 약 $3.4) |
| 7단계 CI | 테스트는 OpenSearch가 없으면 메모리 흉내로 돈다(`tests/conftest.py`). G-1·G-2·DIFY-1이 끝나기 전에는 실패 5개가 남아 CI가 빨갛다. 그 상태로 관문을 만들지, 아는 실패를 빼고 돌릴지 정한다 |

## 4. 🔍 영역에서 자주 칠 명령

```bash
python -m soc.simulator.run --load data/sim.jsonl      # 기록 3,161건 + 알림 22건 (여러 번 해도 중복 없음)
pytest tests/test_telemetry_tools.py -q                # 조사 도구 테스트 8개
python -m soc.telemetry.index_template                 # 실습용 템플릿 다시 넣기
python -m soc.worker --once                            # 알림 하나 처리 (격리 권고면 pending_approval로 멈춤)
psql postgresql://soc:soc@localhost:5432/soc -c "select thread_id, count(*) from checkpoints group by thread_id"
```

승인은 API(`uvicorn soc.api.main:app --port 8000`)를 띄운 뒤 `POST /approvals/{alert_id}`에 `{"approved": true, "approver": "SOC 팀장"}`을 보낸다. 조사 도구를 직접 불러 보려면:

```bash
python -c "from soc.telemetry.tools import get_process_tree as t; print(t('WS-006', 51765))"   # 함수를 바로 부름 (LLM용 도구는 TELEMETRY_TOOLS)
```

## 5. 발표 노트 (🔍 순서, 약 3분)

발표 순서 2번 "기록 쪽: 인덱스 설계, 조사 도구 설계(요약, 설명문), 고장 예상표 결과, 고도화 2개의 숫자"를 이 순서로 말하면 된다.

**① 인덱스 설계: 왜 이렇게 했나**
- 기록은 날짜별 인덱스(`edr-events-2026.11.16`)에 넣는다. 오래된 기록을 인덱스째 지울 수 있어서다. 인덱스가 매일 생기므로 매핑은 템플릿으로 미리 정했다.
- `dynamic: strict`라서 스키마에 없는 칸이 오면 거절한다. 오타 난 칸이 조용히 생기지 않게 하려는 것이다.
- **host, type, process.name은 keyword**: 통째로 맞춰 본다. text면 `WS-006`이 `ws`, `006`으로 쪼개진다. 실험: host term `WS-006` → 349건, `ws-006` → 0건.
- **명령줄, 스크립트, 파일 경로는 text + keyword 둘 다**: 단어로도 찾고(match "comsvcs.dll MiniDump" → 4건) 통째로도 맞춘다. text 칸에 통째로 term을 걸면 0건이다.
- 포기한 것: keyword 쪽은 1,024자가 넘으면 색인을 건너뛴다(가장 긴 명령줄은 319자).

**② 조사 도구: 무엇을 받아 무엇을 돌려주나**

| 도구 | 받는 것 | 돌려주는 것 | 상한 |
|---|---|---|---|
| `get_process_tree` | host, pid | 그 프로세스, 부모들(가까운 순, 최대 5단계), 자식들. 끊기면 `note` | 부모 5단계, 자식 20개 |
| `get_process_activity` | host, pid | 그 프로세스의 통신·파일·레지스트리·스크립트 기록(시간순) | 50건 |
| `get_host_timeline` | host, 기준 시각, 앞뒤 몇 분 | 그 PC의 모든 기록(시간순). 넘치면 기준 시각에 가까운 것만 + `truncated` | 100건 |

- 모든 기록에 `event_id`가 있다. 가드레일이 "판정 근거가 실제로 조회한 기록인가"를 검사하는 데 쓴다.
- **요약하는 이유:** LLM에 넘기는 글자 수가 곧 비용과 속도다. 명령줄은 120자까지만 넘긴다.
- **설명문(docstring)이 도구 선택을 정한다.** LLM은 설명을 읽고 고른다. 그래서 "언제 쓰는지"를 첫 줄에 적었다. 실제로 LSASS 알림에서 LLM은 족보 → 활동 → 타임라인 순으로 세 도구를 다 불렀다.
- **설계에서 고민한 함정 두 가지**
  - 같은 PC 안에서도 pid가 재사용된다. 가장 최근 기록을 부모로 고르면 나중에 같은 pid로 뜬 svchost.exe가 공격 rundll32의 부모가 된다. 그래서 "자식보다 먼저 생긴 것 중 가장 가까운 것"을 고른다.
  - 다른 PC에 같은 pid가 있다(실습 데이터에서 pid 21개). 모든 검색에 host 조건을 건다.

**③ 고장 예상표 결과**
- 예상 3개는 모두 데이터에 실제로 있었다: 부모 기록 없음(76%), 다른 PC의 같은 pid, event_id 순서 ≠ 시간 순서. 도구가 셋 다 막아서 고장은 안 났다.
- 예상 못 한 고장 두 가지: ① 같은 PC 안 pid 재사용(위 ②) ② **테스트가 실습용 템플릿을 덮어씀**. 템플릿 이름이 고정이라 pytest를 돌리면 실습 템플릿이 `test-edr-events-*` 패턴으로 바뀌어 있었다. 템플릿 이름을 인덱스 이름에서 가져오게 고쳤다.
- 도구 결과를 사람이 먼저 읽어 보니, 판정은 할 수 있지만 도구로 알 수 없는 것도 있었다: pid 668이 정말 lsass인지(lsass 기록 0건), 14분 전에 같은 PC에서 일어난 같은 공격.

**④ 숫자 (2일차 기준점이 나오면 채운다)**
- 알림 하나(LSASS 덤프, 진짜 LLM): 16.2초, LLM 4번, 입력 27,662토큰, $0.0047. 그중 타임라인 한 번이 29,112자다. 설명문에 "잘리면 minutes를 줄여 다시 부르라"고 썼지만 LLM은 다시 부르지 않았다.
- 청킹 교차 실험: 청크 300자에서만 k14(한국어 질문 → 영어 문서)를 맞혔다. `max_characters`만 키우면 청크가 안 바뀐다(`new_after_n_chars`가 먼저 닫음).
- 고도화 2개의 숫자: 3일차에 고른 것으로 채운다. 후보는 `DECISIONS.md` "고도화 선정"에 있다.

**예상 질문과 답**
- Q. 왜 Deployment가 아니라 StatefulSet인가(OpenSearch)? → 데이터를 가진 워크로드라 파드가 다시 만들어져도 같은 이름과 같은 디스크(PVC)를 다시 붙여야 한다.
- Q. 승인 대기 중에 서버가 꺼지면? → 상태가 Postgres 체크포인트에 있어서 다시 켜고 승인하면 승인 노드부터 이어 간다. 메모리 저장이면 410으로 실패한다(실험함).
- Q. 왜 승인 노드 앞에 DB 쓰기를 두면 안 되나? → 재개하면 멈췄던 노드가 처음부터 다시 실행된다. 쓰기가 두 번 일어난다.
- Q. 부모 기록이 없으면 도구가 뭘 돌려주나? → 예외 대신 지금까지 찾은 것과 `note`("부모 프로세스(pid 1653, explorer.exe)의 생성 기록이 없습니다")를 돌려준다. 이름은 자식 기록의 `parent_name`에서 가져온다.
