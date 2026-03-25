# Dify 공식 도구 카탈로그

> Dify v1.0+ 기준. 모든 도구는 플러그인 방식으로 마켓플레이스에서 설치 후 사용.
> 소스: https://github.com/langgenius/dify-official-plugins/tree/main/tools
> 최종 갱신: 2026-03-25

---

## 사용법

이 카탈로그는 다음 단계에서 참조한다:
- **DSL 생성(STEP 2)**: 더미 code 노드 작성 시 실제 도구의 입출력 형식 참고
- **개발계획(STEP 4)**: Python 구현 시 대응하는 Dify 플러그인/API 매핑 참고
- 시나리오(STEP 1)에서는 직접 참조하지 않음 (추상 기능 수준으로 수집)

---

## 도구 선별 기준

### 1순위: ★ 기본 추천 도구 사용

각 카테고리 표에서 **★ 표시가 기본 추천 도구**이다.
★는 아래 5가지 기준을 종합 평가하여 사전 선정한 결과이므로, 특별한 사유가 없으면 ★ 도구를 그대로 추천한다.
복수 ★인 경우 용도가 서로 다른 것이므로 둘 다 제시한다.

| 평가 기준 | 설명 |
|-----------|------|
| **범용성** | 특정 벤더/지역에 종속되지 않고 글로벌하게 사용 가능한 도구 우선 |
| **진입 장벽** | API 키 불필요 또는 무료 티어가 있는 도구 우선 |
| **한국어 지원** | 한국어 입출력을 지원하는 도구 우선 |
| **생태계 호환** | 널리 쓰이는 서비스(Google Workspace, Microsoft 365 등)와 연동되는 도구 우선 |
| **기능 완성도** | API 안정성, 기능 범위, 문서화 수준이 높은 도구 우선 |

### 2순위: 사용자 환경에 따라 ★ 교체

사용자가 특정 환경을 언급하면, 해당 생태계에 맞는 도구로 ★를 교체한다:

| 사용자 환경 | 교체 예시 |
|------------|----------|
| Google Workspace 사용 | email(★) → gmail, google_calendar 유지 |
| Microsoft 365 사용 | email(★) → outlook, google_calendar(★) → microsoft_excel_365 계열 |
| Lark/Feishu 사용 | slack(★) → lark_message_and_group, google_calendar(★) → lark_calendar |
| 셀프호스트 환경 | supabase(★) → sqlite, dropbox → nextcloud |
| 중국 시장 대상 | google(★) → bing, deepl(★) → baidu_translate |

---

## 카테고리별 도구 목록

### 1. 검색/크롤링

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| google | Google Search | 웹 검색 | ★ |
| tavily | Tavily | AI 최적화 검색 (요약 포함) | ★ |
| duckduckgo | DuckDuckGo | 웹 검색 (API 키 불필요) | |
| bing | Bing Search | 웹 검색 | |
| brave | Brave Search | 프라이버시 중심 웹 검색 | |
| searxng | SearXNG | 메타 검색 엔진 (셀프호스트) | |
| searchapi | SearchAPI | 통합 검색 API | |
| serper | Serper | Google SERP API | |
| perplexity | Perplexity | AI 검색 | |
| jina | Jina | 웹 리더/검색 | |
| firecrawl | FireCrawl | 웹 스크래핑/크롤링 | ★ |
| spider | Spider | 웹 크롤링 | |
| websearch | Web Search | 기본 웹 검색 | |

> **선별 근거**: 웹 검색은 google(범용성·정확도 최고), 크롤링은 firecrawl(Dify 공식 예제에서 사용). tavily는 검색 + AI 요약이 필요한 경우 추천. API 키 없이 빠르게 테스트하려면 duckduckgo.

### 2. 학술/지식 검색

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| wikipedia | Wikipedia | 백과사전 검색 | ★ |
| arxiv | arXiv | 학술 논문 검색 | ★ |
| pubmed | PubMed | 의학/생명과학 논문 검색 | |
| hackernews | Hacker News | 기술 뉴스 검색 | |
| stackexchange | Stack Exchange | 기술 Q&A 검색 | |
| devdocs | DevDocs | 개발 문서 검색 | |
| crossref | Crossref | 학술 메타데이터 검색 | |

> **선별 근거**: 일반 지식은 wikipedia(API 키 불필요), 학술은 arxiv(오픈 액세스). 도메인 특화 시 pubmed(의료), stackexchange(기술) 추가.

