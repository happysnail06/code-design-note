# Coding Convention — SELF-INDEX 코드베이스에서 뽑은 작성 규약

이 문서는 [augustinLib/Self-Index](https://github.com/augustinLib/Self-Index)(commit `9c6fade`)의
Python 소스 131개 파일, 약 9,600줄을 전부 읽고 정리한 코딩 규약입니다. 각 항목은 "이 레포가 실제로
이렇게 한다"는 관찰과 "앞으로 이렇게 쓴다"는 규칙을 함께 적었고, 근거가 되는 위치를
`파일:줄` 형식으로 달았습니다. 마지막 두 절에는 이 레포에서 따라 하지 않을 부분과, 기존 작업 원칙과
충돌해서 결정이 필요한 부분을 따로 모았습니다.

---

## 0. 숫자로 본 이 코드베이스의 성격

| 항목 | 값 |
|---|---|
| 함수 수 | 704개 |
| 함수 길이 | 중앙값 6줄, 평균 9줄, 상위 10% 경계 20줄 |
| 10줄 이하 함수 | 479개 (68%) |
| 20줄 이하 함수 | 640개 (91%) |
| 가장 긴 함수 | `optimize` 56줄 (`src/selfindex/pipeline/optimizer.py:275`) |
| docstring | 0개 |
| 주석 줄 | 0줄 (shebang과 `# noqa` 제외) |
| 반환 타입 표기가 있는 함수 | 50개 (7%) |
| `_`로 시작하는 private 함수 | 229개 |
| `raise ValueError` / `TypeError` / `RuntimeError` | 101 / 16 / 15회 |
| `@dataclass` (그중 `frozen=True`) | 33개 (20개) |
| 함수 안에서 하는 지연 import | 146곳 |
| `print(..., flush=True)` | 62곳 (`logging` 모듈은 쓰지 않음) |

요약하면 이 코드는 **짧은 함수, 서술적인 이름, 입구에서의 엄격한 검증, 명시적인 등록(registry),
원자적인 파일 쓰기**로 품질을 확보하고, 설명은 주석이 아니라 이름과 README·docs에 맡기는
스타일입니다.

---

## 1. 레이어와 의존 방향

### 관찰

```
run.py                      CLI 진입점. 인자 파싱과 Runner 호출만 한다.
└─ runtime/                 실험을 계획(plan)하고 실행(run)한다.
   ├─ runner.py             ExperimentSpec → ExecutionPlan → Task 실행
   ├─ catalog/              benchmark·retriever 등록부
   ├─ factories.py          family별 Task 생성기
   ├─ commands.py           "이름 → module:function" 명령 표
   ├─ platform/             환경 변수, endpoint, device, encoder 설정
   └─ workflows/            재개 가능한 stage 실행과 checkpoint
└─ pipeline/                index evolution 알고리즘 본체
   ├─ engine.py             round loop
   ├─ optimizer.py          진단 → 수정 → 검증
   ├─ strategies/           signal·selector (교체 가능한 slot)
   └─ exploration/, lifecycle/, generation/
└─ index/, retrieval/, validation/, encoding/   알고리즘이 쓰는 부품
└─ storage/                 산출물 쓰기, provenance
└─ common/                  prompt 상수, JSON 파싱, 모델 이름표
adapters/                   외부 benchmark와 연결하는 코드 (browsecomp, longmem)
externals/                  upstream 코드. git submodule로 pin하고 수정하지 않는다.
```

- framework(`src/selfindex`)와 외부 benchmark 연결 코드(`adapters/`)를 패키지 단위로 분리합니다.
  framework는 adapter를 **지연 import**로만 부르고(`benchmarks.py`의 `from browsecomp... import`가
  전부 메서드 안에 있음), adapter는 framework를 자유롭게 import합니다.
- 공식 benchmark 코드는 `externals/`에 submodule로 고정 commit을 걸고, 고치지 않고 adapter에서
  감싸서 씁니다 (`externals/README.md`).

### 규칙

1. 진입점(CLI)은 인자를 파싱하고 spec 객체를 만들어 넘기는 일만 합니다. 로직을 두지 않습니다.
2. "무엇을 할지 계획한다"와 "실행한다"를 다른 함수로 나눕니다. 이 레포는 `Runner.plan()`이
   실행 없이 `ExecutionPlan`을 돌려주고, `run_experiment()`가 그 plan을 실행합니다
   (`src/selfindex/runtime/runner.py:41`, `:53`). 덕분에 `--dry-run`은 plan을 JSON으로 출력하기만
   하면 됩니다 (`run.py:176`).
3. 내 코드와 외부 코드의 경계는 디렉터리로 드러냅니다. 외부 코드는 pin하고 수정하지 않습니다.
4. 상위 레이어가 하위 레이어의 선택적 의존성(torch, pyserini, upstream 모듈)을 import 시점에
   끌어오지 않도록, 무거운 의존성은 쓰는 함수 안에서 import합니다 (8절 참고).

---

## 2. 파일과 모듈 구성

### 관찰

- **파일이 작습니다.** 가장 큰 소스 파일이 370줄(`pipeline/optimizer.py`)이고, 대부분 20~130줄입니다.
  `common/io.py`는 24줄, `runtime/platform/devices.py`는 13줄입니다.
- **계약과 구현을 파일로 나눕니다.** `index/contracts.py`, `retrieval/contracts.py`,
  `encoding/contracts.py`, `pipeline/contracts.py`, `validation/base.py`, `revision/base.py`가
  ABC·Protocol·공용 dataclass만 담고, 구현은 `dense.py`, `lexical.py` 같은 형제 파일에 둡니다.
- **prompt는 코드와 분리된 상수 모듈에 둡니다.** `common/optimizer_prompts.py`,
  `common/judge_prompts.py`, `pipeline/generation/prompts.py`.
- **경로 상수는 전용 모듈에 둡니다.** `adapters/browsecomp/agent/_paths.py`,
  `adapters/longmem/adapter/paths.py`, `runtime/platform/environment.py`. 경로는 모두
  `Path(__file__).resolve().parents[N]`에서 출발해 계산하므로 실행 위치(cwd)에 의존하지 않습니다.
- **upstream을 sys.path에 올리는 일은 `_bootstrap.py` 한 곳에서만 합니다**
  (`adapters/browsecomp/agent/_bootstrap.py`, `adapters/longmem/adapter/_bootstrap.py`).
- 빈 패키지의 `__init__.py`에는 `...` 한 줄만 둡니다.
- 모델 이름표는 dict 상수 모듈로 모읍니다 (`common/models/encoders.py`의 `ENCODERS`,
  `common/models/roles.py`의 `AGENT_MODEL` 등).

### 규칙

1. 한 파일은 한 가지 관심사를 담고, 300줄을 넘기기 시작하면 분할을 검토합니다.
2. 인터페이스(ABC, Protocol, 공용 값 타입)는 `contracts.py` 또는 `base.py`에 두고, 구현 파일은
   그 계약을 import해서 씁니다.
3. prompt 문자열, 모델 id, 경로처럼 "데이터에 가까운 것"은 로직 파일 밖의 상수 모듈에 둡니다.
4. 파일 경로는 항상 소스 파일 위치를 기준으로 계산하고, `os.getcwd()`에 기대지 않습니다.
5. `sys.path` 조작은 bootstrap 모듈 하나에 가둡니다.

---

## 3. 이름 짓기

### 관찰

- 이름이 길어도 뜻이 바로 드러나는 쪽을 고릅니다. `discard_unanswered_runs`, `answer_every_query`,
  `replace_validated_many`, `permanent_client_error`, `evolution_stage_steps`,
  `_corpus_has_substantive`.
- **상수 이름에 단위를 붙입니다.** `REQUEST_TIMEOUT_SECONDS`, `MCP_POLL_SECONDS`,
  `DOCUMENT_CHARS`, `KEY_MAX_CHARS`, `DIAGNOSIS_TOKENS`, `SCORE_MEMORY_BYTES`,
  `MAX_GROWTH_BYTES`, `TOKEN_BUDGET_PER_ITEM`, `STDOUT_TAIL_CHARS`. 숫자만 보고 단위를 추측할
  필요가 없습니다.
- **역할 접미사가 일관됩니다.**

  | 접미사 | 뜻 | 예 |
  |---|---|---|
  | `Spec` | 실행 전 입력 명세 (불변) | `ExperimentSpec`, `RetrieverSpec`, `StepSpec` |
  | `Plan` | 실행할 단계 목록 (불변) | `ExecutionPlan`, `FullRunPlan` |
  | `Settings` | 설정 값 묶음 (불변) | `LoopSettings`, `SignalSettings`, `EncoderSettings` |
  | `State` | 실행 중 바뀌는 상태 | `RoundState`, `EditState`, `ConversationState`, `MemoryKeyState` |
  | `Report` | 실행 결과 집계 | `IterationReport` |
  | `Backend` | 교체 가능한 엔진 | `RetrieverBackend`, `DenseBackend`, `BM25Backend` |
  | `Factory` | 객체를 만들어 검증까지 하는 생성기 | `BenchmarkFactory`, `SearchAdapterFactory` |
  | `Adapter` | 외부 인터페이스에 맞추는 래퍼 | `SearchAdapter`, `LexicalIndexAdapter` |
  | `Criterion` | 검증 규칙 하나 | `SpecificityCriterion`, `SeparationCriterion` |
  | `View` / `Snapshot` | 읽기 전용 관점 | `ScoringView`, `LiveIndexView`, `IndexSnapshot` |

- boolean은 `has_`, `is_`, 형용사 property로 씁니다. `has_embeddings`, `is_new`, `enabled`,
  `shortfall`, `is_novel()`.
- 모듈 내부용 함수·클래스·전역은 `_`로 시작합니다 (함수 704개 중 229개). 모듈 내부 전용 클래스도
  `_Sender`, `_TsWriter`, `_SafeResp`, `_LeastLoadedClient`처럼 `_`를 붙입니다.
- sentinel 값은 `_MISSING = object()`처럼 이름 있는 객체로 만듭니다
  (`adapters/browsecomp/adapters/compatibility.py`).
- 예외 클래스는 의미가 드러나는 이름으로 좁게 정의합니다. `RequestRejected(RuntimeError)`,
  `_QueryDeadline(BaseException)`.

### 규칙

1. 이름만 보고 무엇을 하는지 알 수 있게 짓습니다. 축약은 `kid`, `doc`처럼 도메인에서 굳은 것만
   씁니다.
2. 숫자 상수에는 단위(`_SECONDS`, `_CHARS`, `_TOKENS`, `_BYTES`, `_ROWS`)를 이름에 넣습니다.
3. 타입 이름의 접미사는 위 표의 뜻으로 고정해서 씁니다.
4. 모듈 밖에서 쓰지 않는 것은 `_`로 시작합니다.

---

## 4. 함수 설계

### 관찰

- **함수가 짧고 한 가지 일만 합니다.** `run.py`의 `build_parser`는 `_add_experiment_options`,
  `_add_execution_options`, `_add_subcommands` 세 함수를 부르는 것으로 끝납니다
  (`run.py:36`).
- **`main`은 조립만 합니다.** `src/selfindex/pipeline/run.py:299`의 `main`은 약 30줄 동안
  `_load_task`, `_run_identity`, `_write_run_config`, `_build_context`, `_evaluation`, `_build_loop`,
  `_finish_run`을 순서대로 부르기만 합니다. 읽는 사람은 함수 이름만 따라가면 전체 흐름을 알 수
  있습니다.
- **guard clause로 빨리 돌아갑니다.**

  ```python
  def send(bodies, urls, *, requests_per_replica, api_key, usage, text):
      if not bodies:
          return []
  ```

  ```python
  def write_round_log(path, rounds):
      if not rounds:
          return
  ```

- **walrus(`:=`)로 "조회하고 바로 판단"을 한 줄에 씁니다** (37곳).

  ```python
  if missing := wanted - found:
      raise ValueError(f"trajectories.jsonl lacks {len(missing)} haystack trajectories")
  ```

- **keyword-only 인자(`*`)로 같은 타입 인자가 섞이는 실수를 막습니다.**
  `optimize(llm, view, texts, queries, *, depth, entries, limit, per_document)`
  (`pipeline/optimizer.py:275`), `endpoint(role, *, model="")`.
- **`main(argv=None)`** 형태로 써서 테스트나 다른 코드에서 argv를 직접 넘길 수 있게 합니다.
  `pipeline/run.py`의 `main(argv=None, *, llm=None)`은 LLM client까지 주입받을 수 있습니다.
- **반복되는 측정 코드는 작은 고차 함수로 뺍니다.**

  ```python
  def _timed(phases, name, action):
      started = time.time()
      result = action()
      phases[name] = round(time.time() - started, 1)
      return result

  sig = _timed(phases, "signal", lambda: self.signal.build(ctx))
  ```
  (`src/selfindex/pipeline/engine.py:11`)

- **Template method로 검증을 강제합니다.** 공개 메서드 `create()`가 하위 클래스의 `build()`를 부르고
  그 반환값의 타입과 불변식을 검사합니다.

  ```python
  def create(self, texts):
      pair = self.build(texts, self.encode)
      if not isinstance(pair, (tuple, list)) or len(pair) != 2:
          raise TypeError("backend build() must return (KeyIndex, Retriever)")
      index, retriever = pair
      if not isinstance(index, KeyIndex) or not isinstance(retriever, Retriever):
          raise TypeError("backend build() must return (KeyIndex, Retriever)")
      if index.N != len(texts):
          raise ValueError("backend index size does not match the corpus")
  ```
  (`src/selfindex/runtime/catalog/retrievers.py:27`. 같은 패턴이
  `runtime/factories.py:55`, `adapters/browsecomp/adapters/search_factory.py:56`에도 있습니다.)

### 규칙

1. 함수는 20줄 안쪽을 목표로 하고, 넘어가면 이름 붙일 수 있는 덩어리를 private 함수로 뺍니다.
2. `main`과 진입 함수는 "이름 있는 단계들을 순서대로 부르는 목차"로 씁니다.
3. 예외 상황은 함수 앞부분의 guard clause로 처리하고 본문은 정상 경로만 담습니다.
4. 같은 타입 인자가 두 개 이상이거나 의미가 헷갈리는 인자는 keyword-only로 받습니다.
5. 진입 함수는 `main(argv=None)`으로 쓰고, 외부 자원(LLM client 등)은 인자로 주입할 수 있게 엽니다.
6. 확장 지점에서는 하위 클래스가 구현하는 `build()`와, 그 결과를 검증하는 공개 `create()`를 나눕니다.

---

## 5. 데이터 모델

### 관찰

- **값은 `@dataclass(frozen=True)`**, **실행 중 바뀌는 상태는 일반 `@dataclass`** 로 나눕니다.
  - frozen: `ExperimentSpec`, `ExecutionPlan`, `Endpoint`, `ProposedKey`, `Diagnosis`,
    `RevisionDecision`, `KeySet`, `Stage`, `Command`, `LoopSettings`, `EncoderSettings` 등 20개.
  - mutable: `RoundState`, `EditState`, `QueryState`, `ConversationState`, `IterationReport`.
- **작은 레코드는 `NamedTuple`** 입니다. `KeySearchResult(key_ids, scores)`, `StepSpec`,
  `StrategySet(signal, selector)`, `_RunUsage`.
- **`__post_init__`에서 검증하고 정규화합니다.** frozen이라 정규화할 때는 `object.__setattr__`을
  씁니다.

  ```python
  @dataclass(frozen=True)
  class ProposedKey:
      text: str
      retained_from: int | None = None

      def __post_init__(self):
          if not isinstance(self.text, str) or not self.text.strip():
              raise ValueError("proposed key must contain text")
          if self.retained_from is not None:
              if isinstance(self.retained_from, bool):
                  raise ValueError("retained key id must be an integer")
              object.__setattr__(self, "retained_from", operator.index(self.retained_from))

      @property
      def is_new(self):
          return self.retained_from is None
  ```
  (`src/selfindex/revision/base.py:8`. `Endpoint`도 같은 방식으로 URL을 검증하고 끝의 `/`를
  지웁니다: `runtime/platform/endpoints.py:47`.)

- **`bool`이 `int`의 하위 타입이라는 함정을 막습니다.** 정수 id를 받는 곳은 `isinstance(x, bool)`을
  먼저 거부하고 `operator.index()`로 정수화합니다 (`index/contracts.py:107`,
  `revision/base.py:12`).
- **dict 상수를 불변으로 만듭니다.** `READER_PROTOCOL = MappingProxyType({...})`
  (`adapters/longmem/adapter/harness_options.py:10`). frozen dataclass가 받은 dict도
  `__post_init__`에서 `MappingProxyType(dict(...))`로 감쌉니다
  (`adapters/browsecomp/pipeline/workflow.py:25`).
- **mutable 기본값은 항상 `field(default_factory=...)`** 로 둡니다.
- **생성 경로가 여러 개면 classmethod로 이름을 붙입니다.** `LoopSettings.from_env()`,
  `EncoderSettings.of(name, **corpus_settings)`, `FullRunPlan.create(tag, retriever, agent)`,
  `Backbone.for_model(model)`, `MemoryKeyState.load(...)`.
- **파생 값은 저장하지 않고 property로 계산합니다.** `Diagnosis.shortfall`, `ProposedKey.is_new`,
  `RevisionDecision.replacement`, `NDCGMetric.label`.
- **밖으로 내보내는 배열을 읽기 전용으로 만듭니다.** `ids.setflags(write=False)`
  (`retrieval/snapshots.py:144`).

### 규칙

1. 실행 중 바뀌지 않는 값은 frozen dataclass나 NamedTuple로 만들고, 상태만 mutable dataclass로 둡니다.
2. 생성 시점 검증은 `__post_init__`에서 하고, 잘못된 값은 객체가 만들어지기 전에 거부합니다.
3. 정수 id를 받을 때는 `bool`을 먼저 거부하고 `operator.index()`로 정수화합니다.
4. 모듈 수준 dict 상수와 외부에서 받은 설정 dict는 `MappingProxyType`으로 감쌉니다.
5. 생성 방법이 둘 이상이면 `from_env`, `of`, `create`, `load` 같은 이름 있는 classmethod로 나눕니다.
6. 다른 필드에서 계산되는 값은 필드로 두지 않고 property로 둡니다.

---

## 6. 확장 지점: Registry와 등록 함수

### 관찰

- **이름 기반 등록부를 하나의 제네릭 클래스로 통일합니다.**

  ```python
  class Registry(Mapping[str, T], Generic[T]):
      def __init__(self, kind: str):
          self.kind = kind
          self._items: dict[str, T] = {}

      def validate_name(self, name: str) -> None:
          if not isinstance(name, str) or not name.strip():
              raise ValueError(f"{self.kind}: a nonempty name is required")
          if name in self._items:
              raise ValueError(f"{self.kind} already registered: {name}")

      def register(self, name: str, value: T) -> T:
          self.validate_name(name)
          self._items[name] = value
          return value
  ```
  (`src/selfindex/runtime/registry.py:9`). `Mapping`을 상속했으므로 `in`, `sorted()`,
  `.items()`가 그대로 동작하고, 외부에서 `__setitem__`으로 덮어쓸 수 없습니다. `kind`는 오류
  메시지에만 쓰입니다.

- **공개 `register_*` 함수가 타입을 검사하고 등록합니다.** `register_benchmark`,
  `register_domains`, `register_retriever`, `register_factory`, `register_search_adapter`,
  `register_command`. 확장하는 사람은 README의 "Extending" 절에 적힌 함수만 알면 됩니다.
- **여러 개를 등록할 때는 전부 검증한 다음에 등록합니다.** 중간에 실패해서 절반만 등록된 상태가
  남지 않습니다.

  ```python
  adapters = tuple(benchmark_type(domain) for domain in domains)
  names, corpora = set(), set()
  for adapter in adapters:
      BENCHMARKS.validate_name(adapter.name)
      CORPORA.validate_name(adapter.domain)
      if adapter.name in names or adapter.domain in corpora:
          raise ValueError("duplicate domain registration")
      names.add(adapter.name)
      corpora.add(adapter.domain)
  for adapter in adapters:
      register_benchmark(adapter)
  ```
  (`src/selfindex/runtime/catalog/benchmarks.py:260`)

- **등록 방식을 용도에 맞게 고릅니다.**
  - decorator: `@OptimizerBackbone.register("my-org/my-model")` (`llm/backbones.py:15`).
    클래스마다 `backbones = {}`를 따로 두어 역할별 등록부가 섞이지 않습니다.
  - `__init_subclass__`: `name`이 있는 하위 클래스는 정의만 해도 등록됩니다
    (`adapters/browsecomp/agent/backbones.py:45`).
  - 문자열 표: `COMMANDS = {"bc.agent": "browsecomp.agent.run_backbone:main", ...}`
    (`runtime/commands.py`). 명령을 실제로 실행할 때만 import하므로 목록 출력이 가볍습니다.
- **조회 실패 메시지에 선택지를 나열합니다.**
  `f"unsupported BrowseComp agent: {name}; available: {', '.join(_REGISTRY)}"`.
- **모델별 차이는 하위 클래스의 class attribute로만 표현합니다.**

  ```python
  @AgentBackbone.register(KIMI_AGENT_MODEL)
  class KimiK25Agent(AgentBackbone):
      extra_body = {"provider": {"order": ["SiliconFlow", "DeepInfra"], "allow_fallbacks": False}}
  ```
  기본 클래스의 `body()`는 `deepcopy(self.extra_body)`를 합쳐서, class attribute dict가 요청마다
  공유·변형되지 않게 합니다 (`llm/backbones.py`).

### 규칙

1. 교체 가능한 구현은 `Registry` 하나로 관리하고, 등록과 조회는 공개 함수로만 합니다.
2. 이름 중복과 빈 이름은 등록 시점에 거부합니다.
3. 여러 항목을 한 번에 등록할 때는 검증을 전부 끝낸 뒤에 등록합니다.
4. 조회에 실패하면 "무엇이 없는지"와 "무엇을 쓸 수 있는지"를 같이 알려 줍니다.
5. 구현마다 다른 부분은 class attribute로 선언하고, 공유 기본 클래스의 로직은 그대로 둡니다.
   class attribute로 둔 mutable 값은 사용할 때 복사합니다.

---

## 7. 계약(Contract) 정의

### 관찰

- **필수 동작은 `@abstractmethod`, 선택 동작은 이유를 밝히는 `NotImplementedError`** 로 나눕니다.

  ```python
  class ScoringView(ABC):
      @abstractmethod
      def key_scores(self, queries, kids): ...

      def original_scores(self, queries):
          raise NotImplementedError(
              f"{type(self).__name__} does not expose original-document scores"
          )
  ```
  (`src/selfindex/index/contracts.py:47`. `KeyIndex.replace_validated`, `Retriever.snapshot`도 같은
  방식입니다.)

- **선택 동작에 기본 구현을 줄 수 있으면 줍니다.** `KeyIndex.replace_validated_many`는
  `replace_validated`를 반복 호출하는 기본 구현을 두고, dense index만 일괄 처리로 override합니다.
- **구조적 타입은 `Protocol`** 로 둡니다. `TextEncoding`, `GenerationClient`
  (`pipeline/contracts.py:15`). 덕분에 LLM client를 가짜 객체로 바꿔 넣기 쉽습니다.
- **타입 표기만을 위한 import는 `TYPE_CHECKING` 블록** 에 둡니다 (`pipeline/contracts.py:7`,
  `adapters/browsecomp/pipeline/workflow.py:15`). 순환 import와 무거운 import를 피합니다.
- 추상 메서드 본문은 `...` 한 줄로 씁니다.

### 규칙

1. 모든 구현이 반드시 가져야 하는 동작만 `@abstractmethod`로 둡니다.
2. 일부 구현만 지원하는 동작은 기본 구현에서 `NotImplementedError(f"{type(self).__name__} does not ...")`
   로 실패하게 하고, 메시지에 구현 클래스 이름을 넣습니다.
3. 상속 관계가 필요 없는 의존성(LLM client, encoder 함수)은 `Protocol`로 표현합니다.
4. 타입 표기 때문에 생기는 import는 `if TYPE_CHECKING:` 안에 둡니다.

---

## 8. 설정, 환경 변수, 지연 import

### 관찰

- **조정 가능한 파라미터는 dict 한 곳에 기본값과 함께 둡니다.**

  ```python
  PARAMETERS = {"ROUNDS": 20, "QUERIES_PER_ROUND": 128, "RETRIEVAL_DEPTH": 30, "MAX_KEYS": 10, "SEED": 42}
  POSITIVE_PARAMETERS = ("QUERIES_PER_ROUND", "RETRIEVAL_DEPTH", "MAX_KEYS")

  def parameter(name) -> int:
      value = int(os.environ.get(name, PARAMETERS[name]))
      if name in POSITIVE_PARAMETERS and value < 1:
          raise ValueError(f"{name} must be at least 1")
      return value
  ```
  (`src/selfindex/pipeline/settings.py:14`). README의 Parameters 표와 이 dict가 1:1로 대응합니다.

- **기본값에서 바뀐 설정만 로그에 출력합니다** (`pipeline/run.py:64`의 `_settings_banner`).
  로그를 보면 이번 실행이 기본값과 어디가 다른지 바로 압니다.
- **환경 변수 이름은 상수로 한 번만 씁니다.** `API_KEY_ENV = "OPENAI_API_KEY"`, 서비스 URL은
  `f"{role}_BASE_URL"` 규칙 하나로 만듭니다 (`runtime/platform/endpoints.py:82`).
- **endpoint URL을 생성 시점에 검증합니다.** scheme이 http(s)가 아니거나, credential·query·fragment가
  들어 있으면 거부합니다 (`endpoints.py:72`).
- **실행 전에 필요한 서비스가 모두 설정됐는지 먼저 확인합니다.** `validate_services(plan)`이 plan의
  모든 step이 요구하는 `*_BASE_URL`을 검사한 뒤에야 첫 step을 실행합니다
  (`runtime/configuration.py:7`). agent는 `check_service()`에서 실제로 서빙 중인 모델 id가 기대한
  모델과 같은지도 확인합니다 (`adapters/browsecomp/agent/backbones.py`의 `GptOss.check_service`).
- **무거운 의존성은 함수 안에서 import합니다** (146곳). `torch`, `transformers`, `pyserini`,
  `tevatron`, `openai`, upstream 모듈이 대상입니다. 그래서 `python run.py list`는 GPU 라이브러리
  없이도 돌아갑니다.
- **비싼 조회는 캐시합니다.** `@functools.cache`로 endpoint의 `/models` 조회를 한 번만 합니다
  (`endpoints.py:18`). 모델 로딩은 모듈 수준 `_MODELS` dict에 캐시합니다
  (`encoding/encoders.py:9`).

### 규칙

1. 실험 파라미터는 `PARAMETERS` 같은 dict 하나에 기본값과 함께 모으고, 읽을 때 검증하는 함수
   하나로만 읽습니다. 문서의 파라미터 표는 이 dict와 같은 내용을 유지합니다.
2. 실행 로그 첫머리에 기본값과 달라진 설정을 출력합니다.
3. 외부 서비스 설정은 첫 작업을 실행하기 전에 전부 검증합니다. 가능하면 실제 서비스에 붙어서
   (모델 id 등) 기대와 같은지까지 확인합니다.
4. 선택적이거나 무거운 의존성은 그것을 쓰는 함수 안에서 import합니다.

---

## 9. 오류 처리

### 관찰

- **입구에서 엄격하게 검증하고 바로 실패합니다.** `raise ValueError`가 101회 나옵니다. 잘못된 입력을
  받아서 조용히 보정하는 대신 이유를 말하고 멈춥니다.
- **오류 메시지는 "무엇이 요구되는지"를 소문자 평서문으로 씁니다.**
  - `"a domain must be one nonempty path component"`
  - `"endpoint URL must not contain credentials or query parameters"`
  - `"--index needs the key set's --keys"`
  - `"configure JUDGE_BASE_URL"`
  - `"requested keys differ from the saved memory; rebuild instead of mixing key sets"`

  마지막 예처럼 **해결 방법까지** 메시지에 넣는 경우가 많습니다.
- **예외 종류를 의미에 맞게 고릅니다.** 값이 틀리면 `ValueError`, 타입이나 계약 위반이면
  `TypeError`, 실행 중 외부 결과가 기대와 다르면 `RuntimeError`, 파일이 없으면
  `FileNotFoundError`, 이미 있으면 `FileExistsError`.
- **사용자 입력 오류는 `parser.error()`로 바꿔서 CLI 형식으로 보여 줍니다** (`run.py:182`).
- **내부 예외를 다른 예외로 바꿀 때 원인 체인이 의미 없으면 `from None`** 을 씁니다
  (`adapters/browsecomp/pipeline/build_bm25_index.py:58`).
- **영구 오류와 일시 오류를 구분해서 재시도합니다.**

  ```python
  def permanent_client_error(status):
      return (
          isinstance(status, int)
          and HTTPStatus.BAD_REQUEST <= status < HTTPStatus.INTERNAL_SERVER_ERROR
          and status not in (HTTPStatus.REQUEST_TIMEOUT, HTTPStatus.TOO_MANY_REQUESTS)
      )
  ```
  4xx(408, 429 제외)는 `RequestRejected`로 즉시 올리고, 나머지만 재시도합니다
  (`llm/requests.py:11`, `llm/client.py:49`). 재시도할 때는 다음 replica로 넘어갑니다
  (`self.urls[(index + attempt) % len(self.urls)]`). Gemini client는 서버가 알려 준 대기 시간을
  읽고, jitter를 더하고, 상한을 둡니다 (`gemini_client_ours.py:43`).
- **실패하면 상태를 되돌립니다.**
  - `_replace_encoded`는 key를 추가하다 실패하면 shard별 count와 text 목록을 원래 길이로 되돌리고
    다시 올립니다 (`src/selfindex/index/dense.py:302`).
  - `_publish_index`는 기존 index를 backup으로 rename한 뒤 새 index를 rename하고, 실패하면
    backup을 되돌립니다 (`build_bm25_index.py:62`).
  - snapshot `__enter__`는 view 생성에 실패하면 lease와 lock을 풀고 다시 올립니다
    (`retrieval/snapshots.py`).
- **바꾼 전역 상태는 `finally`에서 복원합니다.** `sys.argv`, `os.chdir`, `sys.path`, stdout을 바꾸는
  곳은 모두 try/finally로 감쌉니다 (`agent/judge_run.py:12`, `runtime/commands.py:57`,
  `adapters/browsecomp/adapters/judging.py:72`).
- **정리 코드가 겹칠 때는 `finally` 안에 다시 `try/finally`를 둡니다.**

  ```python
  finally:
      try:
          _report_aborted()
      finally:
          client.close()
  ```
  (`adapters/browsecomp/agent/oss_client_ours.py`의 `main`)

- **출력의 완전성을 검증합니다.** 기대한 query id 집합과 실제 결과 집합이 정확히 같은지 확인합니다
  (`adapters/browsecomp/pipeline/specification.py:34`의 `verify_evaluation`). agent 실행은 최대
  5 pass까지 답이 없는 query만 다시 돌리고, 끝까지 빠진 것이 있거나 query set 밖의 결과가 섞이면
  실패합니다 (`agent/run_backbone.py:62`).
- **숫자 결과가 유한한지 확인합니다.** `np.isfinite(...).all()`, `torch.isfinite(...).all()` 검사가
  evaluation, validation, key embedding, memory 점수 경로마다 있습니다
  (`evaluation/evaluator.py:44`, `validation/base.py`, `index/dense.py`의 `key_vectors`).

### 규칙

1. 잘못된 입력은 받는 즉시 이유를 밝혀 실패시킵니다. 조용한 보정은 하지 않습니다.
2. 오류 메시지는 요구 조건을 평서문으로 쓰고, 가능하면 고치는 방법이나 선택지를 함께 적습니다.
3. 예외 타입은 값 오류(`ValueError`), 계약 위반(`TypeError`), 실행 결과 이상(`RuntimeError`)으로
   구분합니다.
4. 외부 호출은 영구 오류와 일시 오류를 나누고, 일시 오류만 backoff를 두고 재시도합니다.
5. 여러 단계로 상태를 바꾸는 작업은 실패했을 때 되돌리는 코드를 같이 씁니다.
6. `sys.argv`, cwd, `sys.path`, 전역 속성을 바꾸면 반드시 `finally`나 context manager로 복원합니다.
7. 결과가 기대한 집합을 정확히 덮는지, 수치가 유한한지 검증한 뒤에 다음 단계로 넘깁니다.

---

## 10. 파일 쓰기와 산출물

### 관찰

- **모든 산출물 쓰기는 원자적입니다.**

  ```python
  def atomic_replace(path, write, **temporary_options):
      path = Path(path)
      pending = None
      try:
          with tempfile.NamedTemporaryFile(dir=path.parent, delete=False, **temporary_options) as stream:
              pending = Path(stream.name)
              write(stream)
          os.replace(pending, path)
          pending = None
      finally:
          if pending is not None:
              pending.unlink(missing_ok=True)
  ```
  (`src/selfindex/storage/artifacts.py:25`). 임시 파일을 **같은 디렉터리**에 만들어서
  `os.replace`가 같은 파일시스템 안의 원자적 rename이 되게 합니다. 중간에 죽어도 반쯤 쓰인 파일이
  남지 않습니다. `LocalArtifactStore.write_json` / `write_jsonl`이 이 함수를 감쌉니다.
- **디렉터리 단위 산출물은 staging → rename으로 게시합니다.** BM25 index는 임시 디렉터리에서 만든
  뒤, 같은 장치면 rename하고 다른 장치면 copytree한 다음 교체합니다
  (`build_bm25_index.py:62`).
- **동시에 같은 대상을 쓰지 못하게 파일 lock을 겁니다.** `fcntl.flock(..., LOCK_EX | LOCK_NB)`로
  즉시 실패시키고, "another build is publishing ..."이라고 알려 줍니다 (`build_bm25_index.py:50`,
  `runtime/workflows/execution.py`).
- **경로 안전성을 검사합니다.** 게시 대상이 symlink인지, index 루트 자체나 상위 디렉터리인지,
  산출물 경로가 출력 디렉터리 밖으로 나가는지(`is_relative_to`) 확인합니다
  (`build_bm25_index.py:123`, `runtime/workflows/checkpoints.py`의 `_path`).
- **재개(resume)는 receipt로 검증합니다.** 각 stage가 끝나면 산출물의 sha256을 receipt에 기록하고,
  재개할 때 파일이 그대로인지 다시 해시합니다. 실행 identity(설정 환경 변수, 소스 해시, 입력 파일
  해시)가 바뀌었으면 재개를 거부합니다 (`runtime/workflows/checkpoints.py:43`,
  `adapters/browsecomp/pipeline/workflow.py:39`). 기존 receipt가 있는데 `--resume`이 없으면
  덮어쓰지 않고 실패합니다.
- **실행마다 provenance를 남깁니다.** 소스 파일 복사본과 sha256, git HEAD와 dirty 여부, Python과
  주요 패키지 버전을 `manifest.json`에 씁니다 (`storage/provenance.py:90`). `run_config.json`에는
  corpus 텍스트와 문서 id의 fingerprint를 넣어서, 같은 tag라도 데이터가 달랐는지 알 수 있습니다
  (`pipeline/run.py:200`). fingerprint는 각 텍스트 앞에 길이를 넣어 경계가 모호해지지 않게 합니다.
- **기존 로그를 덮어쓰지 않고 timestamp를 붙여 옮깁니다** (`runtime/factories.py`의
  `LaunchTask.run`).
- **산출물 형식이 문서화되어 있습니다.** `docs/ARTIFACTS.md`가 파일마다 내용과 필드 이름을 표로
  설명합니다.
- **상태 파일에 schema version을 넣습니다.** `"schema_version": 1`(run config), `2`(manifest),
  `STATE_VERSION = 3`(memory key state). 읽을 때 버전이 다르면 거부합니다
  (`adapters/longmem/adapter/key_state.py`).
- pickle을 쓰지 않아도 되는 곳에서는 `np.load(path, allow_pickle=False)`로 엽니다.

### 규칙

1. 산출물은 같은 디렉터리의 임시 파일에 쓴 뒤 `os.replace`로 교체합니다.
2. 디렉터리 산출물은 staging에서 완성한 뒤 rename으로 게시하고, 실패하면 이전 것을 복원합니다.
3. 같은 산출물을 여러 프로세스가 쓸 수 있으면 non-blocking 파일 lock으로 막습니다.
4. 사용자 입력으로 정해지는 경로는 symlink와 디렉터리 탈출을 검사합니다.
5. 오래 걸리는 다단계 작업은 stage별 산출물 해시를 기록해서 재개할 때 검증하고, 실행 identity가
   다르면 재개를 거부합니다.
6. 실험 실행마다 코드, 설정, 데이터 fingerprint, 패키지 버전을 산출물 옆에 남깁니다.
7. 저장 형식에는 version을 넣고, 형식은 문서에 표로 적습니다.

---

## 11. 재현성과 결정성

### 관찰

- **전역 `random`을 쓰지 않고 지역 RNG를 seed와 함께 만듭니다.**
  `random.Random(f"{self.settings.seed}:{ctx.round_state.round}")`
  (`pipeline/strategies/signals.py:157`). round마다 다른 seed를 문자열로 조합하므로 round 순서가
  바뀌거나 일부만 다시 돌려도 결과가 같습니다.
- **정렬은 stable로 합니다.** `np.argsort(..., kind="stable")`, `torch.sort(..., stable=True)`.
- **glob, dict, set을 순회할 때 정렬합니다.** `sorted(glob.glob(...))`, `sorted(diagnoses)`,
  `sorted(candidates)`.
- **순서를 보존하는 중복 제거에 `dict.fromkeys`** 를 씁니다 (`index/dense.py`,
  `validation/base.py`, `validation/specificity.py`).
- **동점 처리를 명시합니다.** nDCG 계산은 `argpartition`으로 빠르게 고르되, 선택된 값에 동점이
  있으면 전체 `argsort`로 다시 계산합니다 (`evaluation/metrics.py:29`).
- **길이순 정렬로 batch를 만들고 역순열로 원래 순서를 복원합니다.**

  ```python
  order = np.argsort(np.fromiter((len(k) for k in keys), np.int64, len(keys)), kind="stable")
  inverse = np.empty(len(order), np.int64)
  inverse[order] = np.arange(len(order))
  ...
  return np.concatenate(batches)[inverse], started
  ```
  (`adapters/browsecomp/pipeline/encode_keys.py:76`. `encoding/encoders.py:106`도 같습니다.)

- **길이가 반드시 같아야 하는 곳에서는 `zip(..., strict=True)`** 로 짧은 쪽에 맞춰 조용히 잘리는
  일을 막습니다 (`runtime/runner.py:58`, `build_bm25_index.py:28`, `agent/ours_agent_common.py:27`).
  길이가 달라도 되는 곳은 `strict=False`를 명시하기도 하지만, 일반 `zip()`도 많이 섞여 있어서 레포
  전체에 일관된 규칙은 아닙니다.

### 규칙

1. 난수는 `random.Random(seed)` 같은 지역 RNG로 만들고, 단계별 seed는 문자열 조합으로 파생합니다.
2. 결과 순서에 영향을 주는 정렬은 stable 정렬을 쓰고, 파일 목록과 dict·set은 정렬해서 순회합니다.
3. 순서를 지키는 중복 제거는 `dict.fromkeys`를 씁니다.
4. 길이가 같아야 하는 시퀀스를 묶을 때는 `zip(strict=True)`를 씁니다.

---

## 12. 동시성

### 관찰

- **읽기 lease와 쓰기 mutation을 구분하는 lock을 직접 만듭니다.** `SnapshotLock.readonly()`는
  thread별 lease 수를 세고, `mutation()`은 lease가 모두 끝날 때까지 기다립니다. lease를 가진 thread가
  mutation을 시도하면 deadlock 대신 즉시 `RuntimeError`를 냅니다 (`index/contracts.py:7`).
- **snapshot은 한 번에 하나만 활성화합니다.** `self._entry.acquire(blocking=False)`가 실패하면
  "snapshot lease is already active"로 실패합니다. 활성 상태가 아닐 때 view 메서드를 부르면
  `_active()`가 실패시킵니다 (`retrieval/snapshots.py`).
- **HTTP client는 thread-local로 하나씩 만들고, 만든 것은 목록에 모아 나중에 모두 닫습니다**
  (`llm/client.py`의 `_Sender._client`, `close`).
- **공유 카운터는 lock 안에서만 갱신합니다** (`_Sender._record_usage`, `LLM._add_usage`).
- **`ThreadPoolExecutor.map`으로 입력 순서를 유지한 채 병렬 호출합니다.** worker 수는
  `min(replica 수 × replica당 요청 수, 요청 수)`로 정합니다 (`llm/client.py`의 `send`).
- **replica 중 처리 중 요청이 가장 적은 곳으로 보냅니다** (`agent/oss_client_ours.py`의
  `_LeastLoadedClient`).
- 비동기 코드에서 호출 단위 누적값은 `contextvars.ContextVar`로 넘깁니다
  (`agent/gemini_client_ours.py`).
- GPU 작업은 `ThreadPoolExecutor(max_workers=1)`로 한 줄로 세워 실행합니다
  (`agent/searchers_ours.py`의 `DenseSearcher`).

### 규칙

1. 읽기와 쓰기가 섞이는 공유 구조는 "읽기 lease / 쓰기 mutation" 두 모드를 가진 lock으로 보호하고,
   deadlock이 될 조합은 즉시 예외로 막습니다.
2. thread마다 필요한 client는 thread-local로 만들고, 생성한 것을 추적해서 반드시 닫습니다.
3. 공유 카운터와 집계는 lock 안에서만 바꿉니다.
4. 순서가 중요한 병렬 호출은 `executor.map`으로 결과 순서를 입력 순서에 맞춥니다.

---

## 13. 수치·텐서 코드

### 관찰

- **메모리 예산을 상수로 두고 chunk 크기를 계산합니다.**

  ```python
  SCORE_MEMORY_BYTES = 2 << 30
  SCORE_ELEMENT_BYTES = np.dtype(np.float32).itemsize
  MIN_CHUNK_KEYS = 64
  MAX_CHUNK_KEYS = 8192

  def _chunk_size(n_docs):
      capacity = SCORE_MEMORY_BYTES // (SCORE_ELEMENT_BYTES * max(n_docs, 1))
      return max(MIN_CHUNK_KEYS, min(MAX_CHUNK_KEYS, capacity))
  ```
  (`src/selfindex/validation/validator.py:21`). encode 쪽은 "batch당 token 예산"으로 길이가 다른
  key들을 묶습니다 (`encode_keys.py:25`의 `encoding_spans`).
- **버퍼를 미리 크게 잡고 필요할 때 늘립니다.** `_grow_shard`는 필요한 크기의 절반만큼 여유를 두되,
  여유가 `MAX_GROWTH_BYTES`를 넘지 않게 합니다 (`index/dense.py:190`).
- **문서별 최댓값 집계는 `scatter_reduce_(..., reduce="amax")`** 로 한 번에 합니다
  (`common/fusion.py`, `index/dense.py`, `retrieval/lexical.py`).
- **정밀도 경계를 상수로 다룹니다.** token 집합 교집합 계산에서 집합 크기가 fp16이 정확히 표현하는
  정수 범위(`FP16_EXACT_INTEGER_LIMIT = 2048`)를 넘으면 float32로 바꿉니다
  (`pipeline/exploration/dissimilarity.py`).
- **GPU 경로와 CPU 경로를 같은 판정 규칙으로 둘 다 둡니다.** `dissimilar_mask`는 CUDA면 텐서
  구현, 아니면 prefix-filter 기반 scan 구현을 씁니다 (`pipeline/exploration/dissimilarity.py:142`).
  두 구현 모두 "이미 쓴 query나 앞서 수락한 후보와 Jaccard가 τ 이상이면 버리고, 앞에서부터 차례로
  수락한다"는 같은 규칙을 따릅니다. 두 경로의 결과가 같은지 비교하는 테스트는 레포에 없습니다.
- **큰 중간 텐서는 쓰고 나서 `del`** 합니다.
- **추론은 `torch.no_grad()` 안에서**, device가 CPU면 autocast를 끕니다
  (`torch.amp.autocast("cuda", enabled=device != "cpu")`).
- **NaN을 조용히 넘기지 않습니다.** encoder 출력에 NaN 행이 있으면 0으로 바꾸고 몇 행인지 출력합니다
  (`encode_keys.py`의 `_zero_nan_rows`). 다른 경로에서는 non-finite 값이면 예외를 냅니다.
- **id 공간을 부호로 나눕니다.** 원문 문서는 `-(doc + 1)`, 생성 key는 `shard * KID_STRIDE + row`로
  표현해서 한 정수 배열에 섞어 담습니다 (`index/dense.py`, `retrieval/snapshots.py`).
  `KID_STRIDE = 1 << 40`처럼 경계를 상수로 둡니다.

### 규칙

1. GPU 메모리를 쓰는 루프는 byte 예산 상수에서 chunk 크기를 계산하고, 하한과 상한을 둡니다.
2. 반복해서 늘어나는 텐서는 여유 용량을 두고 키우되, 한 번에 늘리는 양에 상한을 둡니다.
3. 집계는 Python 루프 대신 `scatter_reduce_`, `bincount` 같은 벡터 연산으로 합니다.
4. 결과에 NaN이나 inf가 섞일 수 있는 경로는 검사하고, 보정한다면 보정한 사실을 출력합니다.
5. 같은 기능의 GPU 경로와 CPU 경로를 둘 때는 같은 결과를 내도록 맞춥니다.

---

## 14. 외부 코드 통합 (adapter)

### 관찰

- **upstream을 고치지 않고 실행 중에만 속성을 바꿉니다.** 바꾼 속성은 원래 값으로, 원래 없던
  속성은 삭제로 되돌립니다.

  ```python
  _MISSING = object()

  @contextmanager
  def patched_attributes(*bindings):
      def restore(target, name, original):
          if original is _MISSING:
              delattr(target, name)
          else:
              setattr(target, name, original)

      with ExitStack() as stack:
          for target, name, replacement in bindings:
              original = getattr(target, name, _MISSING)
              setattr(target, name, replacement)
              stack.callback(restore, target, name, original)
          yield
  ```
  (`adapters/browsecomp/adapters/compatibility.py:7`)

- **upstream의 전제가 바뀌면 실행하지 않고 실패합니다.** judge evaluator를 불러올 때 upstream
  스크립트를 AST로 읽어 `from vllm import LLM, SamplingParams` import가 정확히 하나 있는지 확인하고,
  다르면 "upstream evaluator inference contract changed; review the adapter"로 멈춥니다. 확인이
  끝나면 그 import만 지우고 원격 judge 구현을 주입해서 실행합니다 (`adapters/judging.py:72`).
- **upstream 설정을 읽어 값을 맞춥니다.** 여러 memory system 설정이 같은 값을 쓰는지 확인하고,
  다르면 실패합니다 (`adapters/longmem/adapter/corpus.py:10`의 `_shared_parameters`). 값을 복사해서
  하드코딩하지 않습니다.
- **upstream 클래스는 mixin으로 확장합니다.** `SelfIndexMixin`이 `insert`, `_save_backend`,
  `_load_backend`, `_search_entries`를 감싸고 `super()`를 부릅니다. 저장된 key와 요청한 key가
  다르면 섞지 않고 실패합니다 (`adapters/longmem/adapter/memory_ours.py:17`).
- **응답 객체를 고치지 않고 proxy로 감쌉니다.** `_SafeResp`는 `__getattr__`로 모든 속성을 원본에
  넘기고 `model_dump`만 정리된 결과를 돌려줍니다 (`agent/gemini_client_ours.py:109`).
- 별도 프로세스로 실행할 단계는 `subprocess_argv(name, args)`로 `run.py exec <name>`을 다시
  부릅니다. 어떤 진입점이든 같은 import 경로와 같은 명령 표를 거칩니다
  (`runtime/commands.py:72`).

### 규칙

1. 외부 코드는 수정하지 않고, 바꿔야 하는 동작은 복원이 보장되는 context manager 안에서만 바꿉니다.
2. adapter가 기대는 upstream의 전제(import, 함수 이름, 설정 키)는 실행 전에 검사하고, 다르면
   실패시킵니다.
3. upstream 설정 값은 복사하지 않고 실행 시점에 읽습니다. 여러 곳의 값이 같아야 하면 같은지 확인합니다.
4. upstream 클래스 확장은 mixin과 `super()` 호출로 하고, 원래 동작을 대체하지 않고 앞뒤에 덧붙입니다.

---

## 15. LLM 호출 코드

### 관찰

- **prompt는 모듈 상수입니다.** 공통 조각(`SUPPORT`, `SCALE`, `_REVISION_INPUTS`)을 따로 두고 문자열
  연결로 조립합니다 (`common/judge_prompts.py`, `common/optimizer_prompts.py`). `.format()`에 쓸
  JSON 예시의 중괄호는 `{{ }}`로 escape합니다.
- **문서를 prompt에 넣을 때 `<<<DOC START>>> ... <<<DOC END>>>`** 같은 명확한 경계 표지로 감쌉니다.
- **작업마다 temperature와 max_tokens를 상수로 둡니다.** `DIAGNOSIS_TEMPERATURE = 0.5`,
  `FAITHFULNESS_TEMPERATURE = 0.3`, `DIAGNOSIS_TOKENS = 1200`.
- **max_tokens를 입력 크기에서 계산합니다.**
  `FAITHFULNESS_TOKEN_OVERHEAD + FAITHFULNESS_TOKENS_PER_KEY * len(proposals[doc])`,
  `REVISION_TOKENS + KEY_TOKENS * room` (`pipeline/optimizer.py`). job마다 다른 값은 `per_job`
  인자로 넘깁니다.
- **호출은 batch 단위입니다.** `llm.batch(list_of_messages, ...)`가 모든 요청을 병렬로 보내고 입력
  순서대로 결과를 돌려줍니다. 호출하는 쪽은 `zip(docs, raws)`로 짝을 맞춥니다.
- **LLM 출력 파싱은 실패를 예외로 만들지 않고 빈 결과로 만듭니다.** `extract_obj`는 dict가 아니면
  `{}`, `extract_list`는 list가 아니면 `[]`를 돌려줍니다 (`common/parsing.py`). `extract_json`은
  `</think>` 앞부분과 code fence를 벗기고, 실패하면 괄호 범위 찾기와 닫는 괄호 덧붙이기를 순서대로
  시도합니다 (`common/json_response.py`). 결과 문자열에서 surrogate 문자도 지웁니다.
- **점수 응답은 정규식으로 줄 단위 파싱하고 범위를 검사합니다.**
  `_SCORE_LINE = re.compile(r"\s*\[?(\d+)\]?\s*:.*=>\s*([0-3])")`, 그리고 `0 <= index < n`
  (`pipeline/generation/faithfulness.py`).
- **모델별 차이는 backbone 클래스로 흡수합니다.** reasoning effort, `extra_body`, 응답 텍스트
  추출 방법을 class attribute와 `text()` override로 바꿉니다 (`llm/backbones.py`). 요청 본문을 만드는
  코드는 하나뿐입니다.
- **토큰 사용량을 집계해서 round log에 남깁니다** (`LLM.tok`, `engine.py`의 `_usage_record`).
- 요청 전에 문자열을 UTF-8로 인코딩할 수 있게 정리합니다 (`llm/client.py`의 `_clean_messages`).
- LLM이 판정하는 단계(answerability, faithfulness)와 점수로 판정하는 단계(specificity,
  separation)를 분리하고, 각 단계에서 몇 개가 떨어졌는지 counter로 셉니다
  (`faithfulness_dropped`, `specificity_dropped`, `separation_dropped`).

### 규칙

1. prompt는 로직 밖의 상수로 두고, 공통 조각은 한 번만 정의해서 조립합니다.
2. 작업별 sampling 설정은 이름 있는 상수로 두고, 출력 길이 상한은 입력 크기에서 계산합니다.
3. LLM 출력 파싱은 형식이 틀려도 프로세스를 멈추지 않고 빈 결과를 돌려주며, 그렇게 버려진 건수를
   집계합니다.
4. 모델별 요청 차이는 backbone 하위 클래스로만 표현하고, 요청 본문 생성 코드는 하나로 유지합니다.
5. 판정 단계마다 통과·탈락 건수를 counter로 남깁니다.

---

## 16. CLI

### 관찰

- 인자 정의를 `_add_experiment_options`, `_add_execution_options`, `_add_subcommands`로 나눕니다.
- `choices`를 registry에서 만듭니다. `choices=sorted(RETRIEVERS)`, `choices=agent_names()`.
  새 구현을 등록하면 CLI 선택지도 자동으로 늘어납니다.
- help 문자열에 기본값과 출처를 씁니다. `"optimizer LLM base URL (OpenAI-compatible; default: LLM_BASE_URL)"`,
  `"run tag (default: derived from the configuration)"`.
- 서로 맞지 않는 옵션 조합을 명시적으로 거부합니다. subcommand 앞에 experiment 옵션을 쓰면
  `parser.error`로 알려 줍니다 (`run.py:121`). benchmark마다 `validate_spec`이 쓸 수 없는 옵션을
  거부합니다 (`--agent-model`은 BrowseComp 평가에서만 등).
- `list` 명령이 등록된 benchmark, retriever, agent, 명령 이름을 모두 출력합니다.
- 모든 진입점은 `raise SystemExit(main())`으로 끝나고, `main`은 정수 exit code를 돌려줍니다.
- 쉘 스크립트(`setup.sh`)는 `set -euo pipefail`, 모르는 옵션은 exit 2, `--help` 지원, 스크립트
  위치로 `cd`한 뒤 실행합니다.

### 규칙

1. CLI 선택지는 registry에서 만들어 코드와 CLI가 어긋나지 않게 합니다.
2. help에 기본값과 그 기본값이 어디서 오는지 적습니다.
3. 함께 쓸 수 없는 옵션 조합은 실행 전에 이유와 함께 거부합니다.
4. 등록된 구성요소를 나열하는 `list` 명령을 둡니다.
5. 쉘 스크립트는 `set -euo pipefail`로 시작하고 자기 위치 기준으로 동작합니다.

---

## 17. 로그 출력

### 관찰

- `logging` 대신 `print(..., flush=True)`를 씁니다 (62곳). 출력은 대부분 subprocess의 log 파일로
  redirect되므로, `flush=True`로 버퍼링 때문에 로그가 늦게 보이는 일을 막습니다.
- 모든 줄이 `[구성요소]` prefix로 시작합니다. `[0]`(준비), `[round N]`, `[optimizer]`, `[explore]`,
  `[demand]`, `[EVAL]`, `[bm25]`, `[enc]`, `[deadline]`, `[gpt-oss]` 등입니다. `grep '\[EVAL\]'` 한
  번으로 점수 줄을 찾을 수 있고, README가 그 줄을 결과 위치로 안내합니다.
- 큰 수는 `{:,}`, 비율은 `{:.0%}`, 차이는 `{:+.2f}`로 씁니다. 한 줄 요약의 항목 구분은 `·` 또는
  `|`입니다.
- 장시간 실행 stdout에는 줄 앞에 시각을 붙이는 writer를 끼웁니다 (`pipeline/run.py:31`의
  `_TsWriter`). 이미 설치돼 있으면 다시 감싸지 않습니다.
- 사람이 읽는 로그와 별개로, 같은 수치를 `round_log.json`, `summary.json`, `per_query.json` 같은
  구조화된 파일로 남깁니다.
- 오류가 나면 로그 파일 위치를 메시지에 넣습니다. `f"... judge failed (exit {returncode}); see {log_path}"`.

### 규칙

1. 로그 줄은 `[구성요소]` prefix로 시작하고, 핵심 결과 줄은 grep으로 바로 찾을 수 있는 고정
   prefix를 씁니다.
2. 파일로 redirect되는 출력은 즉시 flush합니다.
3. 사람이 읽는 로그와 같은 수치를 기계가 읽는 JSON으로도 남깁니다.
4. 실패 메시지에는 자세한 내용을 볼 수 있는 로그 경로를 넣습니다.

---

## 18. 도구와 의존성

### 관찰

- `pyproject.toml`
  - black 26.5.1, `line-length = 88`, `skip-magic-trailing-comma = true`, `target-version = ["py312"]`.
    trailing comma가 있어도 한 줄에 들어가면 접습니다.
  - pylint는 `E`, `F`(오류와 치명적 문제)만 켭니다. 스타일 경고로 소음을 만들지 않습니다.
  - vulture(죽은 코드), radon(복잡도)을 dev 의존성으로 둡니다.
  - 모든 도구에서 `externals/`를 제외합니다.
- 의존성 버전은 `==`로 정확히 고정하고 `uv.lock`도 커밋합니다. git 의존성은 commit hash로
  고정합니다.
- 선택 기능은 optional dependency group으로 나눕니다 (`.[longmem]`, `.[browsecomp]`).
- Python 3.12 기능을 적극적으로 씁니다. 괄호로 묶은 여러 context manager(`with (a, b):`),
  `Path.is_relative_to`, `zip(strict=)`, `functools.cache`, `int | None` 표기.
- `repo.check` 명령이 설치 직후 저장소 상태를 점검합니다. 해결 안 된 merge conflict, 저장소 밖을
  가리키는 symlink, 소스로 추적되는 생성물(`.pyc`, `.npz` 등), 소스 안에 박힌 checkout 절대 경로를
  찾아냅니다 (`runtime/repository_check.py`).
- `.gitignore`는 `.env.*`를 무시하되 `!.env.example`로 예시 파일만 추적합니다.
- 레포에 테스트 디렉터리나 테스트 파일은 없습니다. 검증은 실행 중의 입력 검사, 출력 완전성 검사,
  `repo.check`가 맡습니다.

### 규칙

1. formatter와 linter 버전을 고정하고, linter는 실제 오류만 잡도록 좁게 켭니다.
2. 런타임 의존성은 정확한 버전으로 고정하고 lock 파일을 커밋합니다.
3. 저장소 무결성(충돌 표지, 생성물, 절대 경로)을 검사하는 명령을 두고 setup에서 실행합니다.
4. 환경 변수 예시는 `.env.example`로 추적하고 실제 `.env`는 무시합니다.

---

## 19. 문서화 방식

### 관찰

- 코드 안에는 docstring도 주석도 없습니다. 의미는 이름, 짧은 함수, 타입이 드러나는 dataclass,
  오류 메시지가 전달합니다.
- 대신 저장소 문서가 역할을 나눠 맡습니다.
  - `README.md`: 설치, 서비스 환경 변수 표, 실행 예시, 파라미터 표, 확장 방법(등록 함수 목록과
    backbone 하위 클래스 예시), 디렉터리 구조.
  - `docs/REPRODUCING.md`: 보고된 수치를 재현하는 정확한 명령.
  - `docs/ARTIFACTS.md`: 산출물 파일별 내용과 필드.
  - `externals/README.md`: submodule 출처, commit, license.
  - `.env.example`: 환경 변수마다 한 줄 설명.
- README의 표가 코드의 dict와 1:1로 대응합니다(`PARAMETERS`, `*_BASE_URL`, `DEVICES`).

### 규칙

1. 사용자가 알아야 하는 것(설치, 환경 변수, 파라미터, 산출물 형식, 확장 방법, 재현 명령)은 저장소
   문서에 표로 적습니다.
2. 코드의 설정 dict와 문서의 표는 같은 변경에서 함께 고칩니다.
3. 코드 안 문서화 방식은 21절의 결정에 따릅니다.

---

## 20. 이 레포에서 따라 하지 않을 부분

전부 읽어 보면 일관성이 매우 높지만, 아래는 규약으로 옮기지 않는 것이 맞다고 판단한 지점입니다.

1. **예외를 삼키는 곳이 있습니다.**
   - `common/json_response.py:43`, `:48` — `except Exception: pass` / `continue`. 파싱 시도 단계라
     의도는 이해되지만, 빈 처리는 남기지 않습니다.
   - `adapters/browsecomp/costs/usage.py:50` — 읽을 수 없는 run 파일을 `continue`로 건너뛰어서,
     비용 합계가 조용히 작아질 수 있습니다.
   - `llm/client.py:55` — 일시 오류로 재시도를 모두 실패하면 아무 기록 없이 `None`을 돌려줍니다.
     실패 건수를 세지 않으므로, 몇 건이 LLM 실패로 빠졌는지 로그에서 알 수 없습니다.
   - `data/corpora.py:34`, `encoding/encoders.py:51`, `agent/oss_client_ours.py:43` — 넓은
     `except Exception`으로 기본값을 돌려줍니다.
2. **같은 값의 상수가 여러 곳에 흩어져 있습니다.** 문서 clip 길이 2400이 `settings.py`의
   `DOCUMENT_CLIP_CHARS`, `optimizer.py:20`의 `DOCUMENT_CHARS`, `filters.py:29`의 `DOCUMENT_CHARS`,
   `signals.py:38`의 `DOCUMENT_PROMPT_CHARS`로 네 번 정의되어 있습니다. 한 곳만 바꾸면 단계마다
   다른 길이를 보게 됩니다. 같은 뜻의 상수는 한 곳에 둡니다.
3. **상수를 사용처보다 아래에 정의한 곳이 있습니다** (`pipeline/exploration/filters.py`의
   `DOCUMENT_CHARS`, `ANSWERABILITY_TOKENS`가 `answerable` 함수 아래에 있음). 실행에는 문제없지만
   읽는 순서가 어색합니다. 상수는 import 바로 아래에 둡니다.
4. **같은 prompt 본문이 두 번 있습니다.** `pipeline/generation/prompts.py`의 `_PASSAGE_PROMPT`와
   `common/optimizer_prompts.py`의 `TASK_PASSAGES` 앞부분이 경계 표지(`DOC_START` / `DOC START`)만
   다르고 같습니다. 공통 조각으로 한 번만 정의합니다.
5. **논문 맥락이 이름에 남아 있습니다.** `_in_table7(form, shape)`(`common/optimizer_prompts.py:160`)는
   논문의 표 번호를 이름으로 썼습니다. 이름은 하는 일(예: `revision_prompt`)로 짓습니다.
6. **데이터를 자르는 곳이 있습니다.** `response.text[:500]`(`llm/client.py:65`), subprocess
   stdout/stderr의 끝 1500/2000자(`build_bm25_index.py`), prompt에 넣는 문서의 앞 2400자. prompt
   길이 제한은 알고리즘의 일부지만, 오류 메시지와 로그를 자르는 것은 기존 작업 원칙("데이터를 임의로
   자르지 않는다")과 맞지 않습니다. 21절에서 결정이 필요합니다.
7. **`__init__`에서 만들지 않은 속성을 `getattr(self, "_x", None)`으로 지연 생성합니다**
   (`selectors.py:49`, `signals.py:189`, `agent/backbones.py:206`). 객체가 가질 수 있는 속성을
   `__init__`만 보고 알 수 없게 됩니다. 속성은 `__init__`에서 `None`으로 초기화합니다.
8. **전역 가변 상태가 있습니다.** 선택된 encoder 설정을 모듈 전역 `_SELECTED`에 두고
   `use_encoder()`로 바꿉니다 (`runtime/platform/settings.py:44`). 한 프로세스에서 encoder를 하나만
   쓰는 전제에서만 안전합니다. 가능하면 설정을 인자로 넘깁니다.
9. **import 순서가 섞인 파일이 있습니다** (`adapters/browsecomp/agent/backbones.py`는 `selfindex`와
   `browsecomp` import가 번갈아 나옵니다). black은 import 순서를 정리하지 않으므로, isort 또는 ruff의
   import 정렬을 함께 켭니다.
10. **반환 타입 표기가 7%뿐입니다.** 이름이 서술적이어도 공개 함수의 인자와 반환 형태는 표기가
    있는 편이 낫습니다.

---

## 21. 기존 작업 원칙과 다른 지점 (결정이 필요합니다)

이 레포의 스타일과 `~/.claude/CLAUDE.md`의 코드 작성 규약이 정면으로 다른 부분입니다. 이 문서에서는
어느 쪽으로도 정하지 않았습니다.

| 항목 | 이 레포 | 기존 작업 원칙 |
|---|---|---|
| 파일 헤더 | 없음 | 파일 첫머리에 목적과 용도를 적음 |
| 함수 docstring | 0개 | 공개·비자명 함수마다 목적·인자·반환·실패 동작을 적음 |
| 본문 주석 | 0줄 | 논리 덩어리마다 목적 주석 한 문장 |
| 공개 함수 타입 표기 | 반환 타입 7% | 공개 함수 시그니처에 타입 명시 |
| 예외 처리 | 대부분 엄격하지만 일부 `except: pass`류 존재 | 에러를 삼키지 않음 |
| 데이터 절단 | 오류 메시지·로그 일부를 자름 | 임의 절단 금지, 상한이 필요하면 물어봄 |

제가 보기에는 다음처럼 합치는 방법이 자연스럽습니다. 다만 무엇을 따를지는 정해 주셔야 합니다.

- 1~16절의 구조·설계 규약(짧은 함수, registry, frozen dataclass, 원자적 쓰기, 재개 검증, 결정성,
  오류 메시지 형식)은 그대로 가져옵니다.
- 문서화(헤더, docstring, 본문 주석)와 타입 표기는 기존 작업 원칙을 유지합니다. 이 레포가 주석 없이도
  읽히는 것은 함수가 매우 짧고 이름이 서술적이기 때문이므로, 그 두 가지는 주석이 있더라도 그대로
  지킵니다.
- 예외 삼키기와 로그 절단은 20절에 적은 대로 따르지 않습니다.

---

## 부록: 빠르게 훑는 체크리스트

- [ ] 함수가 20줄을 넘으면 이름 붙일 수 있는 덩어리를 뺐는가
- [ ] `main`이 단계 함수들의 목차처럼 읽히는가
- [ ] 숫자 상수 이름에 단위가 있는가, 같은 값이 다른 곳에 또 정의되어 있지 않은가
- [ ] 바뀌지 않는 값은 frozen dataclass / NamedTuple / MappingProxyType인가
- [ ] 입력 검증이 생성 시점(`__post_init__`, `create`, `register_*`)에 있는가
- [ ] 오류 메시지가 요구 조건과 해결 방법, 선택지를 말하는가
- [ ] 외부 호출은 영구 오류와 일시 오류를 나눠 재시도하는가
- [ ] 바꾼 전역 상태(`sys.argv`, cwd, `sys.path`, 속성)를 `finally`로 복원하는가
- [ ] 산출물을 임시 파일 + `os.replace`로 쓰는가
- [ ] 재개 가능한 작업이 산출물 해시와 실행 identity를 검증하는가
- [ ] RNG가 지역 seed RNG이고, 정렬이 stable이고, 순회가 정렬되어 있는가
- [ ] 결과가 기대 집합을 정확히 덮는지, 수치가 유한한지 확인하는가
- [ ] 무거운 의존성은 쓰는 함수 안에서 import하는가
- [ ] LLM 출력 파싱이 실패해도 멈추지 않고, 버린 건수를 세는가
- [ ] 로그 줄에 `[구성요소]` prefix가 있고, 같은 수치가 JSON으로도 남는가
- [ ] 설정 dict와 README 표가 같은 내용인가
