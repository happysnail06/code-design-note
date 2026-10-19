---
sidebar_position: 8
sidebar_label: "D8. 재시도할 오류 구분"
description: "재시도해도 소용없는 오류와 일시적인 오류를 나누고, 재시도 정책은 한 곳에서 정하는 방법입니다."
---

# 재시도할 오류 구분

재시도해도 소용없는 오류와 일시적인 오류를 나누고, 재시도 정책은 한 곳에서 정하는 방법입니다.

## 사용 방법

- HTTP 4xx는 요청 자체가 잘못된 것이므로 바로 올립니다. 다만 408(시간 초과)과 429(요청 과다)는 일시적인 오류로
  봅니다.
- 나머지 오류만 다음 replica로 넘겨 재시도합니다.
- OpenAI SDK client는 `max_retries=0`으로 만들어서, 재시도 정책을 SDK가 아니라 우리 코드 한 곳에서 정합니다.

## 왜 필요한가

잘못된 요청을 재시도하면 시간만 쓰고 결과는 같습니다. SDK와 우리 코드가 각자 재시도하면 실제 재시도 횟수가
곱해집니다.

## 예시

```python
# 예시: 재시도할 오류인지 판단하는 규칙을 한 함수에 모읍니다
def is_retryable(status: int) -> bool:
    # 4xx는 요청이 잘못된 것이지만, 408과 429는 기다리면 풀릴 수 있습니다
    if 400 <= status < 500:
        return status in (408, 429)
    return True


print([is_retryable(code) for code in (400, 404, 408, 429, 500, 503)])
# [False, False, True, True, True, True]
```

## Self-Index에서의 사용

`llm/requests.py:11`, `llm/client.py:49`, `endpoints.py:68`, `oss_client_ours.py:78`.
