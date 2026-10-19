---
sidebar_position: 4
sidebar_label: "A4. 실행 전 전체 검증"
description: "할 일 전체를 plan으로 만들고 모두 검증한 뒤에 첫 단계를 실행하는 방법입니다."
---

# 실행 전 전체 검증

할 일 전체를 plan으로 만들고 모두 검증한 뒤에 첫 단계를 실행하는 방법입니다.

## 개념

plan은 "어떤 단계를 어떤 설정으로 어떤 순서로 실행할지"를 담은 불변 객체입니다.

## 사용 방법

실행을 네 단계로 나눕니다.

1. 할 일을 plan으로 만듭니다.
2. plan 전체를 검증합니다.
3. 모든 단계의 실행 객체를 만듭니다.
4. 첫 단계를 실행합니다.

## 왜 필요한가

세 번째 단계의 설정이 틀렸다는 사실을 첫 단계를 몇 시간 돌린 뒤에 알게 되는 일을 막습니다. plan을 출력만 하고
끝내면 `--dry-run`이 됩니다.

## 예시

```python
# 예시: 모든 단계를 검사한 뒤에야 첫 단계를 실행합니다
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Step:
    name: str
    input_path: str


def validate(plan: tuple[Step, ...]) -> None:
    # 입력 파일이 없는 단계를 모두 모아 한 번에 알립니다
    if missing := [step.name for step in plan if not Path(step.input_path).exists()]:
        raise ValueError(f"inputs are missing for steps: {missing}")


def run(plan: tuple[Step, ...]) -> None:
    validate(plan)
    for step in plan:
        print("running", step.name)


plan = (Step("encode", "."), Step("search", "no/such/file"))
try:
    run(plan)
except ValueError as error:
    # "running encode"도 출력되지 않고 바로 실패합니다
    print(error)  # inputs are missing for steps: ['search']
```

## Self-Index에서의 사용

`src/selfindex/runtime/runner.py:53`

```python
def run_experiment(self, spec: ExperimentSpec) -> int:
    plan = self.plan(spec)

    validate_services(plan)
    tasks = self._build_tasks(plan)
    for step, task in zip(plan.steps, tasks, strict=True):
        ...
        if (code := task.run()) != 0:
            return code
    return 0
```

## 주의할 점

앞 단계의 출력을 봐야 다음 단계를 정할 수 있는 동적 workflow에는 그대로 맞지 않습니다. 그런 경우에도 미리 알 수
있는 검사(서비스 설정, 경로, 이름)는 첫 단계 전에 끝냅니다.
