---
sidebar_position: 3
sidebar_label: "A3. 단일 진입점과 명령 표"
description: "모든 실행, 하위 프로세스까지 하나의 진입점과 명령 표를 거치게 해서 import 경로와 환경을 하나로 맞추는 방법입니다."
---

# 단일 진입점과 명령 표

모든 실행, 하위 프로세스까지 하나의 진입점과 명령 표를 거치게 해서 import 경로와 환경을 하나로 맞추는
방법입니다.

## 개념

- **진입점**은 사용자가 실행하는 파일입니다(`python run.py ...`).
- **명령 표**는 "명령 이름"과 "실행할 함수의 위치"를 짝지은 dict입니다.

## 사용 방법

- 실행할 수 있는 함수를 `{"이름": "module:function"}` 문자열 표에 등록합니다.
- 하위 프로세스는 항상 `python run.py exec <이름>`으로 띄웁니다.
- 진입점은 이름으로 표를 찾고, 그때 module을 import해서 함수를 부릅니다.

## 왜 필요한가

어떤 단계든 같은 `sys.path`, 같은 환경 설정, 같은 명령 표를 거칩니다. 그래서 "직접 실행하면 되는데 하위
프로세스에서는 import가 깨진다" 같은 문제가 생기지 않습니다. 명령 목록을 출력할 때는 문자열만 읽고 module을
import하지 않으므로 목록 출력도 가볍습니다.

## 예시

```python
# 예시: 문자열 명령 표와, 이름으로 함수를 찾아 부르는 dispatch
import importlib

COMMANDS = {
    "json.dumps": "json:dumps",
    "path.join": "os.path:join",
}


def dispatch(name: str, *args: str) -> object:
    # 등록되지 않은 이름이면 쓸 수 있는 이름을 함께 알립니다
    if name not in COMMANDS:
        raise ValueError(f"unknown command: {name}; available: {', '.join(sorted(COMMANDS))}")

    # 실행 직전에야 module을 import합니다
    module_name, function_name = COMMANDS[name].split(":")
    function = getattr(importlib.import_module(module_name), function_name)
    return function(*args)


print(dispatch("path.join", "data", "run.json"))  # data/run.json
```

## Self-Index에서의 사용

`src/selfindex/runtime/commands.py:10`, `:72`

```python
COMMANDS = {
    "pipeline.launch": "selfindex.runtime.execution.launch:main",
    "bc.agent": "browsecomp.agent.run_backbone:main",
    ...
}

def subprocess_argv(name, args=()):
    return [sys.executable, os.path.join(REPO_ROOT, "run.py"), "exec", name, *[str(arg) for arg in args]]
```

`dispatch()`(`commands.py:57`)는 `inspect.signature(function).bind(list(argv))`로 대상 함수가 `main(argv)`인지
인자 없는 `main()`인지 판별합니다. 인자 없는 함수면 `sys.argv`를 잠시 바꿔 부르고 `finally`에서 되돌립니다.
`main()`이 돌려준 값이 `bool`이면 exit code로 인정하지 않습니다(`exit_code()`, `:53`).

## 주의할 점

하위 프로세스를 띄우지 않는 단일 프로세스 도구라면 명령 표 없이 argparse subcommand로 충분합니다.
