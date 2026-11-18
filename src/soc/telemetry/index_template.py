"""🔍 텔레메트리 인덱스 템플릿과 적재.

이벤트는 날짜별 인덱스(edr-events-2026.11.16)에 들어갑니다. 날짜별로 나누면 오래된 기록을
인덱스째 지울 수 있습니다(보존 기간). 인덱스가 매일 새로 생기므로 매핑은 '템플릿'으로 미리 정해 둡니다.

    python -m soc.telemetry.index_template                         # 템플릿만 만들기
    python -m soc.telemetry.index_template --load data/sim.jsonl   # 템플릿 + 기록 넣기
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from ..config import settings
from ..osclient import bulk_index, get_client

TEMPLATE_NAME = "edr-events"


def build_template() -> dict:
    """edr-events-* 인덱스에 적용할 템플릿."""
    # TODO[REC-1]: 매핑을 채웁니다. 검색·필터에 쓰는 칸(host, type, process.name 등)은 keyword,
    # 시간은 date, pid·ppid·포트·바이트는 long, IP는 ip, 명령줄과 스크립트는 text와 keyword 둘 다(fields 사용).
    # 왜 text와 keyword를 나누는지 DECISIONS.md에 한 줄로 적으세요. (03 문서 1장의 질문)
    kw = {"type": "keyword"}
    # 단어 일부로도 찾고(text) 통째로 맞춰 보기도 하는(keyword) 긴 문자열: 명령줄, 스크립트, 파일 경로, 레지스트리.
    # keyword 쪽은 1024자가 넘으면 색인만 건너뜁니다(기록은 거절되지 않음). 시뮬레이터의 가장 긴 명령줄은 319자.
    text_kw = {"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 1024}}}
    # dynamic: strict라서 src/soc/schema.py의 칸이 하나라도 빠지면 기록이 거절됩니다. 그래서 스키마 전체를 적습니다.
    properties: dict = {
        "event_id": kw,                     # 가드레일이 근거 id를 정확히 맞춰 봄
        "ts": {"type": "date"},
        "host": kw,                         # WS-007을 통째로 비교 (text면 ws, 007로 쪼개짐)
        "type": kw,
        "process": {"properties": {
            "pid": {"type": "long"},
            "ppid": {"type": "long"},
            "name": kw,
            "cmdline": text_kw,
            "parent_name": kw,
            "signed": {"type": "boolean"},
            "user": kw,
        }},
        "network": {"properties": {
            "dst_ip": {"type": "ip"},       # ip 타입이라 10.0.0.0/8 같은 대역 검색이 됨
            "dst_port": {"type": "long"},
            "proto": kw,
            "bytes_out": {"type": "long"},
        }},
        "file": {"properties": {
            "path": text_kw,
            "action": kw,
            "new_path": text_kw,
        }},
        "registry": {"properties": {
            "key": text_kw,
            "value": text_kw,
        }},
        "script_text": text_kw,
    }
    return {
        "index_patterns": [f"{settings.index_events}-*"],
        "template": {
            "settings": {"number_of_shards": 1, "number_of_replicas": 0},   # 노드가 1개라 복제본 0 (2-5 깨 보기)
            "mappings": {"dynamic": "strict", "properties": properties},
        },
    }


def apply_template(client=None) -> None:
    client = client or get_client()
    client.indices.put_index_template(name=TEMPLATE_NAME, body=build_template())


def index_name(ts: str) -> str:
    day = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y.%m.%d")
    return f"{settings.index_events}-{day}"


def load_jsonl(path: str | Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def index_events(events: list[dict], client=None) -> int:
    """기록을 날짜별 인덱스로 나눠 넣습니다. event_id를 문서 id로 써서 여러 번 넣어도 중복되지 않습니다."""
    client = client or get_client()
    by_index: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        by_index[index_name(e["ts"])].append(e)
    n = sum(bulk_index(client, ix, docs, id_field="event_id") for ix, docs in by_index.items())
    client.indices.refresh(index=f"{settings.index_events}-*")
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--load", help="넣을 jsonl 파일 (예: data/sim.jsonl)")
    args = ap.parse_args()
    client = get_client()
    apply_template(client)
    print(f"템플릿 '{TEMPLATE_NAME}' 적용 완료")
    if args.load:
        n = index_events(load_jsonl(args.load), client)
        total = client.count(index=f"{settings.index_events}-*")["count"]
        print(f"{n}건 넣음 → 전체 {total}건")


if __name__ == "__main__":
    main()
