# Self-Index에서 배울 수 있는 설계 지식

**이 문서의 출발점은 [augustinLib/Self-Index](https://github.com/augustinLib/Self-Index)입니다.
원본 코드와 설계의 크레딧은 Self-Index 저자와 기여자에게 있습니다.**

Self-Index의 [commit `9c6fade`](https://github.com/augustinLib/Self-Index/tree/9c6fade)를 분석해,
다른 프로젝트에서도 참고할 수 있는 설계 지식을 정리했습니다. 설명용 예시와 적용 규칙은 이 학습 노트에서
정리한 내용이며, 실제 레포 코드와 구분해 표시했습니다.

[코딩 규약](./coding-convention.md)은 적용할 규칙을, 이 문서는 그 의미와 이유를 설명합니다.
통계와 코드 위치를 기록한 [분석 원본](https://github.com/happysnail06/code-design-note/blob/main/sources/self-index-coding-conventions.md)도 함께 제공합니다.

문서는 다음 순서로 되어 있습니다.

1. **먼저 알아 둘 개념**: 이 문서에 나오는 용어를 묶음별로 설명합니다.
2. **한눈에 보기**: 모든 주제를 한 줄 설명과 함께 모았습니다.
3. **상세 분석**: 주제마다 하나씩 정리했습니다. 각 주제는 이름과 한 문장 설명으로 시작하고, 다음 절이
   이어집니다. 해당하지 않는 절은 생략했습니다.
   - **개념**: 이 주제의 핵심 개념입니다.
   - **사용 방법**: 무엇을 어떻게 하는지입니다.
   - **왜 필요한가**: 그렇게 하면 어떤 문제가 없어지는지입니다.
   - **예시**: 레포와 상관없이 이해할 수 있게 만든 작은 Python 코드입니다. `# 예시`로 시작하는 코드는 모두
     실제로 실행해서 확인했습니다.
   - **Self-Index에서의 사용**: 레포의 실제 코드 발췌와 위치(`파일:줄`)입니다. 줄인 곳은 `...`로
     표시했습니다.
   - **주의할 점**: 이 방법이 맞지 않는 상황과 한계입니다.

---

## 1. 먼저 알아 둘 개념

용어는 영어로 적고, 설명은 한국어로 적었습니다. Python 코드에서 쓰는 형태는 "Python 표기" 열에 따로
두었습니다.

### 설계 개념

언어와 상관없이 쓰는 설계 용어입니다.

| 용어 | 설명 | 관련 주제 |
|---|---|---|
| interface | 구현이 지켜야 하는 약속입니다. "어떤 이름의 메서드가 어떤 인자를 받아 무엇을 돌려준다"를 정합니다. 이 레포는 interface를 담은 파일을 `contracts.py`라고 부릅니다. | B1 |
| adapter | 외부 서비스, 외부 라이브러리, 다른 저장소의 코드를 부르고, 그 입출력을 우리 코드의 형식으로 바꿔 주는 코드입니다. | A1 |
| upstream | 우리가 가져다 쓰는 다른 저장소의 원본 코드입니다. 이 레포에서는 benchmark 저장소들이 upstream입니다. | A1, B4 |
| lazy import | 파일 첫머리가 아니라, 그 모듈이 필요한 함수 안에서 하는 import입니다. 함수를 부를 때에야 import됩니다. | A2 |
| template method | 기본 클래스가 처리 순서를 정하고, 하위 클래스는 그중 일부 단계만 채우는 설계 방식입니다. | B2 |
| hook | 하위 클래스가 원할 때만 override하는, 기본 동작이 비어 있는 메서드입니다. | B2 |
| registry | 이름을 키로 구현을 등록해 두고, 실행할 때 이름으로 꺼내 쓰는 표입니다. | B3 |
| mixin | 혼자서는 쓰지 않고, 다른 클래스와 함께 상속해서 기능을 덧붙이는 작은 클래스입니다. | B4 |
| MRO | Method Resolution Order의 약자로, 여러 클래스를 상속했을 때 메서드를 찾는 순서입니다. `class C(A, B)`이면 C, A, B 순서로 찾고, `super()`는 이 순서에서 다음 클래스를 가리킵니다. | B4 |
| proxy | 원래 객체를 속성으로 보관하고, 일부 메서드만 바꾸고 나머지는 원래 객체에 넘기는 객체입니다. wrapper라고도 부릅니다. | B5 |
| dependency injection | 필요한 객체나 함수를 내부에서 생성하지 않고 인자로 전달받는 방식입니다. | B1 |
| strategy | 같은 역할의 구현을 교체할 수 있도록 공통 interface로 분리한 동작입니다. | B1 |
| snapshot과 read lease | snapshot은 조회할 index 상태를 일정하게 유지하고, read lease는 조회가 끝날 때까지 변경을 제한합니다. | C7 |
| checkpoint | 완료한 단계와 산출물을 기록해 중단된 실행을 재개할 때 확인하는 정보입니다. | D5 |
| provenance | 결과를 만든 코드, 설정, 데이터, 실행 환경의 기록입니다. | D5 |
| sentinel | "값이 없음"을 표시하려고 만든 특별한 객체입니다. `None`도 정상 값으로 쓰일 때 필요합니다. | C7, C12 |
| atomic replace | 새 파일을 다 쓴 뒤 한 번에 교체하는 것입니다. 다른 프로세스는 이전 파일 아니면 완성된 새 파일만 보게 됩니다. | D1 |

### 클래스와 타입

Python에서 클래스와 타입을 정의할 때 쓰는 기능입니다.

| 용어 | Python 표기 | 설명 | 관련 주제 |
|---|---|---|---|
| ABC | `abc.ABC` | Abstract Base Class의 약자로, interface를 클래스로 표현한 것입니다. 미구현 abstract method가 남아 있으면 객체를 만들 수 없습니다. | B1, C6 |
| abstract method | `@abstractmethod` | ABC 안에서 "하위 클래스가 반드시 구현해야 하는 메서드"를 표시합니다. 하나라도 구현하지 않은 하위 클래스로 객체를 만들면 `TypeError`가 납니다. | B1, C6 |
| Protocol | `typing.Protocol` | 상속하지 않아도, 정해진 메서드만 가지고 있으면 같은 타입으로 인정하는 interface입니다. 타입 검사기가 확인하고, 실행 중에는 아무것도 강제하지 않습니다. | B1, B6 |
| dataclass | `@dataclass` | 필드만 적으면 `__init__`, `__repr__`, `__eq__`를 자동으로 만들어 주는 decorator입니다. | C1 |
| frozen dataclass | `@dataclass(frozen=True)` | 만든 뒤에는 필드에 다시 대입할 수 없는 dataclass입니다. 대입하면 `FrozenInstanceError`가 납니다. | C1 |
| NamedTuple | `typing.NamedTuple` | 필드 이름이 붙은 tuple입니다. `a, b = result`처럼 풀어서 받을 수 있고 `result.a`처럼 이름으로도 읽을 수 있습니다. | C2 |
| Mapping | `collections.abc.Mapping` | dict처럼 읽을 수 있는 객체의 추상 클래스입니다. 세 메서드만 구현하면 `in`, `.get()`, `.items()`가 따라옵니다. | C10 |
| MappingProxyType | `types.MappingProxyType` | dict를 읽기 전용으로 보여 주는 표준 라이브러리 타입입니다. | C1 |
| Callable | `collections.abc.Callable` | "괄호를 붙여 부를 수 있는 것"을 뜻하는 타입입니다. 함수, lambda, `__call__`을 가진 객체가 모두 해당합니다. | B6 |

### decorator

함수나 클래스 정의 위에 `@`로 붙이는 기능입니다.

| 용어 | Python 표기 | 설명 | 관련 주제 |
|---|---|---|---|
| property | `@property` | 메서드를 속성처럼 읽게 합니다. `obj.size()` 대신 `obj.size`로 씁니다. | C3 |
| classmethod | `@classmethod` | 객체가 아니라 클래스를 첫 인자(`cls`)로 받는 메서드를 만듭니다. 객체 없이 `ClassName.method()`로 부릅니다. | C4 |
| staticmethod | `@staticmethod` | `self`도 `cls`도 받지 않는 메서드를 만듭니다. 클래스 안에 둔 일반 함수와 같습니다. | C5 |
| contextmanager | `@contextlib.contextmanager` | `yield` 하나가 있는 함수로 context manager를 만들게 해 줍니다. `yield` 앞이 준비, 뒤가 정리입니다. | C7 |
| cache | `@functools.cache` | 같은 인자로 다시 부르면 함수를 실행하지 않고 저장해 둔 결과를 돌려주게 합니다. | C8 |
| class decorator | `@register("name")` 형태 | 클래스 정의 위에 붙여서 클래스를 받아 처리하는 decorator입니다. 등록에 자주 씁니다. | B3, C4 |

### 특수 메서드

Python이 정해진 때에 자동으로 부르는 메서드입니다.

| 메서드 | 불리는 때 | 이 문서에서의 쓰임 | 관련 주제 |
|---|---|---|---|
| `__post_init__` | dataclass가 자동으로 만든 `__init__`이 끝난 직후 | 입력 검사와 정규화 | C1 |
| `__init_subclass__` | 하위 클래스가 정의되는 순간 | 하위 클래스 자동 등록 | C9 |
| `__getattr__` | 객체에 없는 속성을 읽으려 할 때 | proxy가 나머지 속성을 원래 객체에 넘김 | B5 |
| `__call__` | 객체를 `obj()`처럼 부를 때 | 값을 들고 있는 실행 단위 | B6 |
| `__enter__`, `__exit__` | `with` 블록에 들어갈 때와 나올 때 | 자원 준비와 정리 | C7 |

### 그 밖의 Python 기능

| 용어 | Python 표기 | 설명 | 관련 주제 |
|---|---|---|---|
| context manager | `with` 문 | 블록에 들어갈 때 준비하고, 블록을 나올 때(예외가 나도) 정리하는 객체입니다. | C7 |
| BaseException | `BaseException` | 모든 예외의 뿌리입니다. 일반 오류는 그 아래의 `Exception`을 상속합니다. `BaseException`을 직접 상속한 예외는 `except Exception`에 잡히지 않습니다. | C11 |
| TYPE_CHECKING | `if typing.TYPE_CHECKING:` | 타입 검사기만 읽고 실행 중에는 건너뛰는 블록입니다. 타입 표기에만 필요한 import를 여기에 둡니다. | B1 |
| walrus | `:=` | 값을 변수에 넣으면서 그 값을 바로 식에서 쓰게 하는 연산자입니다. | C12 |
| keyword-only argument | `def f(a, *, b)` | 함수 정의에서 `*` 뒤에 둔 인자입니다. 호출할 때 반드시 `b=값`처럼 이름을 붙여 넘겨야 합니다. | C12 |

---

## 2. 한눈에 보기

### A. 프로젝트 구성과 실행 흐름

- **[A1] Adapter와 upstream**: 외부 서비스, 외부 라이브러리, 다른 저장소의 코드와 닿는 부분을 adapter 한 곳에
  모으고, 가져온 외부 코드는 고치지 않습니다.
- **[A2] Lazy import**: 일부 기능에서만 필요한 모듈은 그 기능을 실행하는 함수 안에서 import해서, 그 모듈이
  없는 환경에서도 나머지 기능이 돌게 합니다.
- **[A3] 단일 진입점과 명령 표**: 모든 실행, 하위 프로세스까지 하나의 진입점과 명령 표를 거치게 해서 import
  경로와 환경을 하나로 맞춥니다.
- **[A4] 실행 전 전체 검증**: 할 일 전체를 plan으로 만들고 모두 검증한 뒤에 첫 단계를 실행합니다.
- **[A5] 소스 파일 기준 경로**: 경로를 작업 디렉터리가 아니라 소스 파일 위치에서 계산해서, 어디서 실행해도
  같은 파일을 가리키게 합니다.
- **[A6] 저장소 문서의 역할 분담**: 문서마다 맡는 내용을 나누고, 코드의 설정 표와 문서의 표를 맞춰 둡니다.

### B. 인터페이스와 객체 설계

- **[B1] ABC와 Protocol**: interface와 구현을 다른 파일에 두고, 상속은 한두 단계에서 끝냅니다.
- **[B2] Template method와 hook**: 하위 클래스가 채우는 `build()`와 바깥에서 부르는 `create()`를 나눠서,
  확장 코드의 실수를 경계에서 잡습니다.
- **[B3] Registry**: 구현을 이름으로 등록하고 이름으로 꺼내 씁니다. 등록할 때 이름 중복과 추상 클래스를
  거부합니다.
- **[B4] Mixin**: 외부 클래스를 고치지 않고, 함께 상속하는 작은 클래스로 기능을 덧붙입니다.
- **[B5] Proxy**: 객체를 감싸서 일부 메서드만 바꾸고 나머지는 원래 객체에 넘깁니다.
- **[B6] Callable**: 실행할 동작을 함수, lambda, 호출 가능한 객체로 전달받습니다.
- **[B7] Context와 상태 객체**: 단계 사이에 넘기는 값 묶음에서 입력과, 실행 중 바뀌는 상태를 나눠 담습니다.

### C. decorator와 언어 기능

- **[C1] Dataclass**: 바뀌지 않는 값은 frozen dataclass, 바뀌는 상태는 일반 dataclass로 만듭니다.
- **[C2] NamedTuple**: 풀어서 받는 작은 반환값과 JSON으로 내보낼 작은 레코드에 씁니다.
- **[C3] Property**: 파생 값, 지연 로드, 추상 속성, 상태를 확인해야 하는 값의 네 경우에 씁니다.
- **[C4] Classmethod**: 이름 있는 생성자, 객체 없이 하는 검사, 등록 decorator에 씁니다.
- **[C5] Staticmethod**: 그 클래스 안에서만 쓰는 private helper에만 씁니다.
- **[C6] Abstract method**: 필수 기능은 abstract method로, 일부 구현만 지원하는 기능은 이유를 밝히는 오류로
  둡니다.
- **[C7] Context manager**: 한 함수 안에서 상태를 바꾸고 복원할 때는 `@contextmanager`, 객체의 자원 사용과
  정리를 관리할 때는 `__enter__`/`__exit__`를 씁니다.
- **[C8] Cache**: 성공한 외부 조회만 기억하게 해서 같은 조회를 한 번만 합니다.
- **[C9] `__init_subclass__`**: 하위 클래스를 정의하는 순간 자동으로 등록합니다.
- **[C10] Mapping**: 읽기 전용 표를 세 메서드만으로 만듭니다.
- **[C11] BaseException**: 외부 코드의 `except Exception`에 잡히면 안 되는 신호를 만듭니다.
- **[C12] 작은 언어 기능**: walrus, keyword-only argument, `zip(strict=True)`, sentinel 같은 기법을 모았습니다.

### D. 실패에 대비하는 방법

- **[D1] Atomic replace**: 임시 파일에 다 쓴 뒤 한 번에 교체해서 반쯤 쓴 파일이 남지 않게 합니다.
- **[D2] 디렉터리 교체와 backup**: 새 디렉터리를 따로 완성하고, 이전 것을 backup으로 옮긴 뒤 교체합니다.
- **[D3] 되돌릴 수 있는 순서**: 실패할 수 있는 단계를 먼저, 되돌리기 어려운 단계를 나중에 합니다.
- **[D4] 기다리지 않는 파일 lock**: 여러 프로세스가 같은 산출물을 쓰려 하면 기다리지 않고 바로 실패시킵니다.
- **[D5] 재개 검증**: 중단된 작업을 재개하기 전에 해시로 실행 조건과 산출물이 같은지 확인합니다.
- **[D6] 저장 형식 version**: 저장 형식에 version을 넣고, 읽을 때 version, shape, 수치를 검사합니다.
- **[D7] 외부 코드 전제 검사**: adapter가 기대는 외부 코드의 전제를 실행 전에 검사합니다.
- **[D8] 재시도할 오류 구분**: 재시도해도 소용없는 오류와 일시적인 오류를 나누고, 재시도 정책은 한 곳에서
  정합니다.
- **[D9] 결과 검사**: 다음 단계로 넘기기 전에 결과의 개수와 수치를 검사합니다.

### E. 설계할 때 주의할 점

실패와 정상 결과의 구분, 입력 검증, 상태 관리, 공통 설정, 공개 interface를 설계할 때의 주의점과 판단 기준을 정리했습니다.

---

## 3. 상세 분석

### A. 프로젝트 구성과 실행 흐름

패키지의 역할과 의존 관계, 실행 순서, 경로와 문서 관리 방법을 다룹니다.

#### A1. Adapter와 upstream

외부 서비스, 외부 라이브러리, 다른 저장소의 코드와 닿는 부분을 adapter 한 곳에 모으고, 가져온 외부 코드는
고치지 않는 방법입니다.

##### 개념

- **adapter**는 외부 코드를 부르고, 그 입출력을 우리 코드의 형식으로 바꿔 주는 코드입니다. 우리 코드는
  adapter가 돌려준 값만 보고, 외부 코드가 어떻게 생겼는지는 알 필요가 없습니다.
- **upstream**은 우리가 가져다 쓰는 다른 저장소의 원본 코드입니다. Self-Index에서는 BrowseComp, LongMemEval
  같은 benchmark 저장소가 upstream입니다.

##### 사용 방법

- 패키지는 하는 일(실행, 알고리즘, index, 검색, 저장)로 나눕니다.
- 외부와 닿는 코드는 `adapters/`에, 외부 코드 자체는 `externals/`에 따로 둡니다.
- upstream은 git submodule로 commit을 고정하고 고치지 않습니다. upstream의 동작을 바꿔야 하면 adapter에서
  처리합니다(B4, B5, C7).

##### 왜 필요한가

알고리즘만 고치는 사람은 `adapters/`를 몰라도 되고, benchmark 연결만 고치는 사람은 알고리즘을 몰라도 됩니다.
upstream이 바뀌어도 고칠 곳이 `adapters/` 안에서 끝납니다.

##### 예시

```python
# 예시: 외부 검색 client의 응답을 우리 형식(SearchHit)으로 바꾸는 adapter
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchHit:
    """우리 코드가 쓰는 검색 결과 형식입니다."""

    doc_id: str
    score: float


class ExternalClient:
    """외부 라이브러리라고 가정합니다. 응답 형식은 우리가 정하지 않습니다."""

    def query(self, text: str) -> dict:
        return {"results": [{"id": 7, "relevance": "0.82"}, {"id": 3, "relevance": "0.40"}]}


class ExternalSearchAdapter:
    """외부 client를 부르고 응답을 SearchHit 목록으로 바꿉니다."""

    def __init__(self, client: ExternalClient) -> None:
        self._client = client

    def search(self, text: str) -> list[SearchHit]:
        # 외부 응답의 필드 이름과 타입은 이 메서드 안에서만 다룹니다
        response = self._client.query(text)
        return [SearchHit(str(row["id"]), float(row["relevance"])) for row in response["results"]]


print(ExternalSearchAdapter(ExternalClient()).search("apple"))
# [SearchHit(doc_id='7', score=0.82), SearchHit(doc_id='3', score=0.4)]
```

외부 라이브러리가 `relevance`를 `score`로 바꾸더라도 고칠 곳은 `ExternalSearchAdapter.search` 한 메서드입니다.

##### Self-Index에서의 사용

디렉터리 지도입니다.

```
run.py (187줄)                    유일한 CLI 진입점. sys.path에 src/, adapters/를 올리고 Runner를 부른다.
setup.sh                          set -euo pipefail. submodule, 가상환경, repo.check까지 한 번에 준비한다.
pyproject.toml / uv.lock          의존성은 == 고정, lock 커밋, optional group(.[browsecomp], .[longmem]).
.env.example                      환경 변수마다 한 줄 설명. 실제 .env는 무시한다.
docs/REPRODUCING.md               보고된 수치를 재현하는 정확한 명령.
docs/ARTIFACTS.md                 산출물 파일별 내용과 필드.
externals/                        upstream benchmark 코드. submodule로 commit을 고정하고 수정하지 않는다.
src/selfindex/                    framework 본체 (91파일, 약 6,100줄)
├─ runtime/   (21파일, 1,359줄)   실험을 계획하고 실행한다. registry, catalog, factory, 명령 표, 환경.
├─ pipeline/  (22파일, 1,878줄)   index evolution 알고리즘. engine(round loop), optimizer, strategies.
├─ index/     (4파일, 470줄)      key index의 계약과 dense·lexical 구현.
├─ retrieval/ (8파일, 702줄)      retriever 계약, BM25, dense, snapshot, view.
├─ validation/(5파일, 237줄)      생성된 key를 점수로 걸러 내는 criterion.
├─ encoding/  (3파일, 144줄)      text encoder 계약과 구현.
├─ llm/       (4파일, 265줄)      HTTP client, backbone(모델별 요청 차이), 오류 분류.
├─ storage/   (4파일, 213줄)      원자적 쓰기, key 게시, provenance.
├─ evaluation/, exploration/, revision/, data/
└─ common/    (11파일, 450줄)     prompt 상수, JSON 파싱, 모델 이름표.
adapters/                         외부 benchmark와 framework를 잇는 코드 (37파일, 약 3,200줄)
├─ browsecomp/  adapters/ agent/ costs/ pipeline/
└─ longmem/adapter/
```

##### 주의할 점

외부 연동이 하나뿐인 작은 프로젝트에서는 최상위 디렉터리까지 나눌 필요가 없습니다. 연동 코드를 모듈 하나에
모으면 충분합니다.

#### A2. Lazy import

일부 기능에서만 필요한 모듈은 그 기능을 실행하는 함수 안에서 import해서, 그 모듈이 없는 환경에서도 나머지
기능이 돌게 하는 방법입니다.

##### 개념

lazy import는 파일 첫머리가 아니라 함수 안에서 하는 import입니다. 그 함수를 부를 때에야 import되므로, 그
함수를 쓰지 않는 실행에서는 해당 모듈이 설치되어 있지 않아도 됩니다.

##### 사용 방법

- adapter(A1)는 핵심 패키지(`selfindex`)를 파일 첫머리에서 자유롭게 import합니다.
- 핵심 패키지는 adapter를 파일 첫머리에서 import하지 않습니다. adapter가 필요한 메서드 안에서만 import합니다.
- torch, pyserini처럼 무겁거나 설치가 선택인 라이브러리도 실제로 쓰는 함수 안에서만 import합니다. 이 레포에는
  이런 import가 146곳 있습니다.

##### 왜 필요한가

framework만 설치한 환경에서도 `python run.py list`와 retrieval 실험이 돌아갑니다. 무거운 라이브러리를 import하는
시간도 그 기능을 쓰는 실행에만 듭니다.

##### 예시

```python
# 예시: 무거운 라이브러리는 그것이 필요한 함수 안에서만 import합니다
def keyword_score(query: str, doc: str) -> int:
    # 표준 기능만 쓰므로 어떤 환경에서도 동작합니다
    return sum(word in doc.split() for word in query.split())


def dense_score(query: str, doc: str) -> float:
    # torch는 이 함수를 부를 때만 필요하므로 여기서 import합니다
    import torch

    ...


# torch가 설치되지 않은 환경에서도 이 줄은 실행됩니다
print(keyword_score("red apple", "an apple a day"))  # 1
```

##### Self-Index에서의 사용

`src/selfindex/runtime/catalog/benchmarks.py:121`

```python
@staticmethod
def _search_adapter(spec):
    from browsecomp.adapters.search_factory import search_adapter_name
    from selfindex.runtime.catalog.retrievers import RETRIEVERS
    ...
```

##### 주의할 점

lazy import는 "모듈이 없다"는 오류를 실행 도중으로 미룹니다. 프로그램 전체가 그 라이브러리 없이 돌 수 없다면
파일 첫머리에서 import해서, 시작하자마자 실패하게 둡니다.

#### A3. 단일 진입점과 명령 표

모든 실행, 하위 프로세스까지 하나의 진입점과 명령 표를 거치게 해서 import 경로와 환경을 하나로 맞추는
방법입니다.

##### 개념

- **진입점**은 사용자가 실행하는 파일입니다(`python run.py ...`).
- **명령 표**는 "명령 이름"과 "실행할 함수의 위치"를 짝지은 dict입니다.

##### 사용 방법

- 실행할 수 있는 함수를 `{"이름": "module:function"}` 문자열 표에 등록합니다.
- 하위 프로세스는 항상 `python run.py exec <이름>`으로 띄웁니다.
- 진입점은 이름으로 표를 찾고, 그때 module을 import해서 함수를 부릅니다.

##### 왜 필요한가

어떤 단계든 같은 `sys.path`, 같은 환경 설정, 같은 명령 표를 거칩니다. 그래서 "직접 실행하면 되는데 하위
프로세스에서는 import가 깨진다" 같은 문제가 생기지 않습니다. 명령 목록을 출력할 때는 문자열만 읽고 module을
import하지 않으므로 목록 출력도 가볍습니다.

##### 예시

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

##### Self-Index에서의 사용

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

##### 주의할 점

하위 프로세스를 띄우지 않는 단일 프로세스 도구라면 명령 표 없이 argparse subcommand로 충분합니다.

#### A4. 실행 전 전체 검증

할 일 전체를 plan으로 만들고 모두 검증한 뒤에 첫 단계를 실행하는 방법입니다.

##### 개념

plan은 "어떤 단계를 어떤 설정으로 어떤 순서로 실행할지"를 담은 불변 객체입니다.

##### 사용 방법

실행을 네 단계로 나눕니다.

1. 할 일을 plan으로 만듭니다.
2. plan 전체를 검증합니다.
3. 모든 단계의 실행 객체를 만듭니다.
4. 첫 단계를 실행합니다.

##### 왜 필요한가

세 번째 단계의 설정이 틀렸다는 사실을 첫 단계를 몇 시간 돌린 뒤에 알게 되는 일을 막습니다. plan을 출력만 하고
끝내면 `--dry-run`이 됩니다.

##### 예시

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

##### Self-Index에서의 사용

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

##### 주의할 점

앞 단계의 출력을 봐야 다음 단계를 정할 수 있는 동적 workflow에는 그대로 맞지 않습니다. 그런 경우에도 미리 알 수
있는 검사(서비스 설정, 경로, 이름)는 첫 단계 전에 끝냅니다.

#### A5. 소스 파일 기준 경로

경로를 작업 디렉터리가 아니라 소스 파일 위치에서 계산해서, 어디서 실행해도 같은 파일을 가리키게 하는
방법입니다.

##### 개념

`Path(__file__)`은 지금 실행 중인 소스 파일의 경로입니다. `.parents[N]`은 그 파일에서 N+1단계 위의
디렉터리입니다.

##### 사용 방법

- 모든 경로 상수는 `Path(__file__).resolve().parents[N]`에서 출발합니다.
- upstream 코드를 `sys.path`에 올리는 일은 `_bootstrap.py` 한 파일만 합니다.

##### 왜 필요한가

어느 디렉터리에서 실행하든 같은 파일을 가리킵니다. import 경로를 바꾸는 코드가 한 곳에만 있으므로, import
문제가 생기면 그 파일만 보면 됩니다.

##### 예시

```python
# 예시: 작업 디렉터리 대신 소스 파일 위치에서 경로를 계산합니다
from pathlib import Path

# 이 파일이 <repo>/src/tool/paths.py라면 parents[2]는 <repo>입니다
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
print(DATA_DIR.name)  # data
```

##### Self-Index에서의 사용

`src/selfindex/runtime/platform/environment.py:7`, `adapters/browsecomp/agent/_bootstrap.py`

```python
REPO_ROOT = str(Path(__file__).resolve().parents[4])
IMPORT_ROOTS = (os.path.join(REPO_ROOT, "src"), ADAPTERS_ROOT)
```

#### A6. 저장소 문서의 역할 분담

문서마다 맡는 내용을 나누고, 코드의 설정 표와 문서의 표를 맞춰 두는 방법입니다.

##### 사용 방법

| 문서 | 맡는 내용 |
|---|---|
| `README.md` | 설치, 환경 변수, 파라미터, 확장 방법 |
| `docs/REPRODUCING.md` | 보고된 수치를 재현하는 명령 |
| `docs/ARTIFACTS.md` | 산출물 파일의 형식과 필드 |
| `externals/README.md` | upstream 출처와 license |

README의 파라미터 표는 코드의 `PARAMETERS` dict와 같은 내용입니다.

##### 왜 필요한가

사용자가 알아야 하는 사실이 한 문서에 몰리지 않습니다. 코드의 설정 dict를 바꿀 때 함께 고쳐야 할 문서 위치도
정해져 있습니다.

### B. 인터페이스와 객체 설계

인터페이스와 구현을 분리하고, 객체의 역할을 나누며, 기능을 추가하거나 교체하는 방법을 다룹니다.

#### B1. ABC와 Protocol

interface와 구현을 다른 파일에 두고, 상속은 한두 단계에서 끝내는 방법입니다.

##### 개념

- **ABC**는 "이 클래스를 상속하는 클래스는 이 메서드들을 반드시 가져야 한다"는 약속만 정하는 클래스입니다.
  미구현 abstract method가 남아 있으면 객체를 만들 수 없습니다.
- **abstract method**(`@abstractmethod`)는 그 약속에 들어가는 메서드입니다. 하나라도 구현하지 않은 하위 클래스로
  객체를 만들면 `TypeError`가 납니다.
- **Protocol**은 상속 없이 "이 메서드를 가지고 있으면 된다"만 정하는 interface입니다. 함수 하나나 외부
  client처럼 우리가 상속 구조를 강제할 수 없는 대상에 씁니다.

##### 사용 방법

- ABC, Protocol, 구현들이 주고받는 데이터 타입은 `contracts.py` 또는 `base.py` 한 파일에 둡니다.
- 구현은 그 옆 파일에 하나씩 둡니다.
- 상속은 대부분 "interface, 구현" 두 단계에서 끝냅니다.
- 타입 표기에만 필요한 import는 `if TYPE_CHECKING:` 안에 둬서, interface 파일과 구현 파일이 서로 import하는
  순환을 만들지 않습니다.

##### 왜 필요한가

새 구현을 추가하는 사람은 interface 파일 하나만 읽고 그 메서드들을 채우면 됩니다. 상속이 얕으면 어떤 메서드가
어디서 오는지 찾느라 여러 파일을 오가지 않아도 됩니다.

##### 예시

```python
# 예시: contracts.py에 interface를, keyword.py에 구현을 둡니다
from abc import ABC, abstractmethod
from typing import Protocol


# --- contracts.py ---
class Retriever(ABC):
    """검색기가 지켜야 하는 약속입니다."""

    @abstractmethod
    def search(self, query: str, k: int) -> list[str]: ...


class Encoder(Protocol):
    """문장 목록을 받아 vector 목록을 돌려주는 것이면 무엇이든 됩니다."""

    def __call__(self, texts: list[str]) -> list[list[float]]: ...


# --- keyword.py ---
class KeywordRetriever(Retriever):
    def __init__(self, docs: list[str]) -> None:
        self.docs = docs

    def search(self, query: str, k: int) -> list[str]:
        return [doc for doc in self.docs if query in doc][:k]


# ABC 자체로는 객체를 만들 수 없습니다
try:
    Retriever()
except TypeError as error:
    print(error)  # Can't instantiate abstract class Retriever ...

# search를 구현하지 않은 하위 클래스도 객체를 만들 때 실패합니다
class Broken(Retriever):
    pass

try:
    Broken()
except TypeError as error:
    print(error)


# Protocol은 상속하지 않은 일반 함수도 받아 줍니다
def length_encoder(texts: list[str]) -> list[list[float]]:
    return [[float(len(text))] for text in texts]


def encode_all(encode: Encoder, texts: list[str]) -> list[list[float]]:
    return encode(texts)


print(KeywordRetriever(["red apple", "green pear"]).search("apple", 5))  # ['red apple']
print(encode_all(length_encoder, ["ab", "abc"]))  # [[2.0], [3.0]]
```

##### Self-Index에서의 사용

클래스 계층입니다(AST로 추출).

```
ScoringView (index/contracts.py)
├─ LiveIndex, LexicalLiveIndex (retrieval/views.py)
└─ LiveIndexView
   └─ IndexSnapshot (retrieval/snapshots.py)
      └─ DenseSnapshot, LexicalSnapshot
KeyIndex (index/contracts.py) ─ IndexState (index/dense.py), LexicalIndexAdapter (index/lexical.py)
Retriever (retrieval/contracts.py) ─ DenseRetriever, LexicalRetriever
TextEncoder → CorpusEmbeddingBackend → MappedCorpusEmbeddingBackend → QwenEmbBackend (adapter)
Benchmark → RetrievalBenchmark → BrightBenchmark, TableBenchmark, LongMemBenchmark
         └→ BCPlusBenchmark
BenchmarkFactory → RetrievalFactory, BrowseCompFactory, LongMemFactory
RetrieverBackend → DenseBackend, BM25Backend
Backbone → OptimizerBackbone, AgentBackbone(→ KimiK25Agent), JudgeBackbone(→ Gpt52Judge)
SearchAgent (adapter) → GptOss, Nano54, Gem37, Kimi25
ScoreCriterion → SpecificityCriterion, SeparationCriterion
SignalSource → QuerySimulator,  DocSelector → EntrySelector
ArtifactStore → LocalArtifactStore
```

가장 깊은 계층은 `TextEncoder`에서 `QwenEmbBackend`까지 네 단계이고, 중간 단계는 모두 추상 클래스입니다. 구현
클래스를 다시 상속하는 곳은 `FullRunPlan → FullRun`, `Task → LaunchTask` 두 곳뿐입니다. `TYPE_CHECKING` 사용
예는 `pipeline/contracts.py:7`에 있습니다.

이 interface를 구현한 객체를 실행 코드에 전달하는 방식은 **dependency injection**입니다. `OptimizerLoop`는 `signal`과
`selector`를 생성자 인자로 받고(`pipeline/engine.py:21`), 각각 `build(ctx)`와 `order(ctx, sig)`를 호출합니다.
두 동작은 **strategy**로 분리되어 있어 loop의 실행 순서를 유지하면서 구현을 교체할 수 있습니다.
실제 구현의 조합은 `pipeline/presets.py:15`의 `build_slots()`에서 정합니다.

##### 주의할 점

구현이 하나뿐이고 늘어날 계획도 없으면 interface를 따로 만들지 않습니다. 이 레포도 `PipelineEvaluation`,
`NDCGMetric`처럼 구현이 하나인 클래스에는 ABC를 두지 않았습니다.

#### B2. Template method와 hook

하위 클래스가 채우는 `build()`와 바깥에서 부르는 `create()`를 나눠서, 확장 코드의 실수를 경계에서 잡는
방법입니다.

##### 개념

- **template method**는 기본 클래스가 처리 순서를 정하고, 하위 클래스는 그중 일부 단계만 채우는 설계입니다.
- **hook**은 하위 클래스가 원할 때만 override하는, 기본 동작이 비어 있는 메서드입니다.

##### 사용 방법

- 확장하는 사람이 구현할 메서드(`build`)와 바깥에서 부르는 메서드(`create`)를 나눕니다.
- `create`는 `build`를 부른 뒤 돌려받은 값의 타입과 조건을 검사합니다.
- 하위 클래스가 필요할 때만 override하는 hook은 빈 일반 메서드로 둡니다.
- 정리를 맡는 hook은 공개 메서드가 `try/finally`로 불러서, 본 작업이 실패해도 항상 실행되게 합니다.

##### 왜 필요한가

확장 코드가 잘못된 타입을 반환하면 `create()`에서 즉시 오류를 냅니다. 잘못된 값이 다른 단계로 전달되기 전에
어떤 구현이 반환 형식을 위반했는지 확인할 수 있습니다.

##### 예시

```python
# 예시: build는 하위 클래스가, 검사는 기본 클래스의 create가 맡습니다
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    name: str


class Factory(ABC):
    def create(self, name: str) -> Task:
        # 하위 클래스가 만든 결과가 약속한 타입인지 경계에서 확인합니다
        result = self.build(name)
        if not isinstance(result, Task):
            raise TypeError(f"{type(self).__name__}.build() must return Task")
        return result

    @abstractmethod
    def build(self, name: str) -> Task: ...


class GoodFactory(Factory):
    def build(self, name: str) -> Task:
        return Task(name)


class BadFactory(Factory):
    def build(self, name: str) -> Task:
        return name  # 실수로 문자열을 돌려줍니다


print(GoodFactory().create("encode"))  # Task(name='encode')
try:
    BadFactory().create("encode")
except TypeError as error:
    print(error)  # BadFactory.build() must return Task
```

##### Self-Index에서의 사용

`src/selfindex/runtime/factories.py:52`. 같은 형태가 `runtime/catalog/retrievers.py:24`,
`adapters/browsecomp/adapters/search_factory.py:53`에도 있습니다.

```python
@abstractmethod
def build(self, task: str, argv: list) -> Task: ...

def create(self, task, argv):
    self.validate_task(task)
    result = self.build(task, list(argv))
    if not isinstance(result, Task):
        raise TypeError("factory build() must return Task")
    return result
```

선택 hook과 정리 hook은 `adapters/browsecomp/agent/backbones.py:73`, `:98`에 있습니다.

```python
def pre_agent(self, log_dir):  # noqa: B027
    ...

def run_agent(self, queries, out_dir, threads, log_path):
    try:
        self.pre_agent(os.path.dirname(log_path) or ".")
        return self._run_process(queries, out_dir, threads, log_path)
    finally:
        self.post_agent()
```

`B027`은 "ABC 안의 빈 메서드가 abstract가 아니다"라는 flake8-bugbear 경고입니다. 이 레포는 의도한 hook이라는
표시로 그 줄에서만 경고를 끕니다.

#### B3. Registry

구현을 이름으로 등록하고 이름으로 꺼내 쓰는 방법입니다. 등록할 때 이름 중복과 추상 클래스를 거부합니다.

##### 개념

registry는 이름을 키로 구현을 등록해 두고, 실행할 때 이름(예: CLI 인자 `--retriever bm25`)으로 꺼내 쓰는
표입니다. 새 구현을 추가할 때 `if name == "bm25": ... elif ...` 분기를 늘리지 않아도 됩니다.

##### 사용 방법

등록하는 방식은 네 가지가 있습니다.

| 방식 | 언제 쓰나 |
|---|---|
| `Registry` 객체와 `register_*()` 함수 | 객체나 설정을 이름으로 등록하고, 등록할 때 타입, 중복, 이름 형식을 검사해야 할 때 |
| class decorator (`@Base.register("name")`) | 클래스 하나를 여러 키에 묶을 때. 클래스 정의 바로 위에 등록 키가 보입니다 |
| `__init_subclass__` (C9) | 하위 클래스를 정의하기만 하면 등록되어야 할 때 |
| 문자열 명령 표 (A3) | import 비용이 큰 대상을 실행 직전에만 불러와야 할 때 |

어떤 방식이든 다음을 지킵니다.

- 조회에 실패하면 무엇이 없는지와 무엇을 쓸 수 있는지를 함께 알립니다.
- 등록 대상이 구체 클래스인지 `inspect.isabstract()`로 확인합니다.
- 여러 개를 한 번에 등록할 때는 전부 검증한 뒤에 등록합니다.
- argparse의 `choices`를 registry에서 만들어서, 등록하면 CLI 선택지도 함께 늘어나게 합니다.

##### 왜 필요한가

구현을 추가하는 일이 "클래스를 만들고 등록한다"로 끝납니다. 실행 코드의 분기, CLI 선택지, 오류 메시지를
따로 고치지 않아도 됩니다.

##### 예시

검증하는 registry와 class decorator 등록입니다. `Mapping`은 C10에서 설명합니다.

```python
# 예시: 등록할 때 검증하고, 조회에 실패하면 선택지를 알려 주는 registry
import inspect
from collections.abc import Iterator, Mapping


class Registry(Mapping):
    def __init__(self, kind: str) -> None:
        self._kind = kind
        self._items: dict[str, type] = {}

    def register(self, name: str, item: type) -> None:
        # 빈 이름, 중복 이름, 추상 클래스는 등록 시점에 거부합니다
        if not name:
            raise ValueError(f"{self._kind} name must not be empty")
        if name in self._items:
            raise ValueError(f"{self._kind} {name!r} is already registered")
        if inspect.isabstract(item):
            raise TypeError(f"{self._kind} {name!r} must be a concrete class")
        self._items[name] = item

    def __getitem__(self, name: str) -> type:
        # 없는 이름이면 쓸 수 있는 이름을 함께 알립니다
        if name not in self._items:
            raise KeyError(f"unknown {self._kind}: {name}; available: {', '.join(sorted(self._items))}")
        return self._items[name]

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)


RETRIEVERS = Registry("retriever")


def retriever(name: str):
    """클래스 정의 위에 붙여 RETRIEVERS에 등록하는 class decorator입니다."""

    def register(cls: type) -> type:
        RETRIEVERS.register(name, cls)
        return cls

    return register


@retriever("bm25")
class BM25:
    pass


print(sorted(RETRIEVERS))  # ['bm25'] — argparse choices로 그대로 씁니다
try:
    RETRIEVERS["dense"]
except KeyError as error:
    print(error)  # 'unknown retriever: dense; available: bm25'
try:
    RETRIEVERS.register("bm25", BM25)
except ValueError as error:
    print(error)  # retriever 'bm25' is already registered
```

##### Self-Index에서의 사용

| 방식 | 위치 |
|---|---|
| `Registry` 객체와 `register_*()` 함수 | `runtime/registry.py`, `register_benchmark`, `register_retriever`, `register_factory`, `register_search_adapter` |
| class decorator | `@AgentBackbone.register(model)`, `llm/backbones.py:14` |
| `__init_subclass__` | `adapters/browsecomp/agent/backbones.py:45` |
| 문자열 명령 표 | `COMMANDS`, `runtime/commands.py:10` |

- 조회 실패 메시지: `f"unknown retriever backend: {name}; available: {', '.join(BACKENDS)}"`.
- `inspect.isabstract()` 검사: `runtime/factories.py:160`, `runtime/catalog/benchmarks.py:264`.
- 전부 검증한 뒤 등록: `register_domains`, `benchmarks.py:260`.
- registry에서 만든 CLI 선택지: `choices=list(SEARCH_ADAPTERS)`, `choices=sorted(RETRIEVERS)`.

#### B4. Mixin

외부 클래스를 고치지 않고, 함께 상속하는 작은 클래스로 기능을 덧붙이는 방법입니다.

##### 개념

- **mixin**은 혼자서는 쓰지 않고 다른 클래스와 함께 상속해서 기능을 덧붙이는 작은 클래스입니다.
- `class Ours(Mixin, Upstream)`이라고 쓰면 메서드를 Ours, Mixin, Upstream 순서로 찾습니다. 이 순서를
  **MRO**라고 합니다. 그래서 Mixin의 메서드가 먼저 불리고, 그 안의 `super()`는 Upstream의 같은 메서드를
  부릅니다.

##### 사용 방법

- upstream 클래스를 고치지 않고 `class Ours(Mixin, Upstream)` 형태로 합칩니다.
- mixin 메서드는 `super()`를 부르고, 그 앞뒤에 동작을 덧붙입니다.
- upstream이 모르는 설정 키는 `super().__init__`에 넘기기 전에 빼냅니다.
- mixin이 추가하는 속성에는 `_si_keys`처럼 mixin 고유의 접두어를 붙입니다.

##### 왜 필요한가

upstream 코드를 한 줄도 고치지 않으므로 upstream을 새 버전으로 바꾸기 쉽습니다. 접두어 덕분에 upstream이 나중에
같은 이름의 속성을 추가해도 서로 덮어쓰지 않습니다.

##### 예시

```python
# 예시: upstream의 Memory를 고치지 않고 추가 건수를 세는 기능을 덧붙입니다
class Memory:
    """upstream 클래스라고 가정합니다. 이 코드는 고치지 않습니다."""

    def __init__(self, params: dict) -> None:
        self.size = params["size"]
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)


class CountingMixin:
    def __init__(self, params: dict) -> None:
        # upstream이 모르는 설정 키는 넘기기 전에 빼냅니다
        params = dict(params)
        self._counting_label = params.pop("label", "memory")
        super().__init__(params)
        self._counting_added = 0

    def add(self, item: str) -> None:
        # upstream 동작을 먼저 하고, 그 뒤에 건수를 셉니다
        super().add(item)
        self._counting_added += 1


class CountingMemory(CountingMixin, Memory):
    pass


memory = CountingMemory({"size": 3, "label": "notes"})
memory.add("first")
print(memory.items, memory._counting_added)  # ['first'] 1
print([cls.__name__ for cls in CountingMemory.__mro__])
# ['CountingMemory', 'CountingMixin', 'Memory', 'object']
```

##### Self-Index에서의 사용

`adapters/longmem/adapter/memory_ours.py:17`, `:104`

```python
class SelfIndexMixin:

    def __init__(self, memory_params):
        params = dict(memory_params)
        keys_path = params.pop("selfindex_keys_path", None)
        super().__init__(params)
        self._selfindex_init(keys_path)
    ...

@register_memory
class RagSelfIndex(SelfIndexMixin, RagMemory):
    memory_type = "rag_selfindex"
```

##### 주의할 점

upstream이 내부 메서드 이름을 바꾸면 mixin의 override가 더 이상 불리지 않는데, 오류도 나지 않습니다. 이 레포는
다른 adapter에서 upstream의 전제를 실행 전에 검사하는 방식으로 이 위험을 다룹니다(D7).

#### B5. Proxy

객체를 감싸서 일부 메서드만 바꾸고, 나머지는 원래 객체에 넘기는 방법입니다.

##### 개념

- **proxy**는 원래 객체를 속성으로 보관하고, 일부 메서드만 직접 정의하고 나머지는 원래 객체에 넘기는 객체입니다.
- **`__getattr__`**은 객체에 없는 속성을 읽으려 할 때만 불립니다. 그래서 직접 정의하지 않은 속성은 모두
  `__getattr__`을 거쳐 원래 객체로 갑니다.

##### 사용 방법

- 바꿀 메서드 한두 개만 직접 정의합니다.
- 나머지 속성 접근은 `__getattr__`으로 원래 객체에 넘깁니다.
- 이미 감싼 객체는 다시 감싸지 않습니다.

##### 왜 필요한가

원래 객체가 가진 수십 개의 메서드를 하나하나 옮겨 적지 않아도 됩니다.

##### 예시

```python
# 예시: write만 바꾸고 나머지는 원래 stream에 넘기는 proxy
import io


class PrefixWriter:
    def __init__(self, raw: io.TextIOBase) -> None:
        self._raw = raw

    def write(self, text: str) -> int:
        # 내용이 있는 줄에만 prefix를 붙입니다
        return self._raw.write(f"[app] {text}" if text.strip() else text)

    def __getattr__(self, name: str):
        # 직접 정의하지 않은 속성은 모두 원래 stream에서 찾습니다
        return getattr(self._raw, name)


buffer = io.StringIO()
writer = PrefixWriter(buffer)
writer.write("started\n")
print(writer.getvalue())  # [app] started  — getvalue는 __getattr__을 거쳐 StringIO에서 옵니다
```

##### Self-Index에서의 사용

`src/selfindex/pipeline/run.py:31`의 `_TsWriter`는 `write`, `flush`만 정의하고 나머지는 원래 stdout에 넘깁니다.

```python
def __getattr__(self, name):
    return getattr(self._raw, name)

def _install_ts_stdout():
    if not isinstance(sys.stdout, _TsWriter):
        sys.stdout = _TsWriter(sys.stdout)
```

upstream이 `client.chat.completions.create(...)`처럼 긴 경로로 부르는 경우에는, `chat`과 `completions`를
`self`를 돌려주는 property로 만들어 같은 경로를 흉내 냅니다(`adapters/browsecomp/agent/or_client_ours.py:19`의
`_Routed`).

##### 주의할 점

proxy는 원래 객체와 타입이 다르므로 `isinstance` 검사까지 통과해야 하는 상황에는 맞지 않습니다. 그럴 때는
상속(B4)을 씁니다.

#### B6. Callable

실행할 동작을 함수, lambda, 호출 가능한 객체로 전달받는 방법입니다.

##### 개념

- **Callable**은 괄호를 붙여 부를 수 있는 모든 것을 뜻하는 타입입니다.
- **`__call__`**을 정의한 객체는 함수처럼 `obj()`로 부를 수 있습니다.

##### 사용 방법

- 실행 단위를 `Callable[[], int | None]`로 받습니다. lambda, 일반 함수, `__call__`을 가진 객체를 모두
  인자로 전달할 수 있습니다.
- 실행에 필요한 값(명령, 인자, 환경)을 들고 있어야 하면 `__call__`을 가진 frozen dataclass로 만듭니다.

##### 왜 필요한가

단계를 실행하는 쪽은 "부르면 exit code가 나온다"만 알면 됩니다. 단계가 함수인지 하위 프로세스인지 몰라도
됩니다.

##### 예시

```python
# 예시: lambda와 __call__ 객체를 같은 Stage에 넣습니다
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Stage:
    name: str
    action: Callable[[], int]


@dataclass(frozen=True)
class Command:
    """하위 프로세스 하나를 들고 있다가, 부르면 실행하고 exit code를 돌려줍니다."""

    arguments: tuple[str, ...]

    def __call__(self) -> int:
        return subprocess.run(self.arguments, check=False).returncode


stages = [
    Stage("inline", lambda: 0),
    Stage("process", Command((sys.executable, "-c", "pass"))),
]
for stage in stages:
    print(stage.name, stage.action())  # inline 0, process 0
```

##### Self-Index에서의 사용

`src/selfindex/runtime/workflows/execution.py:13`

```python
@dataclass(frozen=True)
class Stage:
    name: str
    action: Callable[[], int | None]
    artifacts: Callable[[], tuple[Path, ...]] | None = None

@dataclass(frozen=True)
class Command:
    name: str
    arguments: tuple[str, ...]
    environment: Mapping[str, str]
    directory: Path

    def __call__(self) -> int:
        ...
```

같은 방식으로 `EncodedTexts`(`validation/base.py:15`)는 미리 encode한 결과를 들고 있다가 함수처럼 조회되고,
`TextEncoding` Protocol(`pipeline/contracts.py:15`)은 `__call__` 시그니처만으로 encoder의 약속을 정합니다.

#### B7. Context와 상태 객체

단계 사이에 넘기는 값 묶음에서 입력과, 실행 중 바뀌는 상태를 나눠 담는 방법입니다.

##### 개념

context는 여러 단계가 함께 쓰는 값을 묶어 단계에서 단계로 넘기는 객체입니다.

##### 사용 방법

- `Context`에는 입력 데이터(texts), 함께 사용하는 객체(llm, index, retriever), 단계별 상태 객체를 구분해 담습니다.
  같은 객체를 계속 참조해도 index의 내부 데이터는 실행 중 바뀔 수 있습니다.
- 상태 객체는 `RoundState`, `QueryState`, `SelectionState`처럼 관심사별로 작게 나눕니다.
- 큰 상태는 `repr=False`로 두어 디버그 출력이 길어지지 않게 합니다.

##### 왜 필요한가

상태를 역할별 객체로 나누면 각 단계가 변경하는 값을 확인하기 쉽습니다. 입력 데이터, 공용 객체, 단계별 상태를
구분하면 변경이 영향을 주는 범위도 파악하기 쉽습니다.

##### 예시

```python
# 예시: 입력과 바뀌는 상태를 나눠 담은 context
from dataclasses import dataclass, field


@dataclass
class RoundState:
    round: int = 0
    added: int = 0


@dataclass
class Context:
    texts: list[str]
    round_state: RoundState = field(default_factory=RoundState)
    cache: dict[str, int] = field(default_factory=dict, repr=False)


context = Context(["a", "b"])
context.round_state.round += 1
print(context)  # Context(texts=['a', 'b'], round_state=RoundState(round=1, added=0))
```

##### Self-Index에서의 사용

`src/selfindex/pipeline/contracts.py:55`

```python
@dataclass
class Context:
    texts: list
    encode: TextEncoding
    llm: GenerationClient
    ...
    round_state: RoundState = field(default_factory=RoundState)
    query_state: QueryState = field(default_factory=QueryState, repr=False)
    selection_state: SelectionState = field(default_factory=SelectionState, repr=False)
```

##### 주의할 점

이 레포에서도 `_units()`가 `ctx.selection_state.units`에 계산 결과를 저장하는 것처럼, 상태 객체가 캐시 역할까지
맡는 곳이 있습니다. 어떤 함수가 어떤 상태를 바꾸는지는 이름이나 docstring으로 드러내야 합니다.

### C. decorator와 언어 기능

decorator와 Python 언어 기능의 용도와 선택 기준을 다룹니다. 레포 전체의 decorator 사용 횟수는
다음과 같습니다(AST 집계).

| decorator | 횟수 | 이 레포에서의 용도 |
|---|---|---|
| `@abstractmethod` | 36 | interface의 필수 메서드 |
| `@property` | 28 | 파생 값, 지연 로드, 추상 속성, 상태를 확인한 뒤 돌려주는 값 |
| `@dataclass(frozen=True)` | 20 | spec, plan, settings, 판정 결과 같은 바뀌지 않는 값 |
| `@dataclass` | 13 | 실행 중 바뀌는 상태와 집계 |
| `@classmethod` | 10 | 이름 있는 생성자, 객체 없이 하는 검사, 등록 decorator |
| `@staticmethod` | 6 | 모두 `_`로 시작하는 private helper |
| `@contextmanager` | 4 | 되돌리기가 보장되어야 하는 일시적 변경과 lock |
| `@register_memory` 외 등록 decorator | 4 | 클래스를 registry에 등록 |
| `@cache` | 1 | 외부 서비스 조회 결과 캐시 |

#### C1. Dataclass

바뀌지 않는 값은 frozen dataclass로, 바뀌는 상태는 일반 dataclass로 만드는 방법입니다.

##### 개념

- **dataclass**(`@dataclass`)는 필드 선언만으로 `__init__`, `__repr__`, `__eq__`를 만들어 줍니다.
- **frozen dataclass**(`@dataclass(frozen=True)`)는 만든 뒤 필드에 대입할 수 없습니다.
- **`__post_init__`**은 자동 `__init__`이 끝난 직후 불리므로, 검사와 정규화를 여기서 합니다.

##### 사용 방법

- 실행 중 바뀌지 않는 값(`Spec`, `Plan`, `Settings`)은 frozen, 바뀌는 상태와 집계(`State`, `Report`)만 일반
  dataclass로 둡니다.
- frozen 객체를 `__post_init__`에서 정규화할 때는 `object.__setattr__`을 씁니다. 일반 대입은 frozen 때문에
  막혀 있기 때문입니다.
- frozen은 필드를 다른 객체로 바꾸는 것만 막고, dict 안의 내용을 바꾸는 것은 막지 않습니다. 그래서 받은 dict는
  복사해서 `MappingProxyType`으로 감쌉니다.
- 타입 표기가 없는 class 변수는 dataclass field가 되지 않고 class attribute로 남습니다. 상수로 쓸 수 있지만,
  값의 변경 자체를 막지는 않습니다.
- list나 dict 같은 기본값은 반드시 `field(default_factory=...)`로 줍니다.

##### 왜 필요한가

설정이나 plan의 필드를 실행 도중 실수로 변경하는 일을 막습니다. 필드에 다시 대입하면 즉시 오류가 납니다.

##### 예시

```python
# 예시: 생성할 때 검사하고 정규화하며, 받은 dict까지 읽기 전용으로 만듭니다
from dataclasses import FrozenInstanceError, dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class Endpoint:
    base_url: str
    headers: Mapping[str, str] = field(default_factory=dict)
    timeout_env = "HTTP_TIMEOUT_SECONDS"  # 타입 표기가 없으므로 field가 아닌 공유 상수입니다

    def __post_init__(self) -> None:
        # 잘못된 URL은 만드는 순간 거부합니다
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError("endpoint must be an absolute HTTP(S) URL")

        # frozen이라 일반 대입이 막혀 있으므로 object.__setattr__으로 정규화합니다
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))
        object.__setattr__(self, "headers", MappingProxyType(dict(self.headers)))


endpoint = Endpoint("http://localhost:8000/", {"x-team": "ir"})
print(endpoint.base_url)  # http://localhost:8000

try:
    endpoint.base_url = "http://other"
except FrozenInstanceError:
    print("필드는 다시 대입할 수 없습니다")

try:
    endpoint.headers["x-team"] = "nlp"
except TypeError:
    print("dict 내용도 바꿀 수 없습니다")
```

##### Self-Index에서의 사용

`src/selfindex/runtime/platform/endpoints.py:47`

```python
def __post_init__(self):
    if not isinstance(self.base_url, str) or not isinstance(self.model_name, str):
        raise ValueError("endpoint URL and model must be strings")
    _validate_url(self.base_url)
    object.__setattr__(self, "base_url", self.base_url.rstrip("/"))
```

- dict를 `MappingProxyType(dict(...))`로 감싸는 곳: `adapters/browsecomp/pipeline/workflow.py:25`.
- frozen dataclass로 추상 property를 채우는 곳: `BrowseCompWorkflow`는 `resumed` 필드를 두고 `resume` property가
  그 값을 돌려줍니다. 필드 이름과 property 이름이 같으면 충돌하기 때문입니다(`workflow.py:20`, `:35`).
- 공유 상수: `Endpoint.api_key_env = API_KEY_ENV`(`endpoints.py:45`).
- 기본값을 함수로 계산: `usage: dict = field(default_factory=_empty_usage)`(`or_client_ours.py:73`).

##### 주의할 점

이 레포는 `slots=True`, `kw_only=True`를 쓰지 않습니다. 필드가 많은 spec에 `kw_only=True`를 쓰면 위치 인자 순서
실수를 막을 수 있지만, 레포에서 확인된 관행은 아닙니다.

#### C2. NamedTuple

풀어서 받는 작은 반환값과 JSON으로 내보낼 작은 레코드를 만드는 방법입니다.

##### 개념

NamedTuple은 필드 이름이 붙은 tuple입니다. 위치로 풀어서 받을 수도 있고 이름으로 읽을 수도 있습니다.
`_asdict()`로 dict가 됩니다.

##### 사용 방법

호출하는 쪽이 `ids, scores = ...`처럼 풀어서 받는 반환값은 NamedTuple로 만듭니다.

##### 왜 필요한가

일반 tuple을 돌려주면 `result[0]`이 무엇인지 알 수 없지만, NamedTuple은 `result.ids`로 읽을 수 있습니다. 풀어서
받는 기존 코드도 그대로 동작합니다.

##### 예시

```python
# 예시: 이름으로도, 위치로도 읽을 수 있는 반환값
import json
from typing import NamedTuple


class SearchResult(NamedTuple):
    ids: list[int]
    scores: list[float]


def search() -> SearchResult:
    return SearchResult([3, 1], [0.9, 0.4])


ids, scores = search()
print(search().scores)  # [0.9, 0.4]
print(json.dumps(search()._asdict()))  # {"ids": [3, 1], "scores": [0.9, 0.4]}
```

##### Self-Index에서의 사용

`KeySearchResult(key_ids, scores)`(`retrieval/snapshots.py:16`), `StepSpec`(`runtime/plan.py:5`),
`ExecutionPlan.to_dict()`의 `s._asdict()`(`plan.py:18`).

##### 주의할 점

생성할 때 검사가 필요하거나 필드가 늘어날 값은 frozen dataclass로 만듭니다. NamedTuple에는 `__post_init__`이
없습니다.

#### C3. Property

메서드를 속성처럼 읽게 하는 property를 쓰는 네 가지 경우입니다.

##### 개념

property(`@property`)를 붙인 메서드는 괄호 없이 속성처럼 읽힙니다. `obj.size()` 대신 `obj.size`로 씁니다.

##### 사용 방법

1. **파생 값**: 다른 필드에서 계산되는 값은 저장하지 않고 읽을 때 계산합니다.
2. **지연 로드**: 처음 읽을 때 무거운 데이터를 불러옵니다.
3. **추상 속성**: 하위 클래스가 반드시 제공해야 하는 "값"은 `@property`를 바깥, `@abstractmethod`를 안쪽에
   쌓습니다. 순서를 바꾸면 추상 속성으로 인식되지 않습니다.
4. **상태를 확인한 뒤 돌려주는 값**: `with` 블록 안에서만 유효한 객체는 property에서 상태를 확인하고, 블록
   밖이면 값 대신 오류를 냅니다.

##### 왜 필요한가

파생 값을 저장하면 원래 필드가 바뀔 때 둘이 어긋날 수 있습니다. property는 늘 원래 필드에서 계산하므로 어긋나지
않습니다.

##### 예시

```python
# 예시: property의 네 가지 쓰임
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Judgement:
    causes: tuple[str, ...]

    # 1. 파생 값
    @property
    def failed(self) -> bool:
        return bool(self.causes)


class Index(ABC):
    # 3. 추상 속성: property가 바깥, abstractmethod가 안쪽입니다
    @property
    @abstractmethod
    def size(self) -> int: ...


class FileIndex(Index):
    def __init__(self, rows: list[str]) -> None:
        self._source = rows
        self._loaded: list[str] | None = None

    # 2. 지연 로드: 처음 읽을 때만 불러옵니다
    @property
    def rows(self) -> list[str]:
        if self._loaded is None:
            self._loaded = list(self._source)
        return self._loaded

    @property
    def size(self) -> int:
        return len(self.rows)


class Snapshot:
    def __init__(self, values: list[int]) -> None:
        self._values = values
        self._open = False

    def __enter__(self) -> "Snapshot":
        self._open = True
        return self

    def __exit__(self, *exc_info: object) -> None:
        self._open = False

    # 4. 상태 확인: with 블록 밖에서는 값을 주지 않습니다
    @property
    def values(self) -> list[int]:
        if not self._open:
            raise RuntimeError("snapshot is closed; use it inside a with block")
        return self._values


print(Judgement(("too short",)).failed, FileIndex(["a", "b"]).size)  # True 2
with Snapshot([1, 2]) as snapshot:
    print(snapshot.values)  # [1, 2]
try:
    snapshot.values
except RuntimeError as error:
    print(error)
```

##### Self-Index에서의 사용

| 쓰임 | 위치 |
|---|---|
| 파생 값 | `shortfall`(`pipeline/optimizer.py:134`), `ProposedKey.is_new`, `RevisionDecision.replacement`, `NDCGMetric.label` |
| 지연 로드 | `QwenEmbBackend.lookup`(`adapters/browsecomp/adapters/embedding.py:61`), `Endpoint.model`(`endpoints.py:53`. 모델 이름이 비어 있을 때만 서버에 물어봅니다) |
| 추상 속성 | `index/contracts.py:72`, `encoding/contracts.py:20`, `runtime/workflows/execution.py:105` |
| 상태 확인 | snapshot의 모든 속성이 `self._active()`를 거칩니다(`retrieval/snapshots.py:81`) |

##### 주의할 점

property는 속성 읽기처럼 보이기 때문에, 네트워크 호출처럼 느리거나 실패할 수 있는 동작을 숨기면 호출하는 쪽이
비용을 예상하지 못합니다. `Endpoint.model`이 이 경계에 있습니다. cache(C8)로 조회 결과를 재사용하지만, 처음
읽을 때는 네트워크 요청이 발생합니다.

#### C4. Classmethod

클래스를 첫 인자로 받는 classmethod를 쓰는 세 가지 경우입니다.

##### 개념

classmethod(`@classmethod`)는 객체 대신 클래스를 첫 인자 `cls`로 받습니다. 객체를 만들지 않고
`ClassName.method()`로 부를 수 있고, 하위 클래스에서 부르면 `cls`가 그 하위 클래스가 됩니다.

##### 사용 방법

1. **이름 있는 생성자**: 객체를 만드는 경로마다 이름을 붙입니다. `from_env()`, `of(name)`, `load(directory)`.
2. **객체 없이 하는 검사**: class attribute만 보고 입력을 검사합니다. 무거운 객체를 만들기 전에 잘못된 입력을
   거부할 수 있습니다.
3. **역할별 등록 decorator**: 기본 클래스에 `register`를 classmethod로 두고, 하위 클래스마다 자기 표를 따로
   둡니다. 그러면 `@A.register(...)`와 `@B.register(...)`가 서로 다른 표에 등록합니다.

##### 예시

```python
# 예시: 이름 있는 생성자, 객체 없이 하는 검사, 역할별 등록
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    rounds: int

    # 1. 환경 변수에서 만드는 생성자
    @classmethod
    def from_env(cls) -> "Settings":
        return cls(int(os.environ.get("ROUNDS", "3")))


class Factory:
    tasks = ("encode", "search")

    # 2. 객체를 만들지 않고 class attribute만 보고 검사합니다
    @classmethod
    def validate_task(cls, task: str) -> None:
        if task not in cls.tasks:
            raise ValueError(f"{cls.__name__} supports {cls.tasks}, not {task!r}")


class Backbone:
    def __init__(self, model: str) -> None:
        self.model = model

    # 3. 하위 클래스마다 자기 backbones 표에 등록합니다
    @classmethod
    def register(cls, *models: str):
        def register(backbone: type) -> type:
            cls.backbones.update(dict.fromkeys(models, backbone))
            return backbone

        return register

    @classmethod
    def for_model(cls, model: str) -> "Backbone":
        # 등록되지 않은 모델이면 그 역할의 기본 클래스를 씁니다
        return cls.backbones.get(model, cls)(model)


class AgentBackbone(Backbone):
    backbones: dict[str, type] = {}


class JudgeBackbone(Backbone):
    backbones: dict[str, type] = {}


@AgentBackbone.register("kimi-k2.5")
class KimiAgent(AgentBackbone):
    pass


print(Settings.from_env())
Factory.validate_task("encode")
print(type(AgentBackbone.for_model("kimi-k2.5")).__name__)  # KimiAgent
print(type(JudgeBackbone.for_model("kimi-k2.5")).__name__)  # JudgeBackbone — 다른 표입니다
```

##### Self-Index에서의 사용

- 이름 있는 생성자: `of()`(`runtime/platform/settings.py:24`). 덮어쓸 수 있는 필드를 `CORPUS_SETTINGS`로 제한하고
  `dataclasses.replace`로 새 객체를 만듭니다.
- 객체 없이 하는 검사: `Runner`의 `FACTORIES[family].validate_task(task)`(`runtime/runner.py:34`).
- 역할별 등록: `Backbone.register`와 `for_model`(`llm/backbones.py:14`).

```python
@classmethod
def of(cls, name, **corpus_settings):
    if name not in ENCODERS:
        raise ValueError(f"unknown encoder {name} (choose from {list(ENCODERS)})")
    if unknown := sorted(set(corpus_settings) - set(CORPUS_SETTINGS)):
        raise ValueError(f"a corpus cannot set the encoder's {unknown}")
    ...
    return replace(table, **corpus_settings)
```

##### 주의할 점

이 레포의 기본 클래스 `Backbone`에는 `backbones`가 없으므로 `Backbone.register(...)`를 부르면 `AttributeError`가
납니다. 이 방식을 쓸 때는 기본 클래스에서 부르는 경우를 막거나, 이유를 밝히는 오류를 직접 냅니다.

#### C5. Staticmethod

`self`도 `cls`도 받지 않는 staticmethod를 private helper에만 쓰는 방법입니다.

##### 개념

staticmethod(`@staticmethod`)는 `self`도 `cls`도 받지 않는 메서드입니다. 클래스 안에 둔 일반 함수와 같습니다.

##### 사용 방법

그 클래스 안에서만 쓰는 helper에만 쓰고, 이름은 `_`로 시작합니다. 다른 곳에서도 쓸 순수 함수는 클래스 밖의 모듈
함수로 둡니다.

##### 왜 필요한가

`self`를 쓰지 않는다는 사실이 시그니처에 드러나고, 그 클래스 안에서만 쓰는 helper라는 위치도 유지됩니다.

##### Self-Index에서의 사용

레포의 `@staticmethod` 6개는 모두 `_`로 시작합니다: `_checked_block`, `_units`, `_query_file`,
`_write_query_records`, `_best_per_document`, `_search_adapter`.

#### C6. Abstract method

모든 구현이 가져야 하는 기능은 abstract method로, 일부 구현만 지원하는 기능은 이유를 밝히는 오류로 두는
방법입니다.

##### 개념

- **abstract method**(`@abstractmethod`)는 하위 클래스가 반드시 구현해야 합니다. 구현하지 않으면 객체를 만들 때
  실패합니다.
- 일반 메서드에서 `raise NotImplementedError`를 하면, 하위 클래스가 구현하지 않아도 객체는 만들어지고 그 메서드를
  부를 때만 실패합니다.

##### 사용 방법

- 모든 구현이 가져야 하는 동작만 abstract method로 두고, 본문은 `...` 한 줄로 씁니다.
- 일부 구현만 지원하는 동작은 기본 구현에서 클래스 이름을 넣어 `NotImplementedError`로 실패시킵니다.
- 여러 건을 한 번에 처리하는 메서드는 한 건짜리 메서드를 반복하는 기본 구현을 두고, 더 빠르게 할 수 있는
  구현만 override합니다.

##### 왜 필요한가

모든 기능을 abstract method로 두면 그 기능이 필요 없는 구현도 빈 메서드를 억지로 채워야 합니다. 이유를 밝히는
`NotImplementedError`는 "이 구현은 이 기능을 지원하지 않는다"를 부르는 순간 정확히 알려 줍니다.

##### 예시

```python
# 예시: 필수 기능, 선택 기능, 일괄 처리 기본 구현
from abc import ABC, abstractmethod


class KeyIndex(ABC):
    # 모든 index가 반드시 가져야 하는 기능입니다
    @abstractmethod
    def add(self, doc: int, key: str) -> None: ...

    # 일부 index만 지원하는 기능입니다
    def replace(self, doc: int, key: str) -> None:
        raise NotImplementedError(f"{type(self).__name__} does not support key replacement")

    # 일괄 버전은 한 건짜리를 반복하는 기본 구현을 둡니다
    def replace_many(self, replacements: dict[int, str]) -> None:
        for doc, key in replacements.items():
            self.replace(doc, key)


class AppendOnlyIndex(KeyIndex):
    def __init__(self) -> None:
        self.keys: list[tuple[int, str]] = []

    def add(self, doc: int, key: str) -> None:
        self.keys.append((doc, key))


index = AppendOnlyIndex()
index.add(1, "apple")
try:
    index.replace_many({1: "pear"})
except NotImplementedError as error:
    print(error)  # AppendOnlyIndex does not support key replacement
```

##### Self-Index에서의 사용

`index/contracts.py:98`

```python
def replace_validated(self, doc, texts):
    raise NotImplementedError(
        f"{type(self).__name__} does not support exact validated-key replacement"
    )

def replace_validated_many(self, replacements):
    for doc, keys in replacements.items():
        self.replace_validated(doc, keys)
```

##### 주의할 점

abstract method는 하위 클래스로 객체를 만들 때에야 검사됩니다. 클래스를 registry에 넣는 곳에서는
`inspect.isabstract()`로 미리 거부합니다(B3).

#### C7. Context manager

한 함수 안에서 상태를 바꾸고 복원할 때는 `@contextmanager`, 객체의 자원 사용과 정리를 관리할 때는
`__enter__`/`__exit__`를 쓰는 방법입니다.

##### 개념

- **context manager**는 `with` 블록에 들어갈 때 준비하고, 나올 때 정리하는 객체입니다. 블록 안에서 예외가 나도
  정리는 실행됩니다.
- **contextmanager**(`@contextlib.contextmanager`)는 `yield`가 하나 있는 함수로 context manager를 만들게 해
  줍니다.
- **ExitStack**은 정리할 일을 여러 개 등록해 두었다가 역순으로 실행해 주는 표준 도구입니다.

##### 사용 방법

- "바꾸고, 블록을 실행하고, 되돌린다"가 한 함수로 끝나면 `@contextmanager`를 씁니다. 되돌리는 코드는 `yield`
  뒤의 `finally`에 둡니다.
- 객체가 자원을 사용하는 동안 여러 메서드에서 그 자원에 접근해야 하면 `__enter__`/`__exit__`를
  구현합니다.
- `__enter__`가 중간에 실패하면 그때까지 잡은 자원을 역순으로 풀고 예외를 다시 올립니다.

##### 왜 필요한가

정리 코드가 `finally`나 `__exit__`에 있으면 예외가 나도, 중간에 `return`해도 정리를 빠뜨리지 않습니다.

##### 예시

외부 객체의 속성을 잠시 바꿨다가 되돌리는 context manager입니다. 원래 없던 속성은 sentinel로 구분해서 되돌릴 때
삭제합니다.

```python
# 예시: 여러 속성을 잠시 바꾸고, 블록이 끝나면 모두 되돌립니다
from contextlib import ExitStack, contextmanager
from types import SimpleNamespace
from collections.abc import Iterator

_MISSING = object()


@contextmanager
def patched(target: object, **values: object) -> Iterator[None]:
    with ExitStack() as stack:
        for name, value in values.items():
            # 원래 값을 기억하고, 되돌리는 일을 먼저 등록한 뒤에 바꿉니다
            original = getattr(target, name, _MISSING)
            stack.callback(_restore, target, name, original)
            setattr(target, name, value)
        yield


def _restore(target: object, name: str, original: object) -> None:
    # 원래 없던 속성은 삭제해서 되돌립니다
    if original is _MISSING:
        delattr(target, name)
    else:
        setattr(target, name, original)


config = SimpleNamespace(timeout=10)
try:
    with patched(config, timeout=1, retries=0):
        print(config.timeout, config.retries)  # 1 0
        raise RuntimeError("블록 안에서 실패해도")
except RuntimeError:
    pass
print(vars(config))  # {'timeout': 10} — 되돌아갔고, retries는 지워졌습니다
```

##### Self-Index에서의 사용

| 이름 | 위치 | 하는 일 |
|---|---|---|
| `patched_attributes` | `adapters/browsecomp/adapters/compatibility.py:7` | 위 예시와 같은 구조로 속성을 바꾸고 되돌립니다 |
| `_publication_lock` | `adapters/browsecomp/pipeline/build_bm25_index.py:49` | 기다리지 않는 파일 lock을 잡고, 이미 잡혀 있으면 `FileExistsError`로 바꿔 올립니다(D4) |
| `SnapshotLock.readonly`, `mutation` | `index/contracts.py:21` | thread별 읽기 lease 수를 세고, 다 읽으면 기다리던 쓰기를 깨웁니다 |
| `IndexSnapshot.__enter__` | `retrieval/snapshots.py:38` | lease를 잡고 view를 만들고, 실패하면 잡은 것을 역순으로 풀고 다시 올립니다 |

여기서 **read lease**는 snapshot을 사용하는 동안 index 변경을 제한하는 장치입니다.
`SnapshotLock.mutation()`은 다른 thread의 read lease가 끝날 때까지 기다리고, read lease를 가진 thread가
직접 변경을 시도하면 오류를 냅니다(`index/contracts.py:36`). 이 snapshot은 index 전체를 복사하는 방식이 아니라,
조회하는 동안 변경을 막아 일관된 상태를 유지합니다. `OptimizerLoop`는 snapshot에서 수정안을 계산한 뒤,
lease를 해제하고 index에 반영합니다(`pipeline/engine.py:77`, `:94`).

```python
@contextmanager
def readonly(self):
    thread = threading.get_ident()
    with self:
        self._leases[thread] = self._leases.get(thread, 0) + 1
    try:
        yield
    finally:
        with self:
            self._leases[thread] -= 1
            if not self._leases[thread]:
                del self._leases[thread]
            self._released.notify_all()
```

#### C8. Cache

성공한 외부 조회만 기억하게 해서 같은 조회를 한 번만 하는 방법입니다.

##### 개념

cache(`@functools.cache`)를 붙이면 같은 인자로 다시 부를 때 함수를 실행하지 않고 저장해 둔 결과를 돌려줍니다.

##### 사용 방법

- 예외는 저장되지 않습니다. 조회가 실패하면 다음 호출에서 다시 시도되고, 성공한 결과만 재사용됩니다.
- 캐시 키는 인자 값 그대로입니다. `"http://a/"`와 `"http://a"`는 다른 키이므로, 인자를 먼저 정규화합니다.

##### 왜 필요한가

서버에 "어떤 모델을 서빙하는가"를 묻는 조회를 실행마다 한 번만 하게 하면서, 일시적인 실패가 영원히 남지 않게
합니다.

##### 예시

```python
# 예시: 실패는 저장되지 않으므로 다음 호출에서 다시 시도됩니다
from functools import cache

calls = []


@cache
def served_model(base_url: str) -> str:
    calls.append(base_url)
    if len(calls) == 1:
        raise ConnectionError("server is starting")
    return "qwen3"


try:
    served_model("http://localhost:8000")
except ConnectionError:
    pass
print(served_model("http://localhost:8000"))  # qwen3 — 두 번째 호출에서 다시 시도했습니다
print(served_model("http://localhost:8000"))  # qwen3 — 이번에는 저장된 값입니다
print(len(calls))  # 2
```

##### Self-Index에서의 사용

`src/selfindex/runtime/platform/endpoints.py:17`. URL 끝의 `/`는 `Endpoint.__post_init__`에서 미리 지웁니다(C1).

```python
@cache
def served_model_entry(base_url):
    ...
    except (OSError, ValueError) as error:
        raise ValueError(f"cannot list the models served at {base_url}: {error}")
```

##### 주의할 점

프로세스가 도는 동안 값이 바뀔 수 있는 대상(서버 재시작으로 모델이 바뀌는 경우 등)에는 기한 없는 캐시가 맞지
않습니다.

#### C9. `__init_subclass__`

하위 클래스를 정의하는 순간 자동으로 등록하는 방법입니다.

##### 개념

기본 클래스에 `__init_subclass__`를 정의하면, 그 클래스를 상속한 하위 클래스가 정의될 때마다 자동으로 불립니다.

##### 사용 방법

- `super().__init_subclass__(**kwargs)`를 먼저 부릅니다.
- 등록 조건(예: `name`이 있음)을 둬서 이름 없는 중간 클래스는 등록되지 않게 합니다.
- 이름이 겹치면 정의하는 순간 거부합니다.

##### 예시

레포 코드에 없는 이름 중복 검사를 더한 형태입니다.

```python
# 예시: 정의만 하면 등록되고, 이름이 겹치면 정의하는 순간 실패합니다
_AGENTS: dict[str, type] = {}


class Agent:
    name = ""

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        # 이름이 없는 중간 클래스는 등록하지 않습니다
        if not cls.name:
            return
        if cls.name in _AGENTS:
            raise ValueError(f"agent {cls.name!r} is already defined by {_AGENTS[cls.name].__name__}")
        _AGENTS[cls.name] = cls


class GptAgent(Agent):
    name = "gpt"


try:
    class AnotherGpt(Agent):
        name = "gpt"
except ValueError as error:
    print(error)  # agent 'gpt' is already defined by GptAgent
print(sorted(_AGENTS))  # ['gpt']
```

##### Self-Index에서의 사용

`adapters/browsecomp/agent/backbones.py:45`

```python
def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    if cls.name:
        _REGISTRY[cls.name] = cls
```

##### 주의할 점

레포 코드는 이름 중복을 검사하지 않아서, 같은 `name`을 쓴 두 번째 클래스가 첫 번째를 조용히 덮어씁니다. 위
예시처럼 중복을 거부하거나 `Registry.register`(B3)를 거치게 합니다.

#### C10. Mapping

읽기 전용 표를 `collections.abc.Mapping`의 세 메서드만으로 만드는 방법입니다.

##### 개념

Mapping은 dict처럼 읽을 수 있는 객체의 추상 클래스입니다. `__getitem__`, `__iter__`, `__len__` 세 개만 구현하면
나머지 읽기 기능을 물려받습니다.

##### 사용 방법

- 세 메서드만 구현하면 `in`, `.items()`, `.get()`, `sorted()`가 모두 동작합니다.
- `__setitem__`이 없어서 바깥에서 항목을 덮어쓸 수 없습니다.
- 항목은 검증을 수행하는 `register()`로만 추가합니다.

예시는 B3에 있습니다.

##### Self-Index에서의 사용

`src/selfindex/runtime/registry.py:9`의 `class Registry(Mapping[str, T], Generic[T])`. 레포에서 타입 표기가 가장
충실한 파일이기도 합니다.

#### C11. BaseException

외부 코드의 `except Exception`에 잡히면 안 되는 신호를 만드는 방법입니다.

##### 개념

Python 예외의 뿌리는 `BaseException`이고, 일반 오류는 그 아래의 `Exception`을 상속합니다. `except Exception`은
`Exception` 계열만 잡으므로, `BaseException`을 직접 상속한 예외는 그냥 지나갑니다. `KeyboardInterrupt`가 이렇게
만들어져 있습니다.

##### 사용 방법

- 외부 코드의 `except Exception`에 처리되지 않고 호출한 쪽으로 전달되어야 하는 신호만 `BaseException`을 직접
  상속합니다.
- 그 신호를 잡아 처리하는 wrapper를 반드시 함께 둡니다.
- 실패했을 때 상태를 되돌리는 코드도 `except BaseException:`으로 잡고, 되돌린 뒤 반드시 `raise`합니다. 그래야
  `KeyboardInterrupt`로 멈춰도 반쯤 바뀐 상태가 남지 않습니다.

##### 왜 필요한가

query별 시간 제한을 외부 라이브러리의 대화 loop 안에서 발생시키면, `Exception`을 상속한 예외는 그 라이브러리가
"도구 호출 실패"로 삼키고 loop를 계속 돕니다. `BaseException`이면 우리 wrapper까지 올라옵니다.

##### 예시

```python
# 예시: 외부 loop의 except Exception을 뚫고 올라오는 시간 제한 신호
class Deadline(BaseException):
    pass


def upstream_loop(step) -> None:
    """외부 코드라고 가정합니다. 오류를 잡아 출력하고 계속 돕니다."""
    for turn in range(3):
        try:
            step(turn)
        except Exception as error:
            print("upstream swallowed:", error)


def step(turn: int) -> None:
    if turn == 0:
        raise ValueError("tool failed")
    raise Deadline()


try:
    upstream_loop(step)
except Deadline:
    print("deadline reached")  # ValueError는 삼켜졌지만 Deadline은 올라왔습니다
```

##### Self-Index에서의 사용

`adapters/browsecomp/agent/oss_client_ours.py:20`, `:97`

```python
class _QueryDeadline(BaseException): ...

def _conversation_with_deadline(original, client, initial_request, tool_handler, ...):
    _QUERY_CLOCK.started = time.monotonic()
    try:
        out = original(client, initial_request, tool_handler, max_iterations, verbose)
    except _QueryDeadline as deadline:
        ...
        raise
```

상태를 되돌리는 `except BaseException:`은 `index/dense.py:312`, `retrieval/snapshots.py:63`,
`runtime/workflows/execution.py:63`에 있습니다.

##### 주의할 점

`BaseException` 상속은 일반 오류 처리를 모두 건너뛰므로, 처리할 wrapper가 정해져 있을 때만 씁니다.

#### C12. 작은 언어 기능

자주 쓰이는 작은 Python 기법을 모았습니다.

##### 사용 방법

| 기능 | 한 줄 설명 | 예시 | 레포 위치 |
|---|---|---|---|
| walrus `:=` | 값을 변수에 넣으면서 바로 조건에 씁니다 | `if unknown := sorted(set(given) - set(allowed)): raise ValueError(...)` | 37곳 |
| keyword-only argument `*` | `*` 뒤 인자는 이름으로만 넘깁니다. 같은 타입 인자가 여럿일 때 순서 실수를 막습니다 | `def optimize(texts, *, depth, limit)` | `optimize(...)` |
| `zip(strict=True)` | 두 시퀀스의 길이가 다르면 조용히 잘리지 않고 `ValueError`가 납니다 | `for step, task in zip(steps, tasks, strict=True)` | `runner.py:58` 등 |
| `dict.fromkeys(xs)` | 순서를 지키며 중복을 없앱니다. 여러 키에 같은 값을 묶을 때도 씁니다 | `list(dict.fromkeys(["b", "a", "b"]))`는 `['b', 'a']` | `validation/base.py:18` 등 |
| `MappingProxyType` | dict를 읽기 전용으로 보여 줍니다 | `OPTIONS = MappingProxyType({"k": 10})` | `harness_options.py:10`, `workflow.py:25` |
| sentinel `_MISSING = object()` | "값이 없음"과 "`None`이라는 값"을 구분합니다 | `if getattr(obj, name, _MISSING) is _MISSING:` | `compatibility.py:3` |
| `bool` 먼저 거부, 그다음 `operator.index` | `True`가 id 1로 통과하는 일을 막고, 정수로 바꿀 수 있는 값만 받습니다 | `if isinstance(x, bool): raise TypeError(...)` | `index/contracts.py:107`, `revision/base.py:12` |
| `type(code) is not int` | `bool`까지 거부하는 정확한 타입 검사입니다 | `if type(code) is not int: raise TypeError(...)` | `execution.py:77` |
| `raise ... from None` | 원래 예외를 숨깁니다. 원래 예외가 사용자에게 의미 없을 때만 씁니다 | `except BlockingIOError: raise FileExistsError(...) from None` | `build_bm25_index.py:58` |
| `if TYPE_CHECKING:` | 타입 표기에만 필요한 import를 실행 중에는 건너뜁니다 | `if TYPE_CHECKING: from .index import KeyIndex` | `pipeline/contracts.py:7` |
| 괄호로 묶은 여러 context manager | 여러 자원을 한 `with`로 열고, 줄이 길면 괄호로 묶습니다 | `with (open(a) as src, open(b, "w") as dst):` | `build_bm25_index.py:182`, `embedding.py:107` 등 4곳 |

### D. 실패에 대비하는 방법

실행 중단, 동시 실행, 외부 호출 실패에 대비해 산출물과 상태를 보호하는 방법을 다룹니다. 관찰 원본은
`self-index-coding-conventions.md`의 9~13절에 있습니다.

#### D1. Atomic replace

임시 파일에 다 쓴 뒤 한 번에 교체해서, 반쯤 쓴 파일이 남지 않게 하는 방법입니다.

##### 개념

`os.replace(src, dst)`는 같은 파일 시스템 안에서 한 번에 이름을 바꿉니다. 다른 프로세스는 이전 파일이나 완성된
새 파일 중 하나만 보게 되고, 반쯤 쓴 파일은 보지 않습니다.

##### 사용 방법

- 쓰기 함수를 인자로 받는 `atomic_replace(path, write)` 하나로 JSON, JSONL, numpy 파일을 모두 처리합니다.
- 임시 파일은 같은 디렉터리에 `.`으로 시작하는 숨김 파일로 만듭니다.
- 실패하면 임시 파일을 지웁니다.

##### 왜 필요한가

쓰는 도중 프로세스가 죽어도 이전 산출물이 그대로 남습니다. 다음 실행이 깨진 파일을 읽고 엉뚱한 결과를 내는 일이
없습니다.

##### 예시

```python
# 예시: 임시 파일에 다 쓴 뒤 한 번에 바꿔치기합니다
import json
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import IO


def atomic_replace(path: Path, write: Callable[[IO[str]], None]) -> None:
    # 같은 디렉터리에 숨김 임시 파일을 만들어야 os.replace가 한 번에 바꿀 수 있습니다
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(descriptor, "w") as stream:
            write(stream)
        os.replace(temporary, path)
    except BaseException:
        # 실패하면 임시 파일을 지우고 원래 오류를 그대로 올립니다
        Path(temporary).unlink(missing_ok=True)
        raise


target = Path(tempfile.mkdtemp()) / "result.json"
atomic_replace(target, lambda stream: json.dump({"ndcg": 0.41}, stream))
print(target.read_text())  # {"ndcg": 0.41}
```

##### Self-Index에서의 사용

`storage/artifacts.py:25`의 `atomic_replace(path, write)`.

#### D2. 디렉터리 교체와 backup

새 디렉터리를 따로 완성하고, 이전 것을 backup으로 옮긴 뒤 교체하는 방법입니다.

##### 사용 방법

1. 새 디렉터리를 임시 위치(staging)에서 끝까지 만듭니다.
2. 비어 있는 결과는 먼저 거부합니다.
3. 기존 디렉터리를 backup 이름으로 옮기고, 새 디렉터리를 제자리에 놓습니다.
4. 교체가 실패하면 backup을 원래 이름으로 되돌립니다.

##### Self-Index에서의 사용

`_publish_index`(`build_bm25_index.py:62`). 같은 장치면 rename, 다른 장치면 copytree로 옮깁니다.

#### D3. 되돌릴 수 있는 순서

실패할 수 있는 단계를 먼저, 되돌리기 어려운 단계를 나중에 하는 방법입니다.

##### 사용 방법

항목을 교체할 때는 새 항목 추가를 먼저 하고, 성공한 뒤에야 이전 항목을 지웁니다.

##### 왜 필요한가

추가가 실패해도 이전 항목이 그대로 있으므로, 되돌릴 때는 추가하던 것만 지우면 됩니다. 순서를 반대로 하면 지운 뒤
추가가 실패했을 때 이전 항목을 복구할 방법이 없습니다.

##### 예시

```python
# 예시: 추가를 먼저, 삭제를 나중에 합니다
def replace_keys(index: list[str], old: list[str], new: list[str]) -> None:
    start = len(index)
    try:
        # 실패할 수 있는 단계: 새 key를 검사하며 추가합니다
        for key in new:
            if not key:
                raise ValueError("key must not be empty")
            index.append(key)
    except BaseException:
        # 추가하던 것만 지우면 원래 상태로 돌아갑니다
        del index[start:]
        raise

    # 추가가 모두 성공한 뒤에야 이전 key를 지웁니다
    for key in old:
        index.remove(key)


keys = ["apple"]
try:
    replace_keys(keys, ["apple"], ["pear", ""])
except ValueError:
    pass
print(keys)  # ['apple'] — 실패했지만 이전 상태가 그대로입니다
replace_keys(keys, ["apple"], ["pear"])
print(keys)  # ['pear']
```

##### Self-Index에서의 사용

`_replace_encoded`(`index/dense.py:302`). 추가가 실패하면 shard별 count와 text 목록만 원래 길이로 돌립니다.

#### D4. 기다리지 않는 파일 lock

여러 프로세스가 같은 산출물을 쓰려 하면 기다리지 않고 바로 실패시키는 방법입니다.

##### 개념

`fcntl.flock(f, LOCK_EX | LOCK_NB)`는 파일에 배타 lock을 걸되, 이미 다른 프로세스가 잡고 있으면 기다리지 않고
바로 `BlockingIOError`를 냅니다.

##### 사용 방법

lock을 잡지 못하면 "another build is publishing ..."처럼 무슨 일이 일어났는지 말하는 오류로 바꿔 올립니다.

##### 왜 필요한가

두 프로세스가 같은 산출물을 동시에 쓰면 결과가 섞입니다. 기다리게 하면 사용자는 왜 멈춰 있는지 모릅니다.

##### Self-Index에서의 사용

`build_bm25_index.py:50`, `runtime/workflows/execution.py:48`.

#### D5. 재개 검증

중단된 작업을 재개하기 전에 해시로 실행 조건과 산출물이 같은지 확인하는 방법입니다.

##### 사용 방법

- 단계가 끝날 때마다 산출물의 sha256을 기록(receipt)하고, 이어서 실행할 때 다시 해시해서 비교합니다.
- 설정 환경 변수, 소스 코드, 입력 파일의 해시(실행 identity)도 기록해 두고, 하나라도 다르면 이어서 실행하지
  않습니다.
- 단계 상태(`running`, `failed`, `complete`)와 실패한 예외 타입 이름은 `workflow_status.json`에 원자적으로
  씁니다.

##### 왜 필요한가

설정이나 코드가 바뀐 뒤 이전 실행의 중간 결과를 이어 붙이면, 서로 다른 조건의 결과가 섞인 산출물이 나옵니다.
이런 결과는 겉보기로는 구분할 수 없습니다.

##### Self-Index에서의 사용

`WorkflowCheckpoint`(`runtime/workflows/checkpoints.py:43`)가 실행 identity와 산출물 해시를 확인하고,
`StageRunner`(`runtime/workflows/execution.py:54`)가 완료한 단계를 건너뛰고 나머지를 실행합니다.

결과가 어떤 조건에서 만들어졌는지 추적하는 **provenance**도 기록합니다.
`ProvenanceWriter.write()`(`storage/provenance.py:90`)는 소스 복사본을 `src/`에 저장하고,
소스 해시, git HEAD와 변경 여부, Python·패키지 버전을 `src/manifest.json`에 기록합니다.
데이터 fingerprint와 설정 정보는 `run_config.json`에 저장합니다
(`pipeline/run.py:219`). 재개 시 검증과 함께, 나중에 서로 다른 실행 결과의 조건을 비교하는 데 쓰입니다.

#### D6. 저장 형식 version

저장 형식에 version을 넣고, 읽을 때 version, shape, 수치를 검사하는 방법입니다.

##### 사용 방법

- 저장하는 쪽은 version 필드를 함께 씁니다.
- 읽는 쪽은 파일이 없으면 고치는 방법을 알리고, version이 다르면 거부합니다.
- numpy 파일은 `allow_pickle=False`로 열고, 배열의 차원, dtype, 유한성, 값 범위를 검사합니다.

##### 왜 필요한가

형식이 바뀐 이전 파일을 읽었을 때, 엉뚱한 값으로 계속 돌지 않고 읽는 순간 실패합니다. `allow_pickle=False`는
신뢰할 수 없는 파일이 임의 코드를 실행하는 경로를 막습니다.

##### Self-Index에서의 사용

`MemoryKeyState.save`/`load`(`adapters/longmem/adapter/key_state.py:59`, `:75`).

#### D7. 외부 코드 전제 검사

adapter가 기대는 외부 코드의 전제를 실행 전에 검사하는 방법입니다.

##### 사용 방법

judge evaluator를 불러올 때 upstream 스크립트를 AST로 읽어, 예상한 import가 정확히 하나 있는지 확인합니다.
다르면 "upstream evaluator inference contract changed; review the adapter"로 멈춥니다.

##### 왜 필요한가

upstream을 새 버전으로 바꿨을 때 adapter가 조용히 잘못 도는 대신, 시작할 때 무엇을 다시 봐야 하는지 알려 줍니다.

##### Self-Index에서의 사용

`adapters/browsecomp/adapters/judging.py:72`.

#### D8. 재시도할 오류 구분

재시도해도 소용없는 오류와 일시적인 오류를 나누고, 재시도 정책은 한 곳에서 정하는 방법입니다.

##### 사용 방법

- HTTP 4xx는 요청 자체가 잘못된 것이므로 바로 올립니다. 다만 408(시간 초과)과 429(요청 과다)는 일시적인 오류로
  봅니다.
- 나머지 오류만 다음 replica로 넘겨 재시도합니다.
- OpenAI SDK client는 `max_retries=0`으로 만들어서, 재시도 정책을 SDK가 아니라 우리 코드 한 곳에서 정합니다.

##### 왜 필요한가

잘못된 요청을 재시도하면 시간만 쓰고 결과는 같습니다. SDK와 우리 코드가 각자 재시도하면 실제 재시도 횟수가
곱해집니다.

##### 예시

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

##### Self-Index에서의 사용

`llm/requests.py:11`, `llm/client.py:49`, `endpoints.py:68`, `oss_client_ours.py:78`.

#### D9. 결과 검사

다음 단계로 넘기기 전에 결과의 개수와 수치를 검사하는 방법입니다.

##### 사용 방법

점수 block이 query 수보다 많아도, 적어도, 비어 있어도, NaN이 섞여도 실패시킵니다.

##### 왜 필요한가

개수가 어긋난 결과를 평균 내면 숫자는 나오지만 틀린 숫자입니다. 이런 오류는 나중에 발견하기 가장 어렵습니다.

##### Self-Index에서의 사용

`PipelineEvaluation.measure`(`evaluation/evaluator.py:24`).

### E. 설계할 때 주의할 점

Self-Index의 구현을 살펴보며 정리한 설계상의 주의점입니다. 각 항목은 어떤 문제가 생길 수 있는지와,
다른 프로젝트에 적용할 때 무엇을 기준으로 판단할지를 설명합니다.

#### 실패와 정상 결과를 구분하기

**주의할 점:** 오류가 났을 때 빈 결과나 기본값을 반환하면, 호출한 쪽은 작업이 실패한 것인지 정상적으로
결과가 없었던 것인지 구분하기 어렵습니다. 실패한 항목이 집계에서 빠지면 결과가 실제보다 좋아 보일 수도 있습니다.

**적용 기준:** 계속 진행해도 되는 실패인지 먼저 판단합니다. 계속 진행한다면 실패한 대상, 이유, 건수를
남기고 정상 결과와 구분합니다. 화면에 짧은 오류 요약을 보여 주더라도 원인을 확인할 수 있는 상세 기록은 보존합니다.

관련 주제: 재시도할 오류 구분(D8), 결과 검사(D9).

#### 입력을 보정하기 전에 허용 조건을 정하기

**주의할 점:** 잘못된 입력을 자동으로 바꾸면 사용자가 요청한 조건과 실제 실행 조건이 달라질 수 있습니다.
입력을 받는 곳마다 검사 방식이 다르면 같은 값이 어느 경로에서는 통과하고 다른 경로에서는 거부됩니다.

**적용 기준:** 허용할 값과 중복 여부를 입력을 받는 공통 지점에서 검사합니다. 의미를 바꾸지 않는 정규화와
잘못된 값의 보정을 구분하고, 보정이 필요한 기능이라면 그 규칙과 실제 적용된 값을 알려 줍니다.
registry의 이름 중복도 같은 원칙으로 검사합니다.

관련 주제: 실행 전 전체 검증(A4), Registry(B3).

#### 상태의 소유자와 변경 범위를 명확히 하기

**주의할 점:** 여러 객체가 같은 상태를 공유하면 한쪽의 변경이 다른 쪽의 동작에 영향을 줍니다.
객체가 불변으로 선언되어 있어도 내부의 list나 dict까지 불변인 것은 아닙니다.

**적용 기준:** 상태를 누가 보관하고 누가 변경할 수 있는지 정합니다. 객체가 사용할 속성은 초기화 시점에
드러내고, 공유가 필요 없는 값은 객체별로 보관합니다. 읽기 전용으로 전달할 값은 내부 데이터의 변경 가능성까지
확인합니다. lock은 동시 접근을 조율하지만, 서로 다른 실행이 같은 설정을 공유해도 되는지까지 해결해 주지는 않습니다.

관련 주제: Context와 상태 객체(B7), Dataclass(C1), Context manager(C7).

#### 함께 바뀌어야 하는 값은 한곳에서 관리하기

**주의할 점:** 같은 정책을 여러 곳에 따로 정의하면 한 곳만 수정했을 때 동작이 달라집니다.
반대로 숫자가 우연히 같다는 이유만으로 하나의 상수로 합치면, 서로 다른 정책을 독립적으로 바꾸기 어려워집니다.

**적용 기준:** 값이 같은지가 아니라 의미가 같고 함께 변경되어야 하는지를 기준으로 묶습니다.
공통 정책은 한곳에서 정의하고, 서로 다른 제한이나 설정에는 각각의 목적이 드러나는 이름을 붙입니다.
설정에 대응하는 문서도 함께 갱신합니다.

관련 주제: 저장소 문서의 역할 분담(A6).

#### 공개 interface의 사용 조건을 명시하기

**주의할 점:** 이름이 명확하고 함수가 짧아도, 어떤 입력을 받고 무엇을 반환하며 언제 실패하는지까지
알 수 있는 것은 아닙니다. 필수 기능과 선택 기능의 구분이 없으면 새 구현을 만드는 사람도 무엇을 구현해야 할지
판단하기 어렵습니다.

**적용 기준:** 공개 함수에는 입력·반환 타입을 적고, 타입만으로 표현하기 어려운 조건과 실패 동작은 설명합니다.
모든 구현에 필요한 기능과 일부 구현만 지원하는 기능을 구분하고, 같은 역할의 interface는 일관된 방식으로 표현합니다.

관련 주제: ABC와 Protocol(B1), Abstract method(C6).
