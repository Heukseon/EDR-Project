"""🔍 조사 도구: 에이전트가 PC 기록을 조사할 때 부르는 함수들.

도구 계약 (docs/CONTRACT.md)
- 모든 결과의 기록 하나하나에 `event_id`가 있다 → 가드레일이 판정 근거를 검증하는 데 씀
- 명령줄은 앞부분만 (요약) → LLM에게 넘기는 글자 수가 곧 비용과 속도

함수의 설명(docstring)은 LLM이 '어떤 도구를 부를지' 고를 때 읽는 글입니다. 신경 써서 쓰세요.

    pytest tests/test_telemetry_tools.py -q
"""
from __future__ import annotations

from datetime import datetime, timedelta

from langchain_core.tools import tool

from ..config import settings
from ..osclient import get_client

EVENTS = f"{settings.index_events}-*"
CMD_MAX = 120           # 명령줄 요약 길이
MAX_ANCESTORS = 5
CHILDREN_LIMIT = 20     # 자식 요약 최대 개수 (explorer.exe처럼 자식이 많은 프로세스 대비)
ACTIVITY_LIMIT = 50
TIMELINE_LIMIT = 100
ACTIVITY_TYPES = ["network", "file", "registry", "script"]
_TIME_ORDER = [{"ts": "asc"}, {"event_id": "asc"}]          # 같은 시각이면 event_id로 순서를 고정


def _search(body: dict) -> list[dict]:
    res = get_client().search(index=EVENTS, body=body)
    return [h["_source"] for h in res["hits"]["hits"]]


def summarize(e: dict) -> dict:
    """기록 하나를 LLM에게 넘길 모양으로 줄입니다. (이미 만들어 둔 도우미)"""
    p = e.get("process", {})
    out = {"event_id": e["event_id"], "ts": e["ts"], "type": e["type"],
           "pid": p.get("pid"), "ppid": p.get("ppid"), "name": p.get("name"),
           "cmdline": (p.get("cmdline") or "")[:CMD_MAX], "user": p.get("user"), "signed": p.get("signed")}
    if e.get("network"):
        n = e["network"]
        out["detail"] = f"{n['dst_ip']}:{n['dst_port']} ({n.get('bytes_out', 0)} bytes)"
    elif e.get("file"):
        f = e["file"]
        out["detail"] = f"{f['action']} {f['path']}" + (f" → {f['new_path']}" if f.get("new_path") else "")
    elif e.get("registry"):
        out["detail"] = f"{e['registry']['key']} = {e['registry']['value']}"
    elif e.get("script_text"):
        out["detail"] = e["script_text"][:200]
    return out


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _iso(t: datetime) -> str:
    return t.isoformat().replace("+00:00", "Z")


def _find_process(host: str, pid: int) -> dict | None:
    """host에서 pid를 가진 '프로세스 생성' 기록 하나."""
    rows = _search({"size": 1, "sort": [{"ts": "desc"}], "query": {"bool": {"filter": [
        {"term": {"host": host}}, {"term": {"type": "process"}}, {"term": {"process.pid": pid}}]}}})
    return rows[0] if rows else None


def _process_records(host: str, pid: int, size: int = 20) -> list[dict]:
    """host에서 pid를 가진 '프로세스 생성' 기록 전부 (오래된 것부터). 같은 PC 안에서도 pid는 재사용됩니다."""
    return _search({"size": size, "sort": _TIME_ORDER, "query": {"bool": {"filter": [
        {"term": {"host": host}}, {"term": {"type": "process"}}, {"term": {"process.pid": pid}}]}}})


def _parent_of(host: str, child: dict) -> dict | None:
    """child를 실행한 부모의 생성 기록. 부모 pid가 여러 번 생성됐으면 child보다 먼저 생긴 것 중 가장 가까운 것.
    (가장 최근 기록을 고르면, 나중에 같은 pid로 뜬 다른 프로그램이 부모로 잡힙니다. DECISIONS.md 데이터 관찰 1번)"""
    ppid = child["process"].get("ppid")
    if ppid is None:
        return None
    rows = _search({"size": 1, "sort": [{"ts": "desc"}, {"event_id": "desc"}], "query": {"bool": {"filter": [
        {"term": {"host": host}}, {"term": {"type": "process"}}, {"term": {"process.pid": ppid}},
        {"range": {"ts": {"lte": child["ts"]}}}]}}})
    return rows[0] if rows else None


