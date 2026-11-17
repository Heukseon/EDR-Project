# 도구 계약

> 1일차에 함께 정합니다. **혼자 바꾸지 않습니다.** 바꾸려면 상대에게 먼저 말하고, 이 표와 `src/soc/mocks.py`를 같이 고친 뒤 변경 이력에 적습니다.

🔍 기록 담당: ______  📘 문서 담당: 최재우  (둘 다 이름을 적으면 계약 성립)

## 도구 목록

| 도구 | 만드는 사람 | 입력 | 출력 (꼭 있어야 하는 칸) | 결과 개수 상한 | 실패하면 |
|---|---|---|---|---|---|
| `get_process_tree(host, pid)` | 🔍 | `host`: PC 이름(str, 예: WS-007), `pid`: 프로세스 번호(int) | `host`, `pid`, `process`(요약, 없으면 `None`), `ancestors`(가까운 부모부터), `children`. 기록(요약)마다 `event_id`, `ts`, `type`, `pid`, `ppid`, `name`, `cmdline`, `user`, `signed` | 부모 최대 5단계 | 프로세스 기록이 없으면 예외 대신 `process: None`과 빈 `ancestors`·`children`. 부모 기록이 끊기면 `note`에 설명 |
| `get_process_activity(host, pid)` | 🔍 | `host`(str), `pid`(int) | `host`, `pid`, `events`(시간순). 기록마다 `event_id`와 위 요약 칸, 파일·통신 내용은 `detail` | 최대 50건 | 기록이 없으면 `events: []` |
| `get_host_timeline(host, around_ts, minutes)` | 🔍 | `host`(str), `around_ts`: 기준 시각(ISO 문자열, 예: 2026-11-16T09:12:02Z), `minutes`: 앞뒤 몇 분(int, 기본 10) | `host`, `from`, `to`, `events`(시간순), `truncated`. 기록마다 `event_id`와 위 요약 칸 | 최대 100건, 넘으면 `truncated: true` | 기록이 없으면 `events: []`, `truncated: false` |
| `search_playbook(query, k)` | 📘 | `query`: 질문(str), `k`: 돌려받을 조각 수(int, 기본 3) | 조각 목록(list). 조각마다 `source`(파일 이름), `page`, `category`(요소 종류), `text`, `score`(클수록 관련 높음) | `k`개 (기본 3) | 맞는 조각이 없으면 빈 목록 `[]` |

## 꼭 합의할 것
- 🔍 텔레메트리 도구의 모든 결과에는 **`event_id`**가 있다. → 가드레일이 판정 근거를 추적하는 데 씁니다 (2일차 `G-1`).
- 📘 플레이북 검색 결과에는 **`source`(파일 이름)**가 있다. → 권고에 출처를 붙이는 데 씁니다.

## 변경 이력

| 바꾼 것 | 이유 | 둘 다 동의 |
|---|---|---|
