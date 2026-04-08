# Quick Start

Get an AI assistant running in your Odoo instance in under 10 minutes.

Linkup AI Agent connects Odoo to a local Ollama LLM, an Anthropic Claude cloud LLM,
or both at once — giving you a VS Code-style side panel chat that can query your ERP data
using natural language. Complete Steps 1–4 below to finish your first conversation.

:::{warning}
Odoo 19.0 **Enterprise** 에디션이 필요합니다. Community 에디션에서는
`ai_app` 모듈이 제공되지 않아 설치 자체가 불가능합니다.
:::

## Prerequisites

Odoo 19.0 Enterprise
: 설치 및 실행 중인 인스턴스 (관리자 계정으로 로그인)

Ollama (로컬 LLM 사용 시)
: [Ollama 다운로드](https://ollama.com/download) 후 설치 및 실행

  ```bash
  # 운영 검증 모델 다운로드
  ollama pull qwen3.5:9b
  ```

Anthropic API 키 (Claude 사용 시)
: <https://console.anthropic.com/> 에서 발급

관리자 권한
: Settings 메뉴 접근이 가능한 계정

:::{tip}
Ollama와 Claude를 동시에 설정하여 에이전트별로 다른 Provider를 지정할 수 있습니다 (하이브리드 구성).
:::

## Step 1 — Install the Modules

1. **Apps** 메뉴로 이동합니다.
2. 검색창에 **"Linkup AI"** 를 입력합니다.
3. **Linkup AI Side Panel** (`lu_ai_ui`) 를 설치합니다.
   의존 모듈 (`lu_ai_ollama`, `ai`, `ai_app`, `web_enterprise`) 이 자동으로 함께 설치됩니다.
4. Claude도 사용하려면 **Linkup AI Claude** (`lu_ai_claude`) 를 추가로 설치합니다.

:::{tip}
**Linkup AI Side Panel** 하나만 설치해도 Ollama 연동에 필요한 모든 모듈이 자동으로 설치됩니다.
:::

```{image} /_static/img/ai-agent/qs-install-modules.png
:alt: Apps 목록에서 Linkup AI Side Panel과 Linkup AI Claude 표시
:width: 100%
```

## Step 2 — Configure Your LLM Provider

:::{note}
Ollama와 Claude 설정은 **서로 다른 Settings 페이지**에 있습니다.
두 Provider를 모두 설정하면 Step 3에서 에이전트별로 Provider를 선택할 수 있습니다.
:::

### Option A: Ollama (로컬 LLM)

1. **Settings → Integrations** 으로 이동합니다.
2. **"Use local Ollama models"** 토글을 활성화합니다.
3. URL 입력 필드(`http://localhost:11434` placeholder) 에 Ollama 서버 주소를 입력합니다.
   로컬 설치라면 기본값을 그대로 유지하세요.
4. (선택) API 키 입력 필드(`API Key (optional for local setup)` placeholder) —
   원격/인증 엔드포인트 사용 시에만 필요합니다. 로컬 설치에서는 비워둡니다.
5. **Save** 를 클릭합니다.

:::{note}
필드에 별도 라벨이 표시되지 않고 placeholder 텍스트만 보입니다. 위치를 확인하려면 아래 스크린샷을 참고하세요.
:::

```{image} /_static/img/ai-agent/qs-settings-ollama.png
:alt: Settings → Integrations — "Use local Ollama models" 섹션
:width: 100%
```

### Option B: Claude (클라우드 LLM)

1. **Settings → AI** 로 이동합니다 (Providers 섹션).
2. **"Use your own Anthropic Claude account"** 섹션을 찾아 API 키 입력 필드에 키를 입력합니다.
   키를 입력하면 설정이 자동으로 활성화됩니다.
3. (선택) **Max Output Tokens** — 기본값 16,384.
   Odoo UI에서는 최대 128,000 까지 입력할 수 있으나 실제 한도는 모델에 따라 다릅니다
   (Opus: 128k, Sonnet/Haiku: 64k). 모델 한도를 초과하면 API 레벨에서 자동 조정됩니다.
4. **Save** 를 클릭합니다.

:::{note}
설정 화면에 RAG/임베딩 관련 안내 문구가 표시될 수 있습니다.
이 기능은 Quick Start 범위 밖이며 [Configuration](configuration.md) 가이드에서 다룹니다.
:::

```{image} /_static/img/ai-agent/qs-settings-claude.png
:alt: Settings → AI — "Use your own Anthropic Claude account" 섹션
:width: 100%
```

:::{note}
고급 파라미터 튜닝 및 RAG(문서 검색) 설정은 [Configuration](configuration.md) 가이드를 참조하세요.
:::

## Step 3 — Create an AI Agent

1. **AI → Agents → Agents** 로 이동합니다 (칸반 뷰가 기본).
2. **Create** 를 클릭합니다.
3. 에이전트 이름을 입력합니다 (예: `Sales Assistant`).
4. **LLM Model** 드롭다운에서 모델을 선택합니다:
   - Ollama: `qwen3.5:9b` (운영 권장) 또는 `qwen3.5:35b` (고성능)
   - Claude: `Claude Sonnet 4.6` (균형) 또는 `Claude Opus 4.6` (최고 성능)
5. (선택) System Prompt, Topics 등 — Quick Start에서는 기본값을 유지합니다.
6. **Save** 를 클릭합니다.

:::{tip}
테스트용으로는 `qwen3.5:9b` (로컬, 무료) 또는 `Claude Haiku 4.5` (클라우드, 저비용) 를 추천합니다.
운영 환경에서는 `qwen3.5:35b` 또는 `Claude Sonnet 4.6` 이 도구 호출 정확도가 높습니다.
사용 가능한 모델 목록은 Provider 설정에 따라 자동으로 반영됩니다.
:::

```{image} /_static/img/ai-agent/qs-create-agent.png
:alt: AI → Agents → Agents — 에이전트 생성 폼 (LLM Model 선택)
:width: 100%
```

## Step 4 — Start Your First Chat

1. Odoo 상단 우측 **systray** 에서 **AI 버튼** 을 클릭합니다.
2. 화면 우측에 **사이드 패널** 이 열립니다 (보라색 헤더, 240–480 px, 리사이즈 가능).
3. 에이전트가 여러 개라면 헤더의 **에이전트 선택기** 에서 원하는 에이전트를 선택합니다.
4. **"+"** 버튼으로 새 대화를 시작합니다.
5. 하단 입력창에 메시지를 입력한 뒤 **Enter** 를 누릅니다.

AI Agent는 한국어와 영어를 모두 지원합니다:

- 예시 (full LLM tool-calling — ERP 데이터 조회):
  > *"Show me the top 5 products by revenue this month"*
- 예시 (shortcut — 즉각 응답):
  > *"이번 달 매출 총액은?"*

대화 이름은 첫 메시지를 기준으로 자동 지정됩니다.
이전 대화는 헤더의 **히스토리 버튼** 으로 확인할 수 있습니다 (최근 대화 최대 50개 표시).

:::{tip}
내장 shortcut 쿼리가 Sales, Finance, Inventory, HR, CRM 등 주요 도메인을 지원합니다.
자주 묻는 질문은 LLM을 거치지 않고 즉시 응답하여 속도가 빠릅니다.
:::

```{image} /_static/img/ai-agent/qs-first-chat.png
:alt: 사이드 패널 대화 예시
:width: 100%
```

## What You Just Set Up

:::{tip}
| 구성 요소 | 역할 |
|-----------|------|
| **Ollama** 또는 **Claude API** | LLM 추론 엔진 (로컬 또는 클라우드) |
| **`lu_ai_ollama`** / **`lu_ai_claude`** | Odoo ↔ LLM Provider 연동 |
| **`lu_ai_ui`** | VS Code 스타일 사이드 패널 채팅 UI |
| **AI Agent** | Provider · 모델 · 프롬프트를 묶는 설정 단위 |

하이브리드 구성에서는 에이전트별로 다른 Provider를 지정할 수 있어,
빠른 응답이 필요한 에이전트는 로컬 Ollama, 복잡한 분석은 Claude로 분리 운영이 가능합니다.
:::

## Troubleshooting

| 증상 | 원인 | 해결 |
|------|------|------|
| 모듈 설치 시 "Module not found: ai_app" | Community 에디션 사용 | Enterprise 에디션 필요 |
| "Connection refused" 또는 응답 없음 | Ollama 서버 미실행 | `ollama serve` 실행 확인, Base URL 확인 |
| "No API key set for Anthropic Claude" | Claude API 키 미설정 | **Settings → AI → Providers** 에서 키 입력 |
| "429 Too Many Requests" 또는 "Invalid API key" | Claude API 요율 초과 또는 키 오류 | 요율 한도 확인 (console.anthropic.com), 키 재발급 |
| 사이드 패널이 나타나지 않음 | 브라우저 캐시 | 하드 리프레시 (Ctrl+Shift+R) 후 재시도 |

## Next Steps

- **[Configuration](configuration.md)** — Ollama 파라미터 튜닝 (`num_ctx`, `num_predict`, `keep_alive`),
  Claude 토큰 한도, RAG 설정, 멀티모델 구성
- **Domain Routing** — 도메인별 에이전트 라우팅 (Sales, HR, Finance 등 자동 분기)
- **Workflows** — AI 기반 멀티스텝 자동화
- **Proactive Alerts** — 재고 부족, 미수금 초과 등 ERP 이상 징후 자동 감지 및 알림
