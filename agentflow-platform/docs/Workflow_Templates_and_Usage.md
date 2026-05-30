# 🚀 AgentFlow | Workflow Templates, Agents & Tokenomics

This document provides a comprehensive technical overview of AgentFlow's predefined workflow templates, the specialized agents powering them, and the underlying token/cost tracking architecture.

---

## 1. 🏗️ Workflow Templates

AgentFlow comes pre-configured with **5 production-ready workflow templates** designed for content creation, market analysis, media intelligence, and code performance auditing.

| Workflow Name | Primary Objective | Agents Involved |
| :--- | :--- | :--- |
| **AI Image Studio** | High-fidelity image generation with structured visual prompts. | Prompt Architect, Image Generator |
| **[TEMPLATE] Full Content Lifecycle** | End-to-end content creation from research to polished article to visual assets. | Deep Researcher, Creative Writer, Visual Director |
| **[TEMPLATE] Competitive SWAT Analysis** | Market intelligence gathering and strategic competitive analysis. | Market Analyst, Quant Strategist |
| **YouTube Insight Engine** | YouTube video transcript extraction and executive summary generation. | Media Scout, Briefing Expert |
| **Code Performance Audit** | Code review focusing on logical soundness, security, and performance. | Logic Auditor, Briefing Expert |

---

## 2. 🤖 Agent Roster & Specializations

AgentFlow features **10 specialized agents**, each with a distinct role, system prompt, and set of tools for orchestrating complex multi-step workflows.

### Visual & Design Agents

#### **Prompt Architect** (Visual Designer)
- **Role**: JSON Architect for Image Generation Models
- **Tools**: `[]` (none)
- **Purpose**: Analyzes content and generates structured JSON prompts optimized for image generation models. Outputs prompts with fields like `subject`, `style`, `lighting`, `composition`, and `mood`.

#### **Image Generator** (AI Artist)
- **Role**: High-Fidelity Visual Generation Specialist
- **Tools**: `[]` (none)
- **Purpose**: Takes structured JSON prompts and generates vivid, high-fidelity images using multimodal models. Handles image encoding and persistence.

#### **Visual Director** (Image Designer)
- **Role**: Lead Art Director
- **Tools**: `['calculator']`
- **Purpose**: Interprets written content and generates high-impact visual briefs. Ensures visual output aligns with narrative themes and brand guidelines.

### Research & Analysis Agents

#### **Deep Researcher** (Data Gatherer)
- **Role**: Senior Technical Researcher
- **Tools**: `['web_search', 'url_scraper']`
- **Purpose**: Gathers deep technical facts, statistics, and current trends on any topic using web search and URL scraping. Focuses on credible sources and quantifiable data.

#### **Market Analyst** (Competitive Scout)
- **Role**: Competitive Intelligence Analyst
- **Tools**: `['url_scraper', 'web_search']`
- **Purpose**: Deconstructs competitor strategies by scraping websites and identifying market trends, pricing models, and feature differentiation.

#### **Quant Strategist** (Financial Modeler)
- **Role**: Quantitative Financial Analyst
- **Tools**: `['calculator', 'current_time_fetcher']`
- **Purpose**: Transforms market data into hard financial models, SWOT analyses, and strategic recommendations. Performs calculations and trend projections.

### Content & Communication Agents

#### **Creative Writer** (Storyteller)
- **Role**: Master Content Creator
- **Tools**: `['current_time_fetcher']`
- **Purpose**: Takes researched facts and crafts a single, ready-to-publish article. Focuses on narrative flow, engagement, and clarity.

#### **Media Scout** (Video Intelligence)
- **Role**: AI Video Intelligence Specialist
- **Tools**: `['youtube_transcript', 'url_scraper']`
- **Purpose**: Extracts transcripts from YouTube videos using the `youtube_transcript` tool. Automatically handles blocked or unavailable transcripts with fallback strategies.

#### **Briefing Expert** (Executive Assistant)
- **Role**: Executive Assistant & Summarization Expert
- **Tools**: `['current_time_fetcher']`
- **Purpose**: Condenses lengthy content into clear, actionable summaries. Extracts key takeaways and delivers insights in executive-friendly formats.

### Code & Quality Agents

#### **Logic Auditor** (Code Reviewer)
- **Role**: Principal Software Engineer & Security Auditor
- **Tools**: `['calculator']`
- **Purpose**: Analyzes code for logical soundness, security vulnerabilities (OWASP), efficiency, and clean code adherence. Provides detailed improvement recommendations.

