# AI 사용 기록

AI는 개념 설명과 직접 작성한 코드의 오류 원인 확인에 사용할 수 있습니다. 과제 전체, 미작성 TODO, 프롬프트 문장, 선택 심화 설계를 대신 완성하도록 요청하지 않습니다.

사용하지 않았다면 아래에 사용하지 않음이라고 적습니다. 사용했다면 필요한 만큼 항목을 추가하세요. API 키나 개인정보는 기록하지 않습니다.

- 사용 도구: Claude Code (VS Code 확장, Claude Sonnet 5.5)
- 사용 방식: 처음에 "정답 코드는 알려 주지 말고 1번부터 단계별로 힌트만 달라"고 요청했습니다. 함수 하나를 직접 작성할 때마다 확인을 요청했고, 검사 실행과 오류 원인 설명을 받았습니다. 힌트는 무관한 예제 코드, 빈칸 채우기 형태의 구조, 직접 실행해 볼 파이썬 한 줄 실험으로 받았습니다. 제출 코드와 지시문 문장은 AI가 대신 써 주지 않았고 직접 입력했습니다. 선택 심화 `decide_rollout`은 하지 않았고 AI에게 요청하지도 않았습니다.

## 질문한 내용

- 과제 구조와 진행 순서를 설명해 달라고 했습니다.
- `mask_text`: 이메일 치환 결과에 전화번호 치환을 이어 붙이는 방법과 제공된 `PHONE` 패턴의 한계를 물었습니다.
- `validate_reply`: 직접 쓴 코드를 확인받았습니다. `AttributeError`, `NameError`, 출처 비교가 틀린 이유를 설명받았습니다.
- `candidate_policy`: 직접 쓴 코드의 문법 오류(`return` 뒤 줄바꿈, 따옴표 충돌, 반환 타입)의 원인을 확인받았습니다. 지시문 내용은 ASSIGNMENT의 네 규칙을 직접 옮겨 썼고, AI에게 문장을 써 달라고 요청하지 않았습니다.
- `generation_fields`: 반환해야 하는 사전의 구조와 마스킹 적용 위치를 힌트로 받았습니다.
- `evaluate_case`: 직접 쓴 식이 틀린 이유와 제공 검사로 확인되지 않는 경우를 확인받았습니다.
- `summarize`, `release_gate`: 직접 작성한 뒤 확인받았습니다.
- 실제 비교 결과(`compare-live.json`, `verification-live.json`)를 읽을 때 무엇을 확인해야 하는지 물었습니다. `FEEDBACK` 값과 관측 및 판단 주석은 AI에게 적어 달라고 요청하지 않았습니다.

## 이해한 내용

- 제공 검사를 통과해도 의도대로 동작한다는 보장은 없습니다. `validate_reply`는 비교 방향이 반대였는데 허용 출처가 하나뿐인 검사에서는 우연히 통과했습니다. `evaluate_case`는 출처 비교가 빠져 있어도 제공 검사를 통과했습니다. 경계 상황을 직접 만들어 실행해 확인해야 합니다.
- 리스트에 `in`을 쓰면 원소 하나가 들어 있는지를 묻는 것이고, 출처 목록이 허용 목록의 부분집합인지는 `set`의 `<=`로 확인합니다. 출처가 서로 같은지는 `set(...) == set(...)`로 비교합니다. 순서가 달라도 같고, 많거나 적으면 다릅니다.
- `a == b == c`는 세 값이 서로 같은지를 묻습니다. 모두 `False`여도 `True`가 되므로, "모두 만족"은 `and`로 연결해야 합니다.
- Langfuse에 기록하는 `output`은 마스킹한 문자열이어야 합니다. 사용량이 없을 때는 0이나 빈 값으로 바꾸지 않고 `None`으로 둡니다.
- 지표 분모가 다릅니다. 오류율은 전체 요청 기준이고, 긍정 피드백 비율은 응답한 요청만 기준입니다. 비용 `None`(미확인)과 `0.0`(확인된 0원)은 구분합니다.
- `release_gate`의 `approve`는 이번 작은 평가셋의 검토 조건이며 실제 배포 승인이 아닙니다. `verify`의 `all_verified=true`는 서버 기록이 일치한다는 뜻이고 답변 품질 통과와는 별개입니다. `passed`는 직접 작성한 문자열 검사 결과이며 Langfuse가 사실성을 판정한 것이 아닙니다.
- 실제 비교에서 baseline 요청 2건이 `validate` 단계의 `ValueError`로 오류 처리된 것을 결과 파일에서 확인했습니다.

## 직접 수정한 부분

- `main.py`의 `mask_text`, `validate_reply`, `candidate_policy`, `generation_fields`, `evaluate_case`, `summarize`, `release_gate`를 직접 작성하고, AI가 알려 준 오류 원인에 따라 여러 번 직접 고쳤습니다.
- 힌트 중 일부는 빈칸 채우기 형태의 구조로 받았습니다. 그 구조를 보고 변수 이름과 식을 직접 입력했습니다.

## 다시 실행한 명령과 확인 결과

- `uv run --frozen python main.py demo`: 자료 준비 확인 통과.
- `uv run --frozen python main.py check observe`: 15/15 통과.
- `uv run --frozen python main.py run observe`: 4개 사례 모두 `retrieve → ticket-status → generate → validate` 순서로 `ok` 확인.
- `uv run --frozen python main.py run metrics`: 요청 4, 오류율 0.5, p95 400ms, 토큰과 비용 `null`, 피드백 응답 2, 긍정 비율 0.5로 ASSIGNMENT의 기대값과 일치.
- `uv run --frozen python main.py check compare`: 15/15 통과.
- `uv run --frozen python main.py run compare`: 기준선 2/4, 후보 3/4, `approve=false`(`direct`에서 회귀와 중요 실패).
- AI가 제가 정한 경계 상황으로 `validate_reply`, `evaluate_case`, `summarize`를 별도 스크립트로 점검한 결과, 수정 후 모두 기대대로 나왔습니다.
- `uv run --frozen python main.py run compare --live`: baseline 2/4(오류 요청 2건), 후보 4/4, `approve=true`.
- `uv run --frozen python main.py verify`: `all_verified=true`, 8개 Trace의 단계, 부모 관계, 마스킹, 사용량이 서버 기록과 일치.
