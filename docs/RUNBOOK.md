# 런북: 우리가 겪은 장애와 찾는 법

> 02 문서 8장의 **'좋은 런북'** 형식으로 씁니다. 새벽 당번이 이것만 보고 해결할 수 있게, **실제로 친 명령과 실제 출력**을 남깁니다.

## 공통 1차 확인

**로컬 (docker compose, 인프라 0단계)**
```bash
docker compose ps -a
docker compose logs --tail 30 <서비스 이름>
```

**서버 (k3s, 인프라 1단계부터)**
```bash
kubectl -n soc get pods,svc,ingress,pvc,jobs
kubectl -n soc get events --sort-by=.lastTimestamp | tail -20
```

## 장애 기록

### [0-2] Postgres 5432 포트 충돌  (출제: 📘 최재우 · 진단: 🔍 김진홍 · 복구까지 걸린 시간: 15~30분)
- **환경:** 최재우 PC (Windows), 인프라 0단계 `docker-compose.yml`
  - 그때의 출력은 남기지 못했다. 아래 명령과 출력은 11-18에 김진홍 Mac(Docker 29.9.3)에서 같은 장애를 다시 내서 받은 것이다.
  - 재현 방법(출제): `docker compose stop postgres`로 compose의 postgres를 멈추고, `docker run -d --name other-postgres -p 5432:5432 -e POSTGRES_PASSWORD=other postgres:16`으로 다른 컨테이너가 5432를 먼저 차지하게 했다.
- **증상:**
  - `docker compose up -d`가 실패한다(종료 코드 1). 메시지: `Bind for 0.0.0.0:5432 failed: port is already allocated`
  - opensearch와 dashboards는 그대로 돌고, postgres만 `Exited (128)`이고 PORTS 칸이 비어 있다.
  - `docker compose logs postgres`에는 단서가 없다. 컨테이너가 시작조차 못 해서, 그 전에 정상 종료한 기록만 보인다.
  - (재현에서 봄) 0단계 성공 확인 명령인 `psql`은 5432를 차지한 다른 Postgres에 붙어서 `password authentication failed`를 낸다. 비밀번호 문제처럼 보여 헷갈린다.
- **확인 명령과 출력:**
  ```
  $ docker compose up -d
   Container edr-ai-triage-lab-opensearch-1 Running
   Container edr-ai-triage-lab-dashboards-1 Running
   Container edr-ai-triage-lab-postgres-1 Starting
   Container edr-ai-triage-lab-postgres-1 Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint edr-ai-triage-lab-postgres-1 (6daf9519fa09cc5d91abae52b50b23abda309fb13f4312820a5b072a1571ca8d): Bind for 0.0.0.0:5432 failed: port is already allocated
  Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint edr-ai-triage-lab-postgres-1 (6daf9519fa09cc5d91abae52b50b23abda309fb13f4312820a5b072a1571ca8d): Bind for 0.0.0.0:5432 failed: port is already allocated

  $ docker compose ps -a
  NAME                             IMAGE                                            COMMAND                  SERVICE      CREATED       STATUS                       PORTS
  edr-ai-triage-lab-dashboards-1   opensearchproject/opensearch-dashboards:2.17.1   "./opensearch-dashbo…"   dashboards   5 hours ago   Up 5 hours                   0.0.0.0:5601->5601/tcp, [::]:5601->5601/tcp
  edr-ai-triage-lab-opensearch-1   opensearchproject/opensearch:2.17.1              "./opensearch-docker…"   opensearch   5 hours ago   Up 5 hours                   0.0.0.0:9200->9200/tcp, [::]:9200->9200/tcp
  edr-ai-triage-lab-postgres-1     postgres:16                                      "docker-entrypoint.s…"   postgres     5 hours ago   Exited (128) 5 seconds ago

  $ docker compose logs --tail 10 postgres
  postgres-1  | 2026-11-18 02:54:18.693 UTC [1] LOG:  database system is ready to accept connections
  …(중간 생략)…
  postgres-1  | 2026-11-18 08:18:02.947 UTC [1] LOG:  database system is shut down

  $ psql postgresql://soc:soc@localhost:5432/soc -c 'select 1'
  psql: error: connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "soc"

  $ docker ps --filter publish=5432
  CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS          PORTS                                         NAMES
  86b2190845ca   postgres:16   "docker-entrypoint.s…"   12 seconds ago   Up 11 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   other-postgres

  $ lsof -nP -iTCP:5432 -sTCP:LISTEN
  COMMAND     PID    USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
  com.docke 69941 jinhong  109u  IPv6 0x14392f7f78343f88      0t0  TCP *:5432 (LISTEN)
  ```
  Mac의 `lsof`는 `com.docker.backend`(Docker)라고만 알려 줘서 어느 컨테이너인지는 모른다. `docker ps --filter publish=5432`가 범인 컨테이너 이름을 바로 보여 준다.
