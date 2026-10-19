---
sidebar_position: 1
sidebar_label: "B1. ABC와 Protocol"
description: "interface와 구현을 다른 파일에 두고, 상속은 한두 단계에서 끝내는 방법입니다."
---

# ABC와 Protocol

interface와 구현을 다른 파일에 두고, 상속은 한두 단계에서 끝내는 방법입니다.

## 개념

- **ABC**는 "이 클래스를 상속하는 클래스는 이 메서드들을 반드시 가져야 한다"는 약속만 정하는 클래스입니다.
  미구현 abstract method가 남아 있으면 객체를 만들 수 없습니다.
- **abstract method**(`@abstractmethod`)는 그 약속에 들어가는 메서드입니다. 하나라도 구현하지 않은 하위 클래스로
  객체를 만들면 `TypeError`가 납니다.
- **Protocol**은 상속 없이 "이 메서드를 가지고 있으면 된다"만 정하는 interface입니다. 함수 하나나 외부
  client처럼 우리가 상속 구조를 강제할 수 없는 대상에 씁니다.

## 사용 방법

- ABC, Protocol, 구현들이 주고받는 데이터 타입은 `contracts.py` 또는 `base.py` 한 파일에 둡니다.
- 구현은 그 옆 파일에 하나씩 둡니다.
- 상속은 대부분 "interface, 구현" 두 단계에서 끝냅니다.
- 타입 표기에만 필요한 import는 `if TYPE_CHECKING:` 안에 둬서, interface 파일과 구현 파일이 서로 import하는
  순환을 만들지 않습니다.

## 왜 필요한가

새 구현을 추가하는 사람은 interface 파일 하나만 읽고 그 메서드들을 채우면 됩니다. 상속이 얕으면 어떤 메서드가
어디서 오는지 찾느라 여러 파일을 오가지 않아도 됩니다.

## 예시

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

## Self-Index에서의 사용

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

## 주의할 점

구현이 하나뿐이고 늘어날 계획도 없으면 interface를 따로 만들지 않습니다. 이 레포도 `PipelineEvaluation`,
`NDCGMetric`처럼 구현이 하나인 클래스에는 ABC를 두지 않았습니다.