def get_process_tree(host: str, pid: int) -> dict:
    """프로세스의 족보를 봅니다: 누가 이 프로세스를 실행했는지(부모, 조부모 …)와 이 프로세스가 실행한 자식들.
    '누가 실행했나', '정상 프로그램이 띄운 것인가'를 확인할 때 씁니다.
    부모 기록이 중간에 끊겼거나 같은 pid가 여러 번 생성된 경우에는 note에 설명이 붙습니다.

    Args:
        host: PC 이름 (예: WS-007)
        pid: 프로세스 번호 (알림의 pid)
    """
    # TODO[REC-2]: 부모를 최대 MAX_ANCESTORS단계까지 거슬러 올라가고, 자식(ppid == pid)도 찾습니다.
    # 반드시 host까지 같이 조건에 넣으세요. 다른 PC에 같은 pid가 있을 수 있습니다. (02 문서 9-2 고장 예상표)
    # 돌려줄 모양: {"host", "pid", "process": 요약 또는 None, "ancestors": [가까운 부모부터 요약], "children": [요약]}
    # 요약은 summarize()를 쓰고, 프로세스 기록을 찾을 때는 _find_process()를 쓰면 됩니다.
    out: dict = {"host": host, "pid": pid, "process": None, "ancestors": [], "children": []}
    notes: list[str] = []
    recs = _process_records(host, pid)
    if not recs:                                    # 계약: 예외 대신 process None과 빈 목록
        out["note"] = f"{host}에 pid {pid}의 프로세스 생성 기록이 없습니다."
        return out
    proc = recs[-1]                                 # 같은 pid가 여러 번이면 가장 최근 것을 기준으로
    if len(recs) > 1:
        seen = ", ".join(f"{r['ts'][11:19]} {r['process']['name']}" for r in recs)
        notes.append(f"{host}에 pid {pid}의 생성 기록이 {len(recs)}개 있습니다({seen}). 가장 최근 것을 기준으로 봤습니다.")
    out["process"] = summarize(proc)

    # 부모: 가까운 부모부터 최대 MAX_ANCESTORS단계
    cur, visited = proc, {proc["event_id"]}
    for _ in range(MAX_ANCESTORS):
        ppid = cur["process"].get("ppid")
        if ppid is None:
            break
        parent = _parent_of(host, cur)
        if parent is None:
            name = cur["process"].get("parent_name") or "이름 모름"
            notes.append(f"부모 프로세스(pid {ppid}, {name})의 생성 기록이 없습니다.")
            break
        if parent["event_id"] in visited:           # 기록이 이상해서 족보가 제자리를 돌면 멈춤
            notes.append(f"pid {ppid}에서 족보가 되풀이돼 멈췄습니다.")
            break
        out["ancestors"].append(summarize(parent))
        visited.add(parent["event_id"])
        cur = parent
    else:
        if cur["process"].get("ppid") is not None:
            notes.append(f"부모는 {MAX_ANCESTORS}단계까지만 봤습니다.")

    # 자식: 이 프로세스가 생긴 뒤 ppid == pid로 생성된 프로세스 (같은 pid를 쓰던 예전 프로세스의 자식은 뺌)
    kids = _search({"size": CHILDREN_LIMIT + 1, "sort": _TIME_ORDER, "query": {"bool": {"filter": [
        {"term": {"host": host}}, {"term": {"type": "process"}}, {"term": {"process.ppid": pid}},
        {"range": {"ts": {"gte": proc["ts"]}}}]}}})
    out["children"] = [summarize(k) for k in kids[:CHILDREN_LIMIT]]
    if len(kids) > CHILDREN_LIMIT:
        notes.append(f"자식이 {CHILDREN_LIMIT}개보다 많아 앞의 {CHILDREN_LIMIT}개만 보여 줍니다.")

    if notes:
        out["note"] = " ".join(notes)
    return out


