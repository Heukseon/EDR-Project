# 여기서 시작: 3일 실습 한 장 계획표

> **이 문서 하나만 위에서 아래로 따라가면 됩니다.** 단계마다 누가, 무엇을, 어떤 명령으로, 어디에 기록하는지와 끝났다는 기준을 함께 적었습니다.
> 다른 문서는 "더 알고 싶을 때"만 봅니다. 프로젝트가 무엇인지는 [`PROJECT_GUIDE.md`](PROJECT_GUIDE.md), 원래 문서에서 고친 점은 [`CHANGES.md`](CHANGES.md)에 있습니다.

**표시:** 👤 혼자 · 👥 짝과 함께 · 🔁 상대 영역 · 🔥 깨 보기 · 🔍 기록 담당 · 📘 문서 담당
**번호:** 단계 번호(P-1, D1-3 …)는 `docs/guide/WORK_SPEC.md`, 노션 팀 페이지 체크리스트와 같습니다. 끝낸 단계는 노션에서 체크하세요.
**명령:** 모든 명령은 프로젝트 맨 위 폴더(`edr-ai-triage-lab`)에서, 가상환경을 켠 상태로 칩니다.

---

## 전체 지도

| 구간 | 단계 | 어디서 |
|---|---|---|
| [0. 사전 준비](#0-사전-준비-실습-전날까지) | P-1 ~ P-9 | 혼자 읽기 + 짝과 역할 정하기 |
| [1. 개발 환경 준비](#1-개발-환경-준비-1일차-시작-전-둘-다) | E-1 ~ E-4 | 내 PC |
| [2. 1일차](#2-1일차-계약-각자-검색-계층-에이전트-뼈대) | D1-1 ~ D1-15 | 내 PC (docker compose) |
| [3. 2일차](#3-2일차-에이전트-완성-점수-서버-15단계) | D2-1 ~ D2-17 | 내 PC → 팀 서버 (k3s) |
| [4. 3일차](#4-3일차-서버-67단계-고도화-발표) | D3-1 ~ D3-13 | 팀 서버 |
| [5. 막혔을 때](#5-막혔을-때-자주-나는-오류) | | |

---

## 0. 사전 준비 (실습 전날까지)

| 단계 | 형태 | 할 일 | 남길 것 (개인 노트, 노션 등) | 끝 기준 |
|---|---|---|---|---|
| P-1 | 👤 | `docs/prep/01` 1~5장 읽기 | | 예시 알림을 ① 조사 ~ ⑤ 리포트 순서로 말할 수 있다 |
| P-2 | 👥 | `01` 6장: 역할 정하기 (🔍 / 📘) | | 둘 다 자기 역할이 무엇을 만드는지 안다 |
| P-3 | 👤 | `01` 6장: 내 역할 질문 조사 | 정리 칸, 출처 2개 이상 | 상대에게 설명하고 질문 1개에 답했다 |
| P-4 | 👥 | `01` 6장: 빈칸 ①~④ 채우기 | 빈칸 | 예시 답과 비교했다 |
| P-5 | 👤 | `docs/prep/01b` 읽기 | | "경비원의 수첩"이 Postgres라는 걸 안다 |
| P-6 | 👤 | `docs/prep/02` 1~4장 읽기 (5~8장은 훑기만) | | 트러블슈팅 7단계 순서를 말할 수 있다 |
| P-7 | 👤 | `02` 9-1: 장애 신고 풀기 | 풀이 | 문제 정의 → 관찰 → 가설 → 검증 순서로 풀었다 |
| P-8 | 👤 | `02` 9-2: 내 역할의 **고장 예상표** 2줄 이상 | 예상표 | 실제 자료(🔍 `sample_events.jsonl`, 📘 PDF 03·06·09)를 열어 보고 썼다 |
| P-9 | 👤 | `docs/prep/03` '지금 읽기' 3개 (내 역할 2개 + LangGraph Interrupts) | 링크별 답 메모 | "실습에서 어디에 쓸까" 한 줄까지 |

> `02` 맨 끝 셀프 체크는 지금 하지 않습니다. 2일차 D2-9에서 합니다.

---

## 1. 개발 환경 준비 (1일차 시작 전, 둘 다)

원래 이 내용은 `README_CODE.md`에만 있고 읽는 순서에 빠져 있었습니다. **1일차 첫 명령 전에 반드시 끝내야 합니다.**

### E-1. 필요한 프로그램
| 프로그램 | 확인 명령 | 비고 |
|---|---|---|
| Python 3.11 이상 | `python --version` | |
| Docker Desktop (또는 Docker Engine) | `docker compose version` | 1일차 인프라 0단계에 필요 |
| Git | `git --version` | |
| curl | Windows PowerShell에서는 `curl.exe` 로 칩니다 | PowerShell의 `curl`은 다른 명령입니다 |

### E-2. 가상환경과 패키지
```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate        macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt           # 둘 다
pip install -e .                          # 둘 다: python -m soc.… 명령이 soc 패키지를 찾게 함
pip install -r requirements-kb.txt        # 📘만: PDF 파싱(Unstructured). 무거워서 오래 걸림
```
- 📘 참고: 1일차의 `fast` 파싱은 추가 프로그램이 필요 없습니다. `hi_res`, `ocr_only`(3일차 고도화)는 poppler와 Tesseract(한국어 데이터 포함)를 PC에 따로 설치해야 합니다. 설치 목록은 `Dockerfile.kb`에 있습니다.

### E-3. 설정 파일 `.env`
```bash
cp .env.example .env        # Windows: copy .env.example .env
```
1일차에 쓰는 값만 보면 됩니다.

| 값 | 1일차 값 | 이유 |
|---|---|---|
| `BACKEND` | `real` | D1-3에서 띄운 OpenSearch, Postgres를 씀. **D1-3 전에는 OpenSearch가 필요한 명령을 치지 마세요** |
| `TELEMETRY_TOOLS`, `KB_TOOLS` | `mock` | 1일차 에이전트 뼈대는 가짜 도구로 (2일차에 `real`) |
| `OPENAI_API_KEY` | 강사에게 받은 키 | 📘 D1-11 적재(임베딩)부터 필요. 테스트는 키 없이 돌아감 |
| `FAKE_LLM` | `false` | `true`면 키 없이 돌지만 📘 **벡터 검색 점수가 의미 없어짐** (가짜 임베딩) |

`.env`는 절대 커밋하지 않습니다 (`.gitignore`에 들어 있음).

### E-4. 동작 확인
```bash
pytest -q
```
**실패가 많이 나오는 게 정상입니다.** 아직 채우지 않은 TODO 자리가 `NotImplementedError("TODO[번호]")`를 내기 때문입니다. `ModuleNotFoundError: soc`가 나오면 `pip install -e .`를 빼먹은 것입니다.

---

## 2. 1일차: 계약, 각자 검색 계층, 에이전트 뼈대

**오늘 끝났을 때:** 🔍 `get_process_tree()`가 족보를 돌려준다 · 📘 한국어 질문으로 `search_playbook()`이 플레이북 조각을 돌려준다 · 👥 내 PC에서 OpenSearch와 Postgres가 뜨고, 에이전트 뼈대가 끝까지 흐른다.

```
D1-1 시작 전 확인 → D1-2 계약 → D1-3 인프라 0단계
   → [혼자] 🔍 D1-4, D1-5   |   📘 D1-6, D1-7
   → D1-8 중간 나눔
   → [혼자] 🔍 D1-9, D1-10  |   📘 D1-11, D1-12
   → D1-13 설계 → D1-14 뼈대 → D1-15 티치백
```

### D1-1. 👥 시작 전 확인 (5분)
1. `docs/teachback/day1.md` 맨 위에 역할을 적습니다: `🔍 기록 담당: 이름  📘 문서 담당: 이름`
2. 서로의 P-9 링크 메모를 1분씩 소개합니다. 상대는 내 링크를 안 읽었으니 처음 듣는 사람도 알아듣게.
3. 공통 질문 "그래프가 승인을 기다리며 멈춰 있는 동안 진행 상황은 어디에 저장될까?"에 둘이 한 문장으로 답합니다.
   - 답의 방향: **체크포인터**에 `thread_id`(알림 id)별로 저장되고, 우리 실습에서는 그게 **Postgres = 경비원의 수첩**이다.
4. P-8 고장 예상표를 각자 화면에 열어 둡니다. 오늘 🔍 D1-10, 📘 D1-6에서 맞았는지 확인합니다.

✅ 둘 다 "도구 호출(🔍)은 정확한 조건으로 **기록**을 찾고, RAG(📘)는 뜻으로 **문서 조각**을 찾는다"를 자기 말로 설명할 수 있다.

### D1-2. 👥 도구 계약 정하기
**왜:** 계약(이름, 입력, 출력 모양)을 먼저 정하면, 상대 도구가 아직 없어도 가짜(mock)를 쓰며 둘이 **동시에** 개발할 수 있습니다.

1. `src/soc/mocks.py`를 함께 엽니다. 가짜 도구 4개가 돌려주는 모양이 곧 계약의 견본입니다.
2. `docs/CONTRACT.md` 표를 채웁니다. 칸마다 mocks.py에서 읽은 것을 옮기면 됩니다.

| 도구 | 만드는 사람 | 입력 | 출력에 꼭 있는 칸 (mocks.py 기준) |
|---|---|---|---|
| `get_process_tree(host, pid)` | 🔍 | PC 이름, 프로세스 번호 | `host`, `pid`, `process`, `ancestors`, `children`, 기록마다 `event_id` |
| `get_process_activity(host, pid)` | 🔍 | PC 이름, 프로세스 번호 | `host`, `pid`, `events`, 기록마다 `event_id` |
| `get_host_timeline(host, around_ts, minutes)` | 🔍 | PC 이름, 기준 시각, 앞뒤 몇 분 | `host`, `from`, `to`, `events`, `truncated`, 기록마다 `event_id` |
| `search_playbook(query, k)` | 📘 | 질문, 몇 개 | 조각마다 `source`, `page`, `category`, `text`, `score` |

3. "결과 개수 상한", "실패하면" 칸은 코드 주석을 참고해 정합니다 (예: 타임라인 최대 100건, 넘으면 `truncated: true`).
4. **꼭 합의할 두 가지:** 🔍 모든 기록에 `event_id` (가드레일이 근거를 검사), 📘 모든 조각에 `source` (권고에 출처를 붙임).
5. 둘 다 이름을 적습니다.

✅ `CONTRACT.md`에 둘의 이름이 있다. 앞으로 계약을 바꾸려면 상대에게 먼저 말하고 "변경 이력"에 적는다.

### D1-3. 👥 🔥 인프라 0단계: 내 PC에서 OpenSearch, Postgres 띄우기
**운전(키보드, 진단자): 🔍 · 출제자: 📘** · 자세한 요구사항: `docs/guide/INFRA_STAGES.md` 0단계

**만들 것:** 프로젝트 맨 위에 `docker-compose.yml`을 **직접** 작성합니다.
- OpenSearch 단일 노드: 보안 플러그인 끄기, 힙 1GB, 포트 9200, 데이터 볼륨
- OpenSearch Dashboards: 포트 5601
- Postgres 16: 사용자 `soc`, 비밀번호 `soc`, DB `soc`, 포트 5432, 데이터 볼륨 (`.env`의 `POSTGRES_DSN`과 맞춰야 함)

<details>
<summary>막혔을 때만 펼치기: 참고 예시 (먼저 직접 써 보세요. 이 예시는 실행 검증을 하지 않았습니다)</summary>

```yaml
services:
  opensearch:
    image: opensearchproject/opensearch:2.17.1
    environment:
      - discovery.type=single-node
      - DISABLE_SECURITY_PLUGIN=true
      - DISABLE_INSTALL_DEMO_CONFIG=true
      - OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g
    ports: ["9200:9200"]
    volumes: [osdata:/usr/share/opensearch/data]
  dashboards:
    image: opensearchproject/opensearch-dashboards:2.17.1
    environment:
      - 'OPENSEARCH_HOSTS=["http://opensearch:9200"]'
      - DISABLE_SECURITY_DASHBOARDS_PLUGIN=true
    ports: ["5601:5601"]
    depends_on: [opensearch]
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: soc
      POSTGRES_PASSWORD: soc
      POSTGRES_DB: soc
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
volumes:
  osdata:
  pgdata:
```
</details>

**띄우기와 확인** (원래 문서의 `jq`, `psql`은 Windows에 기본으로 없어서 바꿨습니다)
```bash
docker compose up -d
docker compose ps                                          # 셋 다 running
curl.exe -s http://localhost:9200/_cluster/health          # "status":"green" 또는 "yellow"
docker compose exec postgres psql -U soc -c "select 1"     # 1이 나오면 성공
```

**🔥 깨 보기 (처음이니 규칙부터)**
1. 둘이 `INFRA_STAGES.md`의 "깨 보기 규칙"을 함께 읽습니다.
2. 출제자(📘)가 아래에서 하나를 골라 종이에 적어 뒤집고 몰래 넣습니다. 진단자(🔍)는 관찰 → 가설 → 검증을 소리 내 말하며 찾습니다.

| # | 넣는 장애 | 단서 | 비고 |
|---|---|---|---|
| 0-2 | 5432 포트를 다른 컨테이너가 먼저 쓰게 하기 (`docker compose down` 후 `docker run -d --name pg-block -p 5432:5432 -e POSTGRES_PASSWORD=x postgres:16`, 그다음 `docker compose up -d`) | `port is already allocated` | **Windows에서 가장 하기 쉬움, 추천** |
| 0-1 | 앱 컨테이너의 `OPENSEARCH_URL`을 `localhost`로 | 컨테이너 안의 localhost는 자기 자신 | 선택 항목인 앱 컨테이너를 만든 경우만 |
| 0-3 | `vm.max_map_count`를 65530으로 | OpenSearch 로그 `max virtual memory areas` | Linux 전용 |

3. 찾으면 **진단 후 나눔**: 진단자는 가장 오래 걸린 지점, 출제자는 "나라면 어디부터", 둘이 "다음에 처음 칠 명령 하나"를 정합니다.
4. `docs/RUNBOOK.md`에 기록합니다. 템플릿의 "공통 1차 확인"은 쿠버네티스(2일차) 명령이라, 오늘은 대신 `docker compose ps`, `docker compose logs <서비스 이름>`을 적으세요.
5. 복구한 뒤(`docker rm -f pg-block` 등) 다시 위의 확인 명령이 통과하는지 봅니다.

✅ 둘 다 자기 PC에서 `curl.exe localhost:9200`에 응답이 오고, 깨 보기 1개가 진단 후 나눔까지 `RUNBOOK.md`에 있다.
**말로 설명하기:** 볼륨이 없으면 `docker compose down` 뒤에 무슨 일이 생기나?

---

### 개인 작업 전반 (👤 혼자, 상대 도구가 필요하면 mocks.py)

먼저 끝난 사람은 상대 역할의 `03` 문서 '지금 읽기' 링크를 하나 읽으며 기다립니다.

#### 🔍 D1-4. 데이터 관찰
```bash
python -m soc.simulator.run --dump data/sim.jsonl
# → data/sim.jsonl (기록) 과 data/sim_labels.jsonl (정답 라벨) 이 생김
```
1. `data/sim_labels.jsonl`에서 `"name": "credential_dump"` 줄을 찾아 `event_ids`를 봅니다.
2. 그 `event_id`들을 `data/sim.jsonl`에서 찾아 **시간순(`ts`)으로** 나열합니다. (VS Code에서 열고 Ctrl+F)
3. `process.ppid`(부모 번호)를 같은 `host`의 `process.pid`에서 찾아 족보를 거슬러 올라갑니다.
4. `docs/DECISIONS.md` "🔍 데이터 관찰"에 족보와 눈에 띈 점을 적습니다.

✅ `credential_dump`의 족보를 pid → ppid로 따라갔다.

#### 🔍 D1-5. 텔레메트리 인덱스 매핑 (TODO[REC-1])
✏️ `src/soc/telemetry/index_template.py`의 `properties`를 채웁니다.
- **칸 이름은 `src/soc/schema.py`의 `Event`에서 빠짐없이 가져옵니다.** 템플릿이 `dynamic: strict`라 매핑에 없는 칸이 하나라도 있으면 OpenSearch가 기록을 통째로 거절합니다.
- 검색·필터 칸(`host`, `type`, `process.name` 등)은 `keyword`, 시간 `ts`는 `date`, 번호·포트·바이트는 `long`, IP는 `ip`, 참/거짓은 `boolean`.
- 명령줄(`process.cmdline`)과 스크립트(`script_text`)는 `text` + 하위 `keyword` 둘 다 (`fields` 사용).
- 중첩 칸(`process`, `network`, `file`, `registry`)은 `{"properties": {...}}`로 감쌉니다.

```bash
# 원래 문서의 "시뮬레이터를 OpenSearch 모드로"는 실제로는 이 명령입니다
python -m soc.telemetry.index_template --load data/sim.jsonl
# → "템플릿 적용 완료", "N건 넣음 → 전체 N건"
python -m soc.telemetry.index_template --load data/telemetry/sample_events.jsonl
# → 샘플 24줄도 넣어 둡니다 (D1-10에서 01 문서의 예시 알림 WS-007, pid 40702를 직접 조회할 때 씀)
```
- 거절되면 오류에 "어느 칸이 매핑에 없는지" 나옵니다. 그 칸을 추가하고 다시 실행합니다.
- `DECISIONS.md` "text vs keyword"에 왜 둘을 나눴는지 한 줄. (힌트: `text`는 단어로 쪼개고 소문자로 바꿔 저장해서 `WS-007`을 정확히 일치로 찾을 수 없다)

✅ 기록이 들어갔고 전체 개수를 확인했다.

#### 📘 D1-6. 9개 PDF를 그냥 파싱해 보기
> **순서 주의 (원래 문서의 오류):** 원래 안내는 "제공 스크립트로 그냥 파싱해 보기"가 먼저지만, 그 스크립트(`soc.kb.inspect`)는 내부에서 TODO[DOC-1] 함수를 부릅니다. 그래서 **DOC-1을 먼저** 채워야 돌아갑니다.

1. `data/kb/README.md`를 읽습니다 (PDF마다 일부러 넣은 함정).
2. ✏️ **TODO[DOC-1]** `src/soc/kb/parse.py`의 `parse_pdf()`: `partition(filename=..., strategy=strategy, languages=["kor", "eng"], infer_table_structure=True)` 형태로 호출해 결과를 돌려줍니다.
3. 실행합니다.
   ```bash
   python -m soc.kb.inspect --strategy fast                       # 파일별 요소 수와 종류
   python -m soc.kb.inspect --strategy fast --file 03 --show 10   # 03번 요소 10개를 눈으로 보기
   ```
4. `docs/DECISIONS.md` "📘 파싱 관찰" 표에 파일마다 요소 수, 깨진 것, 고를 파싱 방법을 적습니다. (`data/kb/README.md`의 "제작 시 측정한 결과"와 비교)
5. 고장 예상표 확인: 03(머리말), 06(스캔본, 요소 0개가 정상), 09(표가 Title 조각으로 흩어짐)에 대한 내 예상이 맞았나?

✅ 9개 결과를 표로 남겼고, 03·06·09 예상과 비교했다.

#### 📘 D1-7. 머리말 제거와 청킹 (TODO[DOC-2], [DOC-3])
1. ✏️ **DOC-2** `parse.py`의 `drop_header_footer()`: `category`가 `Header`, `Footer`인 요소를 뺀 목록.
2. ✏️ **DOC-3** `src/soc/kb/chunk.py`의 `make_chunks()`: `chunk_by_title(elements, max_characters=max_characters, new_after_n_chars=new_after_n_chars)`를 돌려줍니다. 처음 값은 800.
3. 미리보기 (임베딩, 저장 안 함 → API 키, OpenSearch 필요 없음)
   ```bash
   python -m soc.kb.ingest --dry-run
   python -m soc.kb.ingest --dry-run --show 10
   ```
4. 03번 청크에 "대외비" 같은 반복 문구가 빠졌는지, 청크마다 `[파일 p.페이지 종류]`가 붙는지 봅니다.

✅ 머리말·꼬리말이 빠지고 출처 정보가 붙은 청크가 보인다.

---

### D1-8. 👥 중간 나눔 (둘 다 전반이 끝났을 때)
**왜:** 혼자 오래 만들면 계약과 조금씩 달라지고, 상대가 이미 아는 문제로 혼자 막힙니다. 절반쯤에서 한 번 맞춥니다.

1. **각자 준비 (👤):** 노트에 세 가지
   | | 🔍 | 📘 |
   |---|---|---|
   | 보여 줄 것 | 매핑과, 실제로 들어간 기록 한 건 (Dashboards `localhost:5601` 또는 `curl.exe "localhost:9200/edr-events-*/_search?size=1"`) | 청크 하나와 그 출처 정보 (`--dry-run` 출력) |
   | 막힌 것 / 놀란 것 | 예: 같은 pid가 다른 PC에도 있었다 | 예: 06번 스캔본에서 글자가 안 나왔다 |
   | 상대에게 물을 질문 | 예: 검색 결과 출처는 어디까지 적혀 있어? | 예: 도구 결과에 명령줄이 얼마나 들어가? |
2. **설명과 질문 (👥):** 🔍가 먼저 (에이전트 안에서 조사가 권고보다 먼저라서). 듣는 사람은 "에이전트가 이 결과를 받으면 무엇을 할 수 있나?"를 기준으로 묻습니다.
3. **함께 정하기 (👥):** "계약을 바꿀 것이 있나?" → 있으면 `CONTRACT.md` 변경 이력에 내용, 없으면 **"중간 나눔: 변경 없음"**.
4. **기록:** `docs/teachback/day1.md` "중간 나눔" 표에 보여 준 것, 막힌 것, 질문과 답, 계약 변경 여부.

✅ 둘 다 상대 결과의 필드 이름과 출처 정보를 말할 수 있고, 계약 변경 여부가 기록돼 있다.

---

### 개인 작업 후반 (👤 혼자)

#### 🔍 D1-9. 조사 도구 3개 (TODO[REC-2~4])
✏️ `src/soc/telemetry/tools.py`. 각 함수의 주석에 돌려줄 모양이 적혀 있고, `summarize()`, `_find_process()`, `_search()` 도우미가 이미 있습니다.
- **REC-2** `get_process_tree`: 부모를 최대 5단계까지, 자식(`process.ppid == pid`)도. **모든 검색 조건에 `host`를 넣습니다** (다른 PC에 같은 pid가 있음).
- **REC-3** `get_process_activity`: 같은 host·pid이면서 type이 network, file, registry, script인 기록을 시간순으로 최대 50건.
- **REC-4** `get_host_timeline`: 같은 host이고 `ts`가 기준 ± minutes 안인 기록을 시간순으로 최대 100건, 넘으면 `truncated: true`.
- docstring은 LLM이 도구를 고를 때 읽는 글이라 신경 써서 씁니다.

```bash
pytest tests/test_telemetry_tools.py -q
```
> OpenSearch가 켜져 있으면 테스트가 **진짜 OpenSearch**로 돌고, 꺼져 있으면 메모리 흉내로 돕니다. 흉내는 매핑을 보지 않아서 REC-1 실수가 숨겨집니다. **반드시 compose를 켠 상태로** 통과시키세요.

✅ 테스트 통과 (`test_mapping_types` 포함).

#### 🔍 D1-10. 고장 예상표 확인, 사람이 먼저 읽어 보기
1. P-8 예상을 직접 확인합니다. 예: "다른 PC에 같은 pid가 있다면?" → `test_process_tree_does_not_mix_hosts`가 바로 그 상황입니다. 예상표 옆에 맞음, 틀림, 고침을 적습니다.
2. 01 문서의 예시 알림을 도구로 직접 조회해 봅니다. `python`을 실행한 뒤 한 줄씩 입력합니다.
   ```python
   from soc.telemetry.tools import get_process_tree, get_process_activity, get_host_timeline
   get_process_tree("WS-007", 40702)
   get_process_activity("WS-007", 40702)
   get_host_timeline("WS-007", "2026-11-16T09:12:02Z", 5)
   ```
3. **결과만 보고 사람이 판정할 수 있나?** 사람이 못 하면 LLM도 못 합니다.

✅ 01 문서 6장 빈칸 "① 조사: 부모 프로그램과 .dmp 파일"을 내 도구로 실제로 찾았다.

#### 📘 D1-11. 저장과 하이브리드 검색 (TODO[DOC-4], [DOC-5])
1. ✏️ **DOC-4** `src/soc/kb/index.py`의 `index_body()`: 설정 `index.knn: true`, 복제본 0 / 매핑 `text`(text), `embedding`(knn_vector, 차원 `settings.embed_dim`, 코사인), `source`·`category`(keyword), `page`·`chunk_index`(integer), `text_as_html`(검색 안 함, `"index": false`).
2. 적재합니다. **이때부터 OpenAI API 키가 필요합니다** (임베딩).
   ```bash
   python -m soc.kb.ingest          # → "'kb-playbooks'에 N개 저장"
   ```
3. ✏️ **DOC-5** `src/soc/kb/search.py`의 `rrf_fuse()`: 목록마다 순위(1부터)를 매겨 문서 id별로 `1/(60+순위)`를 더하고, 합이 큰 순서로 `top_n`개. 돌려줄 때 `score`를 RRF 점수로 바꿉니다.
4. 확인: `python`을 실행한 뒤
   ```python
   from soc.kb.search import search_playbook
   search_playbook("격리는 누가 승인해?")
   ```

✅ 01번이나 09번 정책 문서가 위에 나온다. 01 문서 6장 빈칸 "③ 권고: ___에 따라"를 내 검색으로 찾았다.

#### 📘 D1-12. RAG 첫 측정
```bash
python -m soc.eval.rag_eval --mode all      # 키워드만 / 벡터만 / 합친 것 세 줄 비교
```
> 원래 문서는 `--mode all` 없이 적혀 있었는데, 옵션 없이 치면 "합친 것" 하나만 나옵니다.

- `DECISIONS.md` "첫 Recall@3" 표에 세 숫자를 적습니다.
- k13·k14(한국어 질문 → 영어 문서)에서 어느 방식이 이기는지 봅니다. 키워드는 실패, 벡터는 성공하는 게 설계 의도입니다.
- **k10(스캔본), k12(차트), k15~k21(09번 표)은 지금 틀리는 게 정상**입니다. 3일차 고도화 과제입니다.

✅ 세 방식의 Recall@3이 기록돼 있다.

---

### D1-13. 👥 에이전트 설계 (화이트보드, 코드 금지)
`docs/ARCHITECTURE.md`를 채웁니다. 출발점은 01 문서 5장 그림입니다.
1. **상태에 담을 것:** 알림, 대화 기록, 조회한 근거 id, 판정, 권고, 승인 결과, 지나온 경로 (`src/soc/agent/state.py`에 이미 정의돼 있으니 비교)
2. **노드:** 조사 → (도구 ⇄ 조사) → 판정 → 가드레일 → 권고 → 승인 → 리포트
3. **갈림길 3개:** 도구를 더 부를까 판정으로 갈까(최대 몇 번?), 가드레일 실패 시 다시 조사할까 낮출까, 위험한 조치면 승인에서 멈출까
4. 노드 표에 "읽는 상태 / 쓰는 상태"를 채웁니다.

✅ 상태, 노드, 갈림길 3개를 정했다.

### D1-14. 👥 에이전트 뼈대 (TODO[AG-1~3])
> **원래 안내 문서에는 이 TODO 번호가 빠져 있었습니다.** 코드와 테스트에는 있으니 반드시 채워야 합니다.

**운전 규칙: 상대가 만든 도구를 내가 연결합니다.**

| TODO | 파일 | 운전 | 내용 |
|---|---|---|---|
| AG-1 | `src/soc/agent/nodes.py` `investigate()` | **📘** | `telemetry_tools()`를 `get_llm().bind_tools(...)`로 연결, 시스템 프롬프트(`prompt("investigate")`) + 대화로 호출. 첫 호출이면 `_alert_message(state["alert"])`를 먼저 넣음. 돌려줄 것: 새 메시지들, `trace: ["조사"]`, `usage` |
| AG-2 | `nodes.py` `recommend()` | **🔍** | `search_playbook_fn()`으로 검색 (질문은 알림 제목 + 판정 기법), 판정과 검색 결과를 LLM에 넘겨 `Recommendation` 형식으로. 돌려줄 것: `playbook`, `recommendation`, `trace: ["권고"]`, `usage` |
| AG-3 | `src/soc/agent/graph.py` `build_graph()` | 👥 | 주석대로 엣지 연결. 갈림길은 `add_conditional_edges`에 `nodes.after_investigate`, `nodes.after_guardrail` |

> 프롬프트 이름과 판정 노드 쓰는 법은 이미 완성된 `judge()` 함수와 `src/soc/agent/prompts.py`를 참고하세요.

```bash
pytest tests/test_graph_skeleton.py -q     # 가짜 도구 + 가짜 LLM으로 끝까지 흐르는지
python -m soc.agent.graph                   # Mermaid 그림 출력 → ARCHITECTURE.md 1장에 붙이기
```
**실제로 찍히는 경로:** `조사 → 도구 → 조사 → 판정 → 가드레일 → 권고 → 승인 → 리포트`
> 원래 문서의 확인 문구에는 가드레일과 승인이 빠져 있습니다. 두 노드는 이미 그래프에 있지만 **2일차 전까지는 검사 없이 통과만 하는 빈 껍데기**라서 경로에는 찍힙니다. 테스트는 순서만 확인하므로 통과합니다.

✅ 테스트 통과, Mermaid 그림이 `ARCHITECTURE.md`에 있다.

### D1-15. 👥 티치백
`docs/teachback/day1.md`에 기록합니다.
- 🔍는 조사 도구 3개를, 📘는 검색 파이프라인을 화면을 보여 주며 설명합니다.
- 듣는 사람은 질문 3개. 못 답한 질문은 "답하지 못한 질문 → 다음 할 일"로 옮깁니다 (2일차 첫 일).
- 고장 예상표 중 오늘 실제로 확인한 것을 하나씩 소개합니다.

**1일차 결과물 점검:** `CONTRACT.md`(이름 둘) · `RUNBOOK.md`(0단계 깨 보기 + 진단 후 나눔) · `teachback/day1.md`(중간 나눔 + 티치백) · `ARCHITECTURE.md`(Mermaid + 노드 표) · `DECISIONS.md`(🔍 데이터 관찰, text vs keyword / 📘 파싱 관찰, 청킹 값, 첫 Recall@3) · 고장 예상표 갱신

---

## 3. 2일차: 에이전트 완성, 점수, 서버 1~5단계

**오늘 끝났을 때:** 진짜 도구로 판정하고, 격리 권고에서 멈췄다가 승인 후 이어짐 · 평가 기준점이 기록됨 · 팀 서버 k3s에 1~5단계, 외부에서 승인 API 호출 가능
**자세한 "왜"**: `docs/guide/DAY2.md` · **인프라 요구사항과 깨 보기 문제**: `docs/guide/INFRA_STAGES.md` 해당 단계

### 전반: 에이전트 완성과 점수 (내 PC)

| 단계 | 형태 · 운전 | 할 일 | 명령 / 파일 | 끝 기준 |
|---|---|---|---|---|
| D2-1 | 👥 | 어제 못 답한 질문 해결 | `teachback/day1.md` | 질문 목록이 비었다 |
| D2-2 | 👥 | 진짜 도구로 바꾸기. `.env`에서 `TELEMETRY_TOOLS=real`, `KB_TOOLS=real`, `FAKE_LLM=false` (덜 된 쪽은 `mock`으로 두고 진행) | `python -m soc.simulator.run --inject credential_dump --host WS-007` → `python -m soc.worker --once` | 판정 근거에 **실제** `event_id`가 있다. 계약 위반이 드러나면 `CONTRACT.md` 변경 이력 |
| D2-3 | 👥 운전 📘 | 가드레일 TODO[G-1] 근거가 실제 조회한 기록인가, [G-2] 악성이면 근거 2개 이상. 실패 시 처리(`GUARDRAIL_ON_FAIL` = retry / downgrade)를 둘이 정함 | `src/soc/agent/guardrail.py` · `pytest tests/test_guardrail.py -q` | 테스트 통과, `DECISIONS.md` "가드레일 실패 처리"에 선택과 이유 |
| D2-4 | 👥 운전 🔍 | 사람 승인 TODO[H-1] 위험한 조치면 `interrupt()`, [H-2] `PostgresSaver` 연결. **`interrupt()` 앞에 DB 쓰기 금지** (재개하면 노드가 처음부터 다시 실행됨) | `nodes.py` `approval()`, `checkpoint.py` · `pytest tests/test_approval.py -q` · `uvicorn soc.api.main:app --port 8000` → `localhost:8000/docs`에서 `POST /approvals/{alert_id}` | `pending_approval` → 승인하면 `completed`, 거절도 기록. **API를 껐다 켜도 승인 후 이어진다** (`CHECKPOINTER=memory`와 비교) |
| D2-5 | 👥 | 평가 기준점 (교차 작업 전, 서버 올리기 전에) | `python -m soc.eval.rag_eval` · `python -m soc.eval.agent_eval --n 12` | `DECISIONS.md` "기준점" 표 |
| D2-6 | 👥 🔍 도구 쪽 / 📘 검색 쪽 | 틀린 사례 2개의 원인 단계 찾기 (`02` 문서 5장 표: 도구 / RAG / 판정) | `DECISIONS.md` "틀린 사례 분석" | 사례마다 틀린 단계와 근거 |
| D2-7 | 🔁 📘 → 🔍 영역, 리뷰 🔍 | 새 도구 `get_network_connections(host, minutes)` (외부 IP별 연결 횟수, 간격 요약) | `tools.py`, `CONTRACT.md` 표와 변경 이력 | 🔍가 바뀐 부분을 설명할 수 있다 |
| D2-8 | 🔁 🔍 → 📘 영역, 리뷰 📘 | 청킹 실험: 값을 바꿔 적재 → 평가 | `python -m soc.kb.ingest --max-characters 500` → `python -m soc.eval.rag_eval` | `DECISIONS.md` 청킹 표, **최종 값은 📘가 결정** |

### 후반: 서버 1~5단계 (팀 서버, k3s)

시작 전 **D2-9** 👥: `02` 문서 맨 끝 셀프 체크 4문항에 둘이 답합니다.

모든 단계는 같은 순서입니다: **만들기 → 성공 확인 → 🔥 필수 깨 보기 → 진단 후 나눔 → `RUNBOOK.md` 기록 → 커밋**. 운전자가 진단자, 다른 한 명이 출제자입니다 (`02` 7장의 "역할을 바꿉니다"보다 이 표가 우선).

| 단계 | 운전 / 출제 | 만드는 것 (`INFRA_STAGES.md`) | 성공 확인 | 필수 깨 보기 |
|---|---|---|---|---|
| D2-10 1단계 | 📘 / 🔍 | 서버 접속, `infra/scripts/bootstrap.sh`, k3s, 이미지 GHCR push, `infra/k8s/10-namespace.yaml`, `11-api.yaml` (`BACKEND=memory`) | `kubectl -n soc get pods` → api Running, port-forward로 `/healthz` | 1-1 이미지 태그 오타 |
| D2-11 | 👥 주도 🔍 | **용량 산정** (`nproc`, `free -h` 실측 기준) | `docs/CAPACITY.md` | |
| D2-12 2단계 | 🔍 / 📘 | `infra/k8s/20-opensearch.yaml` StatefulSet + PVC, 힙 ≈ limit의 50% | 파드 지웠다 살아나도 데이터 남음 | 2-1 커널 설정 되돌리기 |
| D2-13 3단계 | 📘 / 🔍 | `30-postgres.yaml`, `31-config.yaml`, `infra/scripts/secrets.sh` (Secret은 YAML로 커밋 금지), `BACKEND=real` | `\dt`에 체크포인트 테이블 | 3-2 초기화 후 비밀번호만 변경 (`02` 9-1과 같은 장애) |
| D2-14 4단계 | 🔍 / 📘 | `40-generator.yaml`, `41-worker.yaml`, 프로브. **프로브 설계표를 `DECISIONS.md`에 먼저** | 모두 1/1, `status=new`가 쌓였다 줄어듦 | 4-3 워커 0개, 4-5 처리 중 워커 삭제 |
| D2-15 5단계 | 📘 / 🔍 | `50-ingress.yaml` (`soc.<서버IP>.nip.io`) | 노트북에서 `curl.exe http://soc.<IP>.nip.io/healthz` | 5-2 Service selector 오타 |
| D2-16 | 👤 각자 | 고장 예상표와 오늘 깨 보기 비교 | 예상표 | 예상한 증상과 처음 확인할 곳이 맞았나 |
| D2-17 | 👥 | 티치백: 진단자가 출제자의 장애를, 교차 작업한 사람이 상대 영역을 설명 | `teachback/day2.md` | |

> 2단계 이후 서버 안의 OpenSearch를 노트북에서 보려면 `kubectl -n soc port-forward svc/opensearch 9200:9200`이 필요합니다. `INFRA_STAGES` 4단계 확인 명령의 `curl localhost:9200`도 이 상태를 전제로 합니다.

---

## 4. 3일차: 서버 6~7단계, 고도화, 발표

**자세한 "왜"와 고도화 아이디어 메뉴**: `docs/guide/DAY3.md`

| 단계 | 형태 · 운전 | 할 일 | 파일 / 명령 | 끝 기준 |
|---|---|---|---|---|
| D3-1 6단계 | 👥 📘 / 🔍 | PDF 적재를 Job으로 (`Dockerfile.kb` 이미지), setup Job | `infra/k8s/60-setup-job.yaml`, `61-kb-ingest-job.yaml` | Job `Complete`, 필수 깨 보기 6-1 Job 접속 주소 오타 |
| D3-2 7단계 | 👥 🔍 / 📘 | CI: 테스트 → 이미지(태그 = 커밋 SHA 7자리) → 배포 → 롤백 | `.github/workflows/ci.yml`, `kubectl rollout undo` | 필수 깨 보기 7-1 깨진 이미지 배포 후 롤백 |
| D3-3 | 👥 | Dify 연동: TODO[DIFY-1] 점수 0~1 정규화, Dify External Knowledge에 `http://soc.<IP>.nip.io/dify` 등록 | `src/soc/api/dify.py` · `pytest tests/test_dify.py -q` | `docs/advanced/dify.md`에 우리 에이전트와 비교 |
| D3-4 | 👤 → 👥 | **고도화 고르기:** 각자 후보 3개(내 영역 2, 상대 영역 1) → 서로 따지기 → 함께 4개 | `DECISIONS.md` "고도화 선정" | 4개마다 근거, 증명할 숫자, 상대 영역이면 원래 담당자 동의. 고르지 않은 후보와 이유 |
| D3-5 | 👤 | 고도화 ① 내 영역 | `docs/advanced/<이름>.md`, 테스트 1개 이상 | k3s 배포, 기준점과 숫자 비교 |
| D3-6 | 🔁 | 고도화 ② 상대 영역 (리뷰: 원래 담당자) | 〃 | 리뷰어가 짚은 줄을 설명할 수 있다 |
| D3-7 | 👥 🔥 | 종합 드릴: 1~7단계 아무 장애, 역할 바꿔 두 번 | `RUNBOOK.md` | 몇 단계인지 모르고 찾았다 |
| D3-8 | 👥 | 최종 평가 | `rag_eval`, `agent_eval --n 12` 재실행 | 기준점과 최종이 나란히 |
| D3-9 | 👤 → 👥 | 숫자 해석 나눔: 각자 변화와 원인 → 서로 질문 → 결론 두 문장 | `DECISIONS.md` "숫자 해석" | 가장 효과 큰 변경과 이유, 남은 약점 |
| D3-10 | 👤 | 고장 예상표 마무리: 맞은 것, 틀린 것, 예상 못 한 것 | 예상표 | |
| 🧊 | | **코드 동결** (이후 코드 수정 금지) | | |
| D3-11 | 👥 | 배포 가이드 → 옆 팀이 ❓ 표시 → 0개까지 수정 | `docs/DEPLOYMENT.md` | ❓ 0개 |
| D3-12 | 👥 | 사후 회고 1건 (비난 없는 형식, "왜?" 다섯 번) | `docs/POSTMORTEM.md` | |
| D3-13 | 👥 | 발표: 데모 → 🔍 → 📘 → 서로 바꿔 설명 → 공동 | | 아래 "발표 전 확인" |

> **현실적인 조언:** 3일차는 할 일이 매우 많습니다. 고도화는 "k3s 배포까지"가 완료 조건이라, 후보를 고를 때 **오늘 안에 배포할 수 있는가**를 가장 먼저 따지세요. 막히면 고도화 하나를 작게 줄이는 편이 드릴, 배포 가이드, 발표를 놓치는 것보다 낫습니다.

**발표 전 확인**
- [ ] 🔍 인덱스 설계 이유, 조사 도구 입출력, 고장 예상표 결과, 고도화 숫자
- [ ] 📘 PDF에서 깨진 것과 해결, 청킹·검색 결정과 Recall, 고도화 숫자
- [ ] 🔍가 📘 영역을, 📘가 🔍 영역을 짧게 (무엇을 받아 무엇을 돌려주고 어디서 쓰이나)
- [ ] 👥 승인에서 멈추고 이어 가는 원리, 가드레일이 막는 것, 장애를 찾은 과정 하나

---

## 5. 막혔을 때: 자주 나는 오류

| 오류 / 증상 | 원인 | 해결 |
|---|---|---|
| `NotImplementedError: TODO[XXX]` | 아직 안 채운 자리를 부름 | 정상. 그 TODO를 채우거나, 순서상 아직이면 다음 단계로 |
| `ModuleNotFoundError: No module named 'soc'` | `pip install -e .` 안 함, 또는 가상환경이 꺼짐 | 가상환경 켜고 `pip install -e .` |
| `ConnectionError` ... `localhost:9200` | OpenSearch가 안 떠 있음 | `docker compose ps`, `docker compose up -d`. 아직 D1-3 전이면 OpenSearch 쓰는 명령은 나중에 |
| 적재 시 `strict_dynamic_mapping_exception` | REC-1 매핑에 칸이 빠짐 | 오류에 나온 칸 이름을 `schema.py`와 비교해 추가 |
| 테스트는 통과하는데 실제 검색이 이상함 | OpenSearch를 끈 채로 테스트 → 메모리 흉내로 통과 | compose를 켜고 다시 `pytest` |
| `openai.AuthenticationError` / 401 | `.env`의 `OPENAI_API_KEY`가 틀리거나 비어 있음 | 키 확인. 흐름만 볼 거면 `FAKE_LLM=true` (단, 📘 점수는 의미 없음) |
| 벡터 검색 Recall이 이상하게 낮음 | `FAKE_LLM=true`로 적재함 (가짜 임베딩) | `FAKE_LLM=false`로 바꾸고 `python -m soc.kb.ingest` 다시 |
| `TODO[H-2] 전: Postgres 대신 메모리에 저장합니다` 경고 | `BACKEND=real`이라 Postgres를 쓰려 했지만 H-2가 아직 | 2일차 D2-4 전까지는 정상 |
| PowerShell에서 `curl` 결과가 이상함 | PowerShell의 `curl`은 `Invoke-WebRequest` | `curl.exe`로 입력 |
| `hi_res` 첫 실행이 멈춘 듯함 | 레이아웃 모델을 인터넷에서 내려받는 중 | 기다리거나 네트워크 확인. 1일차는 `fast`만 씀 |
| 깨 보기에서 막힘 | | `02` 문서 3장 "어디를 볼지" 표를 위에서부터, `docker compose logs` / `kubectl get events --sort-by=.lastTimestamp` 먼저. 충분히 막히면 출제자에게 힌트 1개 요청 |
