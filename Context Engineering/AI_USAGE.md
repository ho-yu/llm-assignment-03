# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 오류 원인 확인에 사용할 수 있습니다. 과제 전체, 미작성 빈칸, 선택 심화의 설계나 정답을 대신 작성하도록 요청하지 않습니다. 설명을 이해한 뒤 직접 수정하고 다시 검사하세요.

사용하지 않았다면 아래에 사용하지 않음이라고 적습니다. 사용했다면 필요한 만큼 행을 추가하세요. API 키와 개인 정보는 기록하지 않습니다.

| 사용 도구 | 질문 | 이해한 내용 | 직접 수정한 부분 | 다시 실행한 명령과 결과 |
|---|---|---|---|---|
| Claude Code | `memory_action`의 빈칸을 어떻게 채우는지, `check memory`가 실패하는 이유 | - 조회, 저장, 수정은 `deepcopy`로 사본을 다룸<br>- 삭제는 `records.pop(키, None)`<br>- `pop`은 `records`에 호출하고 인자는 (키, 없을 때 반환값) | `delete` 줄<br>`dict.pop(records.get(key), value)`에서 TypeError, KeyError가 차례로 나서 `records.pop(key, None)`으로 수정 | `check memory`<br>4/4 통과 |
| Claude Code | `build_messages`의 반환 형식, `check context`가 실패하는 이유 | - `role`과 `content`를 가진 사전의 리스트<br>- `history`는 이미 메시지 리스트이므로 감싸지 않고 `*history`로 펼쳐 넣음<br>- `[*history]`는 리스트 안에 리스트가 생김 | `history`를 `content`에 넣던 코드를 `[*history]`, 다시 `*history`로 수정 | `check context` 5/5 통과<br>`run context` 역할 순서 developer, user, user<br>`check memory` 4/4 통과 |
| Claude Code | `summarize`에 넣을 값, `check compare`가 실패하는 이유 | - 값은 `value`와 `source_turn_id` 두 키를 가진 사전<br>- `source_turn_id`에는 `turn` 전체가 아니라 `turn["id"]`를 넣음 | `"source_turn_id": turn`을 `turn["id"]`로 수정 | `check compare`<br>`summarize` 관련 2개 항목 통과 |
| Claude Code | `select_window`의 예산 계산과 중단 조건, `check compare`가 실패하는 이유 | - 예산은 `limit - reserve - margin`<br>- 후보로 만든 입력의 토큰 수가 예산보다 클 때만 중단하고 같으면 포함<br>- 비교 대상은 `limit`이 아니라 `budget`이고 `make_messages`에는 `candidate`를 넘김 | `budget >= limit`을 거쳐 `count(make_messages(candidate)) > budget`으로 수정 | `check compare` 4/4 통과<br>`run compare`<br>- 전체 대화: 1999토큰, 3/3<br>- 최근 대화: 1744토큰, 0/3<br>- 요약과 최근 대화: 1744토큰, 3/3 |
| Claude Code | `cache_key`를 만드는 방법, `check cache`가 실패하는 이유 | - 사용자 ID, 줄바꿈, `prefix`를 합쳐 UTF-8로 인코딩한 뒤 `sha256`, `hexdigest` 순서<br>- `sha256`은 `bytes`를 받음<br>- `hashlib`은 점으로 잇지 않고 맨 앞에서 호출하고, 묶을 때는 소괄호를 씀 | `.hashlib`으로 잇던 코드와 대괄호를 `hashlib.sha256((...).encode("utf-8")).hexdigest()`로 수정 | `check cache`<br>3/3 통과 |
| Claude Code | live 결과(`compare-live.json`, `cache-live.json`)를 읽고 `select_window`, `cache_key`의 `# 관측:` 주석 작성 | - 실제 입력 토큰은 추정값보다 약 3% 적음<br>- 요약과 최근 대화는 사실 3개를 유지하면서 전체 대화보다 243토큰 적음<br>- 캐시 첫 사용은 쓰기 비용 때문에 비사용보다 약 20% 비쌌고, 재사용에서만 읽기 1228토큰이 관측됨<br>- 지연은 재사용이 더 느려 속도 향상은 단정할 수 없음 | 주석 문장은 AI가 작성함 (직접 작성하지 않음) | `run compare --live`, `run cache --live` 실행<br>`tainted-document`, `unverified-tool`이 최종 입력에 없음을 확인 |

- AI는 풀이 방향과 오류 원인을 설명했고 코드는 직접 작성했습니다. `memory_action`과 `cache_key`는 쓸 메서드와 구조까지 설명을 받았습니다. `# 관측:` 주석 두 곳은 AI가 live 결과를 읽고 작성했습니다.
- 최종 확인: `check all` 16/16 통과
- 실제 연결: `run compare --live`, `run cache --live` 실행 완료. 결과는 `# 관측:` 주석에 반영함
