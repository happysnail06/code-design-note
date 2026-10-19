---
sidebar_position: 1
sidebar_label: "A1. Adapter와 upstream"
description: "외부 서비스, 외부 라이브러리, 다른 저장소의 코드와 닿는 부분을 adapter 한 곳에 모으고, 가져온 외부 코드는 고치지 않는 방법입니다."
---

# Adapter와 upstream

외부 서비스, 외부 라이브러리, 다른 저장소의 코드와 닿는 부분을 adapter 한 곳에 모으고, 가져온 외부 코드는
고치지 않는 방법입니다.

## 개념

- **adapter**는 외부 코드를 부르고, 그 입출력을 우리 코드의 형식으로 바꿔 주는 코드입니다. 우리 코드는
  adapter가 돌려준 값만 보고, 외부 코드가 어떻게 생겼는지는 알 필요가 없습니다.
- **upstream**은 우리가 가져다 쓰는 다른 저장소의 원본 코드입니다. Self-Index에서는 BrowseComp, LongMemEval
  같은 benchmark 저장소가 upstream입니다.

## 사용 방법

- 패키지는 하는 일(실행, 알고리즘, index, 검색, 저장)로 나눕니다.
- 외부와 닿는 코드는 `adapters/`에, 외부 코드 자체는 `externals/`에 따로 둡니다.
- upstream은 git submodule로 commit을 고정하고 고치지 않습니다. upstream의 동작을 바꿔야 하면 adapter에서
  처리합니다([B4](../b-code-structure/b4-mixin.md), [B5](../b-code-structure/b5-proxy.md), [C7](../c-language-features/c7-context-manager.md)).

## 왜 필요한가

알고리즘만 고치는 사람은 `adapters/`를 몰라도 되고, benchmark 연결만 고치는 사람은 알고리즘을 몰라도 됩니다.
upstream이 바뀌어도 고칠 곳이 `adapters/` 안에서 끝납니다.

## 예시

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

## Self-Index에서의 사용

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

## 주의할 점

외부 연동이 하나뿐인 작은 프로젝트에서는 최상위 디렉터리까지 나눌 필요가 없습니다. 연동 코드를 모듈 하나에
모으면 충분합니다.
