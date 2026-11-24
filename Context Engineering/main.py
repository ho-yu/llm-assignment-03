"""main.py의 todo(...) 부분을 작성하세요. support.py와 checks.py는 그대로 사용합니다."""
import copy
import hashlib
import json
import sys

import support


def todo(message):
    raise NotImplementedError(message)


# 필수 1. 필요한 자료와 사용자 기억 관리하기
def select_context(items, user_id, now):
    kept = []
    for item in items:
        # allowed = todo("접근 범위, 신뢰, 현행 여부와 만료 조건")
        allowed = (
            item['user_id'] in ('public', user_id)
            and item['trusted']
            and item['active']
            and (item['expires_at'] is None or item['expires_at'] > now)
        )
        if allowed:
            kept.append(copy.deepcopy(item))
    # 이유: 높은 우선순위의 자료를 먼저 고르면 어떤 문제가 생기는지 적으세요.
    return sorted(kept, key=lambda item: (-item["priority"], item["id"]))


def memory_action(records, user_id, action, name, value=None):
    support.validate_memory_input(user_id, action, name, value)

    key = f"{user_id}:{name}"
    if action == "read":
        return copy.deepcopy(records.get(key))
    if action == "create":
        if key in records:
            raise ValueError("이미 있는 기억입니다. update를 사용하세요.")
        records[key] = copy.deepcopy(value)
    elif action == "update":
        if key not in records:
            raise KeyError("수정할 기억이 없습니다.")
        records[key] = copy.deepcopy(value)
    elif action == "delete":
        return records.pop(key, None)
    return copy.deepcopy(records[key])


def build_messages(prefix, question, context, turns, summary):
    data = json.dumps({"reference_data": context, "summary": summary}, ensure_ascii=False)
    history = [message for turn in turns for message in turn["messages"]]
    # 이유: 장기 기억과 세션 상태의 차이, 자료와 지시를 나누는 이유를 적으세요.
    # return todo("고정 지시, 참고 자료, 대화, 현재 질문 순서의 메시지")
    return [
            {"role": "developer", "content": prefix},
            {"role": "user", "content": data},
            *history,
            {"role": "user", "content": question},
            ]


# 필수 2. 긴 대화를 줄이고 반복 입력 재사용하기
def summarize(turns):
    summary = {}
    for turn in turns:
        for name, value in support.fact_lines(turn["messages"][0]["content"]):
            summary[name] = {"value": value, "source_turn_id": turn["id"]}
    return summary


def select_window(turns, limit, reserve, margin, make_messages, count):
    support.validate_budget(limit, reserve, margin)
    # budget = todo("입력에 쓸 수 있는 예산")
    budget = limit - reserve - margin
    if budget <= 0 or count(make_messages([])) > budget:
        raise ValueError("고정 입력만으로 예산을 넘었습니다.")
    kept = []
    for turn in reversed(turns):
        candidate = [turn, *kept]
        # if todo("전체 후보 입력이 예산을 넘는지"):
        if count(make_messages(candidate)) > budget:
            break
        kept = candidate
    # 관측: run compare --live 결과입니다. 실제는 API 입력 토큰, 추정은 count_tokens 값입니다.
    # - 전체 대화(한도 5000): 실제 1938 / 추정 1999토큰, T01~T07, 완전 일치 3/3
    # - 최근 대화(한도 2300): 실제 1699 / 추정 1744토큰, T05~T07, 완전 일치 0/3
    # - 요약과 최근 대화(한도 2300): 실제 1695 / 추정 1744토큰, T06~T07, 완전 일치 3/3
    # 빠진 사실: 최근 대화는 T02(승인조건)와 T04(담당자 이지훈, 마감일 2026-11-19)가 잘려
    # 담당자와 마감일을 "확인 필요"로 답했고, 승인조건도 정책 문서의 일반 문장만 말해 보안팀 검토가 빠졌습니다.
    # 선택: 요약과 최근 대화(한도 2300). 최근 대화와 비슷한 입력으로 사실 3개를 모두 맞혔고
    # 전체 대화보다 입력이 243토큰(약 12.5%) 적습니다. 요약에 최신 값이 남아 앞에서 정한 승인조건이 사라지지 않습니다.
    # 한계: 고정 지시가 입력 대부분(약 1250토큰)이라 절감폭은 작고, 조건당 호출이 1회뿐이라 일반화할 수 없습니다.
    return kept


def cache_key(prefix, user_id):
    # return todo("사용자와 고정 지시로 만드는 캐시 키")
    return hashlib.sha256((user_id + "\n" + prefix).encode("utf-8")).hexdigest()

    # 관측: run cache --live 결과입니다. 같은 요청을 캐시 비사용, 첫 사용, 재사용 순서로 3회 보냈습니다.
    # - 캐시 비사용: 입력 1533토큰, 읽기 0, 쓰기 0, 입력 비용 $0.0003066, 1539ms
    # - 첫 사용: 읽기 0, 쓰기 1228토큰, 입력 비용 $0.000368(비사용보다 약 20% 비쌈), 1303ms
    # - 재사용: 읽기 1228토큰, 쓰기 0, 입력 비용 $0.0000856(비사용보다 약 72% 저렴), 1835ms
    # 해석: 캐시 쓰기 단가(0.25)가 일반 입력(0.2)보다 높아 첫 사용은 오히려 더 비쌌습니다. 한 번 재사용한 뒤에야
    # 두 요청 합계($0.000454)가 캐시 없이 두 번 보낸 경우($0.000613)보다 낮아졌습니다.
    # 지연은 재사용이 1.3초에서 1.8초로 더 느렸고 요청마다 1회 측정이라 속도 향상은 단정할 수 없습니다.
    # 첫 사용의 cache_observation은 "읽기 0"이지만 쓰기 1228토큰이 계량되어 계량 누락은 아닙니다.
    # 오염 자료 확인: tainted-document와 unverified-tool은 trusted=False라 select_context에서 제외되며
    # cache와 compare 세 조건의 최종 입력 모두에서 id와 본문이 나오지 않음을 검사했습니다.


# 선택 심화 1. 새 대화만 반영하고 변경 이력 남기기
def merge_summary(previous, turns):
    return todo("선택 심화: 새 턴의 요약과 변경 이력")


if __name__ == "__main__":
    raise SystemExit(support.cli(sys.modules[__name__]))