### 3. 이미지 생성

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| openai | DALL·E | OpenAI 이미지 생성 | ★ |
| stability | Stability AI | Stable Diffusion 이미지 생성 | ★ |
| gemini_image | Gemini Image | Google Gemini 이미지 생성 | |
| azuredalle | Azure DALL·E | Azure 기반 이미지 생성 | |
| stablediffusion | Stable Diffusion | 이미지 생성 (WebUI 필요) | |
| cogview | CogView | 중국어 지원 이미지 생성 | |
| novitaai | Novita AI | 이미지 생성/편집 | |
| fal | fal.ai | 빠른 이미지 생성 | |
| getimgai | getimg.ai | AI 이미지 생성 | |
| comfyui | ComfyUI | 노드 기반 이미지 워크플로우 (셀프호스트) | |
| aihubmix_image | AIHubMix Image | 이미지 생성 | |

> **선별 근거**: openai(DALL·E — 품질·한국어 프롬프트 지원 최고), stability(오픈소스 기반·커스터마이징 가능). 셀프호스트 환경이면 comfyui.

### 4. 음성/영상 (멀티미디어)

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| fishaudio | Fish Audio | TTS (텍스트→음성, 다국어) | ★ |
| transcript | Transcript | 음성→텍스트 변환 (STT) | ★ |
| youtube | YouTube | 유튜브 검색/자막 추출 | ★ |
| minimax_tts | MiniMax TTS | TTS (중국어 특화) | |
| did | D-ID | AI 영상 생성 (아바타) | |
| gemini_video | Gemini Video | Google Gemini 영상 | |
| podcast_generator | Podcast Generator | 팟캐스트 자동 생성 | |
| spotify | Spotify | 음악/팟캐스트 검색 | |

> **선별 근거**: TTS는 fishaudio(다국어·한국어 지원), STT는 transcript, 영상 검색은 youtube. 아바타 영상이 필요하면 did 추가.

### 5. 커뮤니케이션/메시징

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| slack | Slack | 팀 메시징 | ★ |
| email | Email | 이메일 발송 (SMTP) | ★ |
| gmail | Gmail | Gmail API 연동 | |
| outlook | Outlook | Microsoft Outlook 연동 | |
| discord | Discord | 디스코드 메시징 | |
| twilio | Twilio | SMS/음성 통신 | ★ |
| dingtalk | DingTalk | 딩톡 메시징 | |
| feishu_message | Feishu Message | 페이슈(라크) 메시징 | |
| lark_message_and_group | Lark Message | 라크 메시지/그룹 | |
| wecom | WeCom | 기업용 위챗 | |
| whatsapp-bot | WhatsApp Bot | 왓츠앱 봇 | |
| telegraph | Telegraph | 텔레그래프 발행 | |
| onebot | OneBot | QQ 등 봇 프레임워크 | |
| plivo_sms | Plivo SMS | SMS 발송 | |
| plivo_verify | Plivo Verify | SMS 인증 | |
| pushover | Pushover | 푸시 알림 | |
| twitter | Twitter | 트위터 API | |
| zoom | Zoom | 화상회의 | |

> **선별 근거**: 팀 협업은 slack(가장 보편적), 이메일은 email(SMTP — 벤더 무관), SMS는 twilio(글로벌 커버리지). 사용자가 Google Workspace면 gmail, Microsoft 365면 outlook으로 교체.

### 6. 프로젝트/업무 관리

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| notion | Notion | 문서/DB 관리 | ★ |
| jira | Jira | 이슈/프로젝트 관리 | ★ |
| github | GitHub | 코드 저장소/이슈 | ★ |
| gitlab | GitLab | 코드 저장소/CI | |
| gitee_ai | Gitee AI | Gitee 연동 | |
| linear | Linear | 이슈 트래커 | |
| trello | Trello | 칸반 보드 | |
| todoist | Todoist | 할 일 관리 | |
| monday | Monday.com | 워크 매니지먼트 | |
| microsoft_todo | Microsoft To Do | MS 할 일 관리 | |
| google_tasks | Google Tasks | 구글 할 일 관리 | |
| hubspot | HubSpot | CRM/마케팅 | |
| attio | Attio | CRM | |
| salesforce | Salesforce | CRM | |
| smartsheet | Smartsheet | 스프레드시트 기반 프로젝트 관리 | |
| frontapp | Front | 고객 커뮤니케이션 | |
| bitbucket | Bitbucket | 코드 저장소 | |
| jiandaoyun | JianDaoYun | 폼/워크플로우 빌더 | |