- **원인:** 다른 프로그램(컨테이너)이 내 PC의 5432 포트를 먼저 차지하고 있어서, compose의 `postgres` 서비스가 같은 포트(`ports: ["5432:5432"]`)를 열지 못했다. Docker는 컨테이너를 시작할 때 호스트 포트를 연결하는데, 이 단계에서 실패하면 Postgres 프로세스는 아예 뜨지 않는다. 그래서 로그에 아무것도 남지 않는다.
- **조치:** 5432를 막던 컨테이너를 지우고 다시 올렸다. 최재우 PC에서는 이것으로 복구됐다.
  ```bash
  docker rm -f other-postgres
  docker compose up -d
  ```
  - **재현(Mac)에서만 나온 2차 고장:** 다시 올린 postgres가 `Up`인데 PORTS가 `5432/tcp`뿐이고 `psql`은 `Connection refused`였다. 컨테이너는 5432 연결을 요청하지만(`PortBindings`), 실제로 연결된 포트는 없었다(`Ports: []`). `docker compose restart postgres`로는 그대로였고, 컨테이너를 다시 만들어서 복구했다. 데이터 볼륨(`pgdata`)은 그대로 남는다.
  ```
  $ docker compose ps postgres
  NAME                           IMAGE         COMMAND                  SERVICE    CREATED       STATUS          PORTS
  edr-ai-triage-lab-postgres-1   postgres:16   "docker-entrypoint.s…"   postgres   5 hours ago   Up 22 seconds   5432/tcp

  $ psql postgresql://soc:soc@localhost:5432/soc -c 'select 1'
  psql: error: connection to server at "localhost" (::1), port 5432 failed: Connection refused
  	Is the server running on that host and accepting TCP/IP connections?
  connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
  	Is the server running on that host and accepting TCP/IP connections?

  $ docker inspect -f "{{json .HostConfig.PortBindings}} | {{json .NetworkSettings.Ports}}" edr-ai-triage-lab-postgres-1
  {"5432/tcp":[{"HostIp":"","HostPort":"5432"}]} | {"5432/tcp":[]}

  $ docker compose up -d --force-recreate postgres
   Container edr-ai-triage-lab-postgres-1 Recreate
   Container edr-ai-triage-lab-postgres-1 Recreated
   Container edr-ai-triage-lab-postgres-1 Starting
   Container edr-ai-triage-lab-postgres-1 Started

  $ docker compose ps -a        # postgres 줄만
  edr-ai-triage-lab-postgres-1     postgres:16   "docker-entrypoint.s…"   postgres     6 seconds ago   Up 5 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp

  $ psql postgresql://soc:soc@localhost:5432/soc -c 'select 1'
   ?column?
  ----------
          1
  (1 row)
  ```
- **진단 후 나눔** (깨 보기 규칙 5~6번)
  - 진단자 (🔍): 포트 충돌이라는 건 알았지만, 5432를 누가 쓰고 있는지 찾는 명령을 몰라서 가장 오래 걸렸다.
  - 출제자 (📘): 나라면 `docker compose ps -a`의 PORTS 칸부터 봤을 것이다. postgres만 `Exited`이고 PORTS가 비어 있어서 포트 문제라는 게 바로 보인다.
  - 다음에 같은 증상을 보면 처음 칠 명령: `docker ps --filter publish=5432` (Mac과 Windows 공통, 5432를 연 컨테이너 이름이 바로 나온다)
- **재발 방지:**
  - compose를 올리기 전에 `docker ps --filter publish=5432`로 5432를 쓰는 컨테이너가 없는지 본다.
  - 막던 것을 치운 뒤에는 `docker compose ps -a`의 PORTS 칸에 `0.0.0.0:5432->5432/tcp`가 있는지 확인한다. `5432/tcp`만 보이면 `docker compose up -d --force-recreate postgres`로 다시 만든다.
  - 컨테이너가 아닌 프로그램(예: Windows에 설치된 PostgreSQL)이 5432를 잡고 있으면 `docker ps`에 안 나온다. Windows에서는 `netstat -ano | findstr :5432`로 PID를 찾는다.
- **고장 예상표와 비교:** 내 고장 예상표(🔍, `sample_events.jsonl` 기준)에는 인프라 고장이 없어서 예상하지 못한 고장이다. 특히 예상 못 한 점은 세 가지다. ① 로그에 단서가 없다. ② `psql`이 비밀번호 오류를 내서 설정 문제처럼 보인다. ③ 막던 것을 치운 뒤에도 포트가 안 열릴 수 있다(재현에서만).

---

### 양식 (새 장애를 기록할 때 복사해서 씀)

```
### [단계-번호] 제목  (출제: 🔍/📘 · 진단: 🔍/📘 · 복구까지 걸린 시간: ____)
- **증상:**
- **확인 명령과 출력:**
- **원인:**
- **조치:**
- **진단 후 나눔** (깨 보기 규칙 5~6번)
  - 진단자: 가장 오래 걸린 지점과 이유
  - 출제자: 나라면 어디부터 봤을지
  - 다음에 같은 증상을 보면 처음 칠 명령:
- **재발 방지:**
- **고장 예상표와 비교:** 02 문서 9-2에서 예상했던 고장인가? 증상과 '처음 확인할 곳'은 맞았나?
```