def get_process_activity(host: str, pid: int) -> dict:
    """한 프로세스가 한 일을 시간순으로 봅니다: 네트워크 연결, 파일 생성·변경, 레지스트리 변경, 실행한 스크립트.
    '이 프로세스가 무엇을 남겼나(파일, 통신)'를 확인할 때 씁니다.

    Args:
        host: PC 이름 (예: WS-007)
        pid: 프로세스 번호
    """
    # TODO[REC-3]: host와 pid가 같은 기록 중 type이 network, file, registry, script인 것을 시간순으로 (최대 50건).
    # 돌려줄 모양: {"host", "pid", "events": [summarize(e) ...]}
    rows = _search({"size": ACTIVITY_LIMIT + 1, "sort": _TIME_ORDER, "query": {"bool": {"filter": [
        {"term": {"host": host}}, {"term": {"process.pid": pid}}, {"terms": {"type": ACTIVITY_TYPES}}]}}})
    out = {"host": host, "pid": pid, "events": [summarize(e) for e in rows[:ACTIVITY_LIMIT]],
           "truncated": len(rows) > ACTIVITY_LIMIT}
    names = sorted({e["process"]["name"] for e in rows})
    if len(names) > 1:                              # 같은 PC에서 pid가 재사용되면 다른 프로그램의 기록이 섞임
        out["note"] = (f"pid {pid}의 기록에 서로 다른 프로세스({', '.join(names)})가 섞여 있습니다. "
                       "같은 PC에서 pid가 재사용됐을 수 있으니 시각과 이름을 같이 보세요.")
    return out


def get_host_timeline(host: str, around_ts: str, minutes: int = 10) -> dict:
    """특정 시각 앞뒤로 그 PC에서 일어난 모든 일을 시간순으로 봅니다.
    알림 직전·직후에 다른 수상한 활동(다른 프로그램, 다른 통신)이 있었는지 넓게 볼 때 씁니다.
    기록이 100건을 넘으면 기준 시각에 가까운 100건만 돌려주고 truncated=true로 알립니다. 그때는 minutes를 줄여 다시 부르세요.

    Args:
        host: PC 이름 (예: WS-007)
        around_ts: 기준 시각 (ISO 형식, 예: 2026-11-16T09:12:02Z). 보통 알림 시각
        minutes: 기준 시각 앞뒤로 몇 분까지 볼지 (기본 10)
    """
    # TODO[REC-4]: host가 같고 ts가 [around_ts - minutes, around_ts + minutes] 안인 기록을 시간순으로 (최대 TIMELINE_LIMIT건).
    # 결과가 잘렸으면 truncated=True로 알려 줍니다 (LLM이 범위를 줄여 다시 부를 수 있게).
    # 돌려줄 모양: {"host", "from", "to", "events": [summarize(e) ...], "truncated": bool}
    center = _parse_ts(around_ts)
    span = timedelta(minutes=max(0, minutes))
    start, end = center - span, center + span
    host_filter = {"term": {"host": host}}
    # 앞쪽(기준 시각 포함)은 가까운 것부터, 뒤쪽은 가까운 것부터 각각 가져옵니다.
    # 시간순으로 앞에서부터 100건을 자르면, 기록이 많을 때 알림 뒤쪽이 통째로 빠지기 때문입니다.
    before = _search({"size": TIMELINE_LIMIT + 1, "sort": [{"ts": "desc"}, {"event_id": "desc"}],
                      "query": {"bool": {"filter": [host_filter, {"range": {"ts": {"gte": _iso(start), "lte": _iso(center)}}}]}}})
    after = _search({"size": TIMELINE_LIMIT + 1, "sort": _TIME_ORDER,
                     "query": {"bool": {"filter": [host_filter, {"range": {"ts": {"gt": _iso(center), "lte": _iso(end)}}}]}}})
    truncated = len(before) + len(after) > TIMELINE_LIMIT
    picked = sorted(before + after, key=lambda e: abs(_parse_ts(e["ts"]) - center))[:TIMELINE_LIMIT]
    picked.sort(key=lambda e: (_parse_ts(e["ts"]), e["event_id"]))
    return {"host": host, "from": _iso(start), "to": _iso(end),
            "events": [summarize(e) for e in picked], "truncated": truncated}




TELEMETRY_TOOLS = [tool(get_process_tree), tool(get_process_activity), tool(get_host_timeline)]