> **선별 근거**: 문서/DB는 notion(유연성 최고), 이슈 관리는 jira(엔터프라이즈 표준), 코드 연동은 github. 사용자가 이미 사용 중인 도구가 있으면 해당 도구 우선.

### 7. 문서/파일 처리

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| dify_extractor | Dify Extractor | 문서 텍스트 추출 | ★ |
| llama_parse | LlamaParse | 고급 문서 파싱 (표/이미지 포함) | ★ |
| unstructured | Unstructured | 비정형 문서 처리 | |
| mineru | MinerU | 문서 구조 분석 | |
| slidespeak | SlideSPeak | PPT 분석/요약 | |
| dicom_reader | DICOM Reader | 의료 영상 파일 읽기 | |
| general_chunk | General Chunk | 문서 청킹 | |
| parent_child_chunk | Parent-Child Chunk | 계층적 문서 청킹 | |
| qa_chunk | QA Chunk | Q&A 기반 청킹 | |

> **선별 근거**: 기본 추출은 dify_extractor(Dify 네이티브, 추가 비용 없음), 복잡한 문서(표·이미지 혼합)는 llama_parse.

### 8. OCR/텍스트 인식

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| paddleocr | PaddleOCR | OCR (이미지→텍스트, 한국어 지원) | ★ |
| paddleocr_text_recognition | PaddleOCR Text | 텍스트 인식 특화 | |

> **선별 근거**: paddleocr이 한국어 포함 다국어 지원, 오픈소스.

### 9. 번역

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| deepl | DeepL | 고품질 번역 (유럽어·한국어) | ★ |
| google_translate | Google Translate | 구글 번역 (최다 언어 지원) | |
| baidu_translate | Baidu Translate | 바이두 번역 (중국어 특화) | |

> **선별 근거**: deepl(한국어 번역 품질 최고). 지원 언어 범위가 넓어야 하면 google_translate.

### 10. 날씨/지도/위치

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| openweather | OpenWeather | 날씨 정보 | ★ |
| nominatim | Nominatim | 주소→좌표 변환 (API 키 불필요) | ★ |
| gaode | Gaode Map | 가오더 지도 (중국) | |
| tianditu | Tianditu | 톈디투 지도 (중국) | |

> **선별 근거**: 날씨는 openweather(글로벌·무료 티어), 지오코딩은 nominatim(API 키 불필요).

### 11. 금융/데이터

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| yahoo | Yahoo Finance | 주식/금융 데이터 (API 키 불필요) | ★ |
| alphavantage | Alpha Vantage | 주식/환율/암호화폐 | |

> **선별 근거**: yahoo(API 키 불필요, 글로벌 시장 데이터). 상세 분석이 필요하면 alphavantage 추가.

### 12. 차트/시각화

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| echarts | ECharts | 고급 차트/대시보드 | ★ |
| chart | Chart | 기본 차트 생성 | |
| qrcode | QR Code | QR 코드 생성 | |
| vectorizer | Vectorizer | 이미지 벡터화 | |
| apitemplate | APITemplate | 이미지/PDF 템플릿 | |
| somark | Somark | 워터마크 생성 | |

> **선별 근거**: echarts(차트 종류 풍부, 한국어 라벨 지원). 단순 차트면 chart로 충분.

### 13. 데이터 저장소/DB

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| supabase | Supabase | PostgreSQL 기반 BaaS | ★ |
| sqlite | SQLite | 경량 DB (로컬) | |
| snowflake | Snowflake | 클라우드 데이터 웨어하우스 | |
| neo4j | Neo4j | 그래프 DB | |
| baserow | Baserow | 오픈소스 스프레드시트 DB | |
| nocodb | NocoDB | 오픈소스 Airtable 대안 | |
| oracle_ai_db | Oracle AI DB | Oracle DB AI 연동 | |

> **선별 근거**: supabase(무료 티어, REST API 기본 제공, PostgreSQL 호환). 로컬 경량 DB면 sqlite. 비개발자용 DB면 nocodb 또는 baserow.

### 14. 클라우드 스토리지

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| onedrive | OneDrive | Microsoft 클라우드 스토리지 | |
| dropbox | Dropbox | 클라우드 스토리지 | |
| nextcloud | Nextcloud | 셀프호스트 클라우드 스토리지 | |

