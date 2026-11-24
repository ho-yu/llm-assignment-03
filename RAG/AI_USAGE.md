# AI 사용 기록

AI는 개념 질문과 직접 작성한 코드의 오류 원인을 확인할 때 사용할 수 있습니다. 미작성 빈칸, 과제 전체, 평가 사례나 선택 심화의 설계를 대신 완성해 달라고 요청하지 않습니다. 실제 실행 결과를 만들거나 고쳐 달라고 요청하지 않습니다.

사용하지 않았다면 아래에 사용하지 않음이라고 적으세요. 사용했다면 필요한 만큼 기록하세요. API 키나 원문 개인정보를 대화에 넣지 않습니다.

사용 도구: Claude Code (VS Code 확장)

질문과 관련 함수:
- `prepare_chunks`, `build_index`, `search`, `rewrite_query`, `answer_question`: 빈칸별 힌트(키워드, 개념 설명)와 check 실패 원인 확인.
- `make_golden`: 평가 사례 작성 방법을 몰라 AI가 만든 예시를 받아 사용함.
- `measure`: 힌트를 여러 번 받고도 풀지 못해 `recall` 식의 정답을 AI에게 받음.

이해한 내용:
- 문단 공백 정리는 `split()`과 `join`, `chunk_id`는 f-string에서 `{}` 안의 식만 값으로 바뀐다는 점.
- Qdrant `must`는 조건 객체를 리스트에 쉼표로 나열해야 하며, `and`를 쓰면 한 조건만 남는다는 점.
- `replace`는 바꿀 대상 문자열(`rewritten`)에서 호출해야 한다는 점.
- 출처 검사는 `citations`의 각 ID가 `allowed`에 있는지 확인하는 것이며, 문서 Recall은 `expected & found`의 크기를 `expected`의 크기로 나눈 값이라는 점.

직접 수정한 부분:
- 코드는 직접 입력했고 check 실패 후 원인 설명을 보고 직접 고침.
- `make_golden`은 AI 예시를 붙여넣었고, `measure`의 `recall`은 AI가 알려준 식을 반영함.
- `# 이유:`, `# 관측:` 주석은 직접 작성함.

다시 실행한 명령과 확인 결과:
- `check index` 3개 중 3개 통과, `check answer` 2개 중 2개 통과, `check evaluate` 3개 중 3개 통과.
- `run index` 실행 완료.