---

## 3. 💰 Token Tracking & Cost Calculation

AgentFlow implements a precise, real-time telemetry system to monitor LLM usage and estimate operational costs across all agent executions.

### 3.1 Token Capture Mechanism (`runtime/gemini_llm.py`)

Token usage is captured **at the moment of execution** for every agent interaction:

#### **Primary Method: Native Metadata**
- The system reads `response.usage_metadata.total_token_count` directly from the Google Gemini SDK.
- This provides exact token consumption from the LLM provider.

#### **Fallback Method: Heuristic Estimation**
- If metadata is unavailable, usage is estimated using: `len(generated_text.split()) + 50`
- The `+ 50` padding accounts for system prompts and framework overhead.

#### **Multimodal Logic: Image Generation**
- Image generation (using `gemini-3.1-flash-image-preview` or similar) is assigned a **fixed cost of 1,000 tokens** per image.
- This reflects the higher computational overhead of visual generation compared to text.

### 3.2 Cost Calculation Formula (`frontend/src/pages/Monitor.jsx`)

The platform translates tokens into estimated USD using a fixed price multiplier:

**Formula:**
```
Estimated Cost (USD) = Total Tokens × $0.000002
```

**Price Constants:**
- **Price Multiplier**: `$0.000002` per token
- **Equivalent**: `$2.00` per 1,000,000 tokens
- **Reference**: Based on Google Gemini's text generation pricing tier

### 3.3 Persistence & Historical Tracking (`database.py`)

Total tokens for an entire workflow run are aggregated and stored in the `usage_tokens` column of the `runs` table:

| Column | Type | Purpose |
| :--- | :--- | :--- |
| `run_id` | TEXT | Unique identifier for the workflow execution |
| `workflow_id` | TEXT | Reference to the workflow executed |
| `status` | TEXT | Execution state (`running`, `completed`, `failed`) |
| `trigger_source` | TEXT | Execution source (`manual` from Web UI or `telegram` from bot) |
| `result` | TEXT | Final polished output from the last agent in the graph |
| `usage_tokens` | INTEGER | **Total tokens consumed across all agents** |
| `created_at` | TIMESTAMP | ISO timestamp of execution |

### 3.4 Real-Time Cost Monitoring

The **Monitor** page displays live cost tracking:
- **Live Token Count**: Updated as agents execute and consume tokens
- **Estimated Cost**: Real-time USD estimate calculated using the multiplier above
- **Run History**: Historical cost analysis for all completed executions

---

## 4. 🔧 Tools Available in the Ecosystem

AgentFlow provides the following tools that agents can invoke during execution:

| Tool Name | Purpose | Used By |
| :--- | :--- | :--- |
| `web_search` | Google Search grounding for factual data retrieval | Deep Researcher, Market Analyst |
| `url_scraper` | Website content extraction and parsing | Deep Researcher, Market Analyst, Media Scout |
| `youtube_transcript` | YouTube video transcript extraction | Media Scout |
| `current_time_fetcher` | Fetches current date/time for context | Creative Writer, Quant Strategist, Briefing Expert |
| `calculator` | Mathematical computations and financial modeling | Visual Director, Quant Strategist, Logic Auditor |

---

## 5. 📊 Workflow Execution Model

All workflows operate on **LangGraph**, a directed acyclic graph (DAG) architecture where:

1. **Sequential Execution**: Agents execute in order, with output from Agent N becoming input for Agent N+1.
2. **State Management**: An `AgentState` object maintains context and message history across all agents.
3. **Tool Invocation**: Each agent can call assigned tools during execution, with results automatically injected into the prompt.
4. **Token Aggregation**: Token usage from each agent is summed into the workflow's `usage_tokens` total.
5. **Result Finalization**: The output from the last agent is stored as the `result` field in the run record.

---

## 6. 💡 Key Design Decisions

### Multimodal Cost Assignment
Image generation tasks are assigned a flat 1,000-token cost to simplify cost tracking while reflecting the compute intensity. This prevents massive byte strings from inflating token counts and keeps billing predictable.

### Heuristic Fallback
The fallback estimation (`len().split() + 50`) ensures that even if the LLM SDK fails to return metadata, cost tracking never goes blind. This provides visibility into API failures.

### Real-Time Telemetry
WebSocket broadcasts from the backend ensure that the frontend's Monitor page reflects live execution progress and cost accumulation without polling delays.

---

*Last Updated: May 30, 2026*
*Database Version: AgentFlow v0.1.0*