> **선별 근거**: 사용자 환경에 따라 선택. Microsoft 365 → onedrive, 범용 → dropbox, 셀프호스트 → nextcloud.

### 15. 캘린더/오피스

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| google_calendar | Google Calendar | 구글 캘린더 | ★ |
| google_contacts | Google Contacts | 구글 연락처 | |
| feishu_calendar | Feishu Calendar | 페이슈 캘린더 | |
| lark_calendar | Lark Calendar | 라크 캘린더 | |
| feishu_spreadsheet | Feishu Spreadsheet | 페이슈 스프레드시트 | |
| lark_spreadsheet | Lark Spreadsheet | 라크 스프레드시트 | |
| feishu_base | Feishu Base | 페이슈 다차원 시트 | |
| lark_base | Lark Base | 라크 다차원 시트 | |
| microsoft_excel_365 | Microsoft Excel 365 | 엑셀 온라인 | |

> **선별 근거**: google_calendar(가장 보편적). 사용자 환경에 따라: Microsoft 365 → 해당 MS 도구, Lark/Feishu → 해당 도구로 교체.

### 16. 위키/지식 관리

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| notion | Notion | 문서/DB 관리 | ★ |
| confluence | Confluence | Atlassian 위키 | |
| feishu_wiki | Feishu Wiki | 페이슈 위키 | |
| lark_wiki | Lark Wiki | 라크 위키 | |
| feishu_document | Feishu Document | 페이슈 문서 | |
| lark_document | Lark Document | 라크 문서 | |
| aliyuque | Aliyuque | 알리 유커 문서 | |

> **선별 근거**: notion(범용성·API 완성도 최고). Atlassian 생태계면 confluence. 사용자가 이미 사용 중인 위키 우선.

### 17. 유틸리티

| provider_id | 도구명 | 용도 | 추천 |
|-------------|--------|------|:----:|
| maths | Maths | 수학 연산 | ★ |
| json_process | JSON Process | JSON 파싱/변환 | ★ |
| regex | Regex | 정규표현식 처리 | |
| judge0ce | Judge0 CE | 코드 실행 (샌드박스) | |
| e2b | E2B | 코드 실행 환경 | |
| rapidapi | RapidAPI | 외부 API 허브 | |
| vanna | Vanna | 자연어→SQL 변환 | |
| hap | HAP | 한국어 형태소 분석 | |
| aws | AWS | AWS 서비스 연동 | |
| seltz | Seltz | 데이터 변환 | |
| spark | Spark | iFlytek 연동 | |
| gpustack | GPUStack | GPU 리소스 관리 | |
| bailian_memory | Bailian Memory | 알리 바이리안 메모리 | |

> **선별 근거**: maths(계산 필요 시 기본), json_process(API 응답 후처리 시 기본). 나머지는 용도별 특화이므로 필요 시 선택.

---

## Dify 네이티브 노드 (플러그인 없이 사용 가능)

도구 플러그인 외에, Dify 워크플로우에서 기본 제공하는 노드:

| 노드 타입 | 용도 | 비고 |
|-----------|------|------|
| knowledge-retrieval | 지식 베이스 검색 (RAG) | 문서 업로드 후 의미 기반 검색 |
| http-request | 외부 REST API 직접 호출 | 도구 플러그인 없는 API도 연동 가능 |
| code | Python/JavaScript 코드 실행 | 데이터 변환, 계산, 파싱 등 |
| question-classifier | 질문 분류 | LLM 기반 입력 분류/라우팅 |
| if-else | 조건 분기 | 워크플로우 로직 제어 |
| iteration | 반복 처리 | 리스트 데이터 순회 |
| parameter-extractor | 파라미터 추출 | LLM으로 구조화된 데이터 추출 |
| template-transform | 템플릿 변환 | Jinja2 기반 텍스트 포매팅 |

---

## 검색 가이드

DSL 생성 또는 개발계획 작성 시, 시나리오의 기능 요구사항을 아래 순서로 매칭:

1. 기능에 대응하는 **Dify 네이티브 노드**가 있는가? (knowledge-retrieval, http-request, code 등)
2. **Dify 공식 도구 플러그인**에 있는가? → 카테고리별 **★ 기본 추천 도구** 참고
3. 사용자가 특정 환경을 언급했는가? → **사용자 환경별 교체 표**에 따라 대체 도구 참고
4. 둘 다 해당 없으면 → **[커스텀 개발 필요]** 태그 부여
