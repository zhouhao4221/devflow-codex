# API 플러그인 - 튜토리얼

🌐 [English](tutorial.en.md) | [中文](tutorial.zh.md) | [한국어](tutorial.ko.md)

## 섹션

 1. 빠른 시작
 2. 설정 관리
 3. Swagger 임포트
 4. 엔드포인트 검색
 5. 필드 매핑
 6. 코드 생성
 7. 자동 감지
 8. FAQ

---

## 1. 빠른 시작

세 단계로 시작:

### 1 단계: 설정 초기화

프론트엔드 프로젝트 루트에서:

```
/api:config init
```

안내에 따라 백엔드 Swagger 문서 주소를 입력하면 `.api-config.json` 이 생성됩니다.

### 2 단계: 엔드포인트 임포트

```
/api:import
```

Swagger 문서를 파싱하고 태그별 엔드포인트 개요를 표시합니다.

### 3 단계: 개발에서 사용

```
/api:search 사용자                      # 엔드포인트 검색
/api:map GET /api/v1/users/{id}        # 필드 매핑 조회
/api:gen GET /api/v1/users/{id}        # 타입 + 요청 함수 생성
```

전체 플로우:

```
/api:config init → /api:import → /api:search → /api:map → /api:gen
설정 초기화        문서 임포트    검색          필드 매핑    코드 생성
```

---

## 2. 설정 관리

설정 파일: 프로젝트 루트의 `.api-config.json`

### 초기화

```
/api:config init
```

인터랙티브 설정 생성, `src/api/` 와 `src/types/` 디렉터리 자동 감지.

### 설정 조회

```
/api:config
```

현재 데이터 소스, 코드 생성 디렉터리, 감지된 요청 라이브러리를 표시.

### 데이터 소스 추가

```
/api:config add
```

URL (백엔드 온라인 문서) 과 로컬 파일 두 가지 방식 지원.

### 데이터 소스 삭제

```
/api:config remove payment-service
```

### 설정 예시

```json
{
  "swagger": {
    "sources": [
      { "name": "main", "url": "http://localhost:8080/swagger/doc.json", "prefix": "/api/v1" },
      { "name": "payment", "file": "./docs/payment-swagger.json", "prefix": "/pay/v1" }
    ]
  },
  "codegen": {
    "outputDir": "src/api",
    "typeDir": "src/types/api",
    "fieldCase": "camelCase"
  }
}
```

`.api-config.json` 을 버전 관리에 포함시켜 팀에서 공유하는 것을 권장합니다.

---

## 3. Swagger 임포트

### 모든 데이터 소스 임포트

```
/api:import
```

### 특정 데이터 소스 임포트

```
/api:import --name=main
```

### 임시 임포트 (설정 수정하지 않음)

```
/api:import --url=http://other-service:8080/swagger/doc.json
```

### 지원 포맷

- OpenAPI 2.0 (Swagger)
- OpenAPI 3.0.x / 3.1.x
- JSON 과 YAML 포맷

Python 3 필요, 첫 사용 시 설치 여부 확인.

---

## 4. 엔드포인트 검색

### 키워드 검색

```
/api:search 사용자
```

경로, 설명, 태그 이름을 매칭하며 다국어 지원.

### 태그별 브라우징

```
/api:search --tag=사용자 관리
```

### 메서드 필터

```
/api:search 사용자 --method=GET
```

### 데이터 소스 지정

```
/api:search 결제 --name=payment
```

### 검색 결과 예시

```
🔍 "사용자" 검색 — 5 개 엔드포인트 발견

┌────┬─────────┬──────────────────────┬──────────────┐
│ #  │ 메서드  │ 경로                  │ 설명         │
├────┼─────────┼──────────────────────┼──────────────┤
│ 1  │ GET     │ /api/v1/users        │ 사용자 목록   │
│ 2  │ POST    │ /api/v1/users        │ 사용자 생성   │
│ 3  │ GET     │ /api/v1/users/{id}   │ 사용자 상세   │
└────┴─────────┴──────────────────────┴──────────────┘
```

---

## 5. 필드 매핑

핵심 기능: 엔드포인트의 백엔드 ↔ 프론트엔드 전체 필드 매핑을 표시합니다.

### 기본 사용법

```
/api:map GET /api/v1/users/{id}
```

### 출력 내용

- 경로 / 쿼리 파라미터
- 요청 바디 필드 매핑 (POST/PUT)
- 응답 바디 필드 매핑
- TypeScript 타입 프리뷰

### 매핑 규칙

```
백엔드 snake_case  →  프론트엔드 camelCase
user_name          →  userName
avatar_url         →  avatarUrl
created_at         →  createdAt
is_active          →  isActive
```

### 중첩 객체

중첩 필드는 계층 번호로 표시되며 (예: 7.1, 7.2), TypeScript 에서 중첩 타입을 생성합니다.

### 일괄 매핑

```
/api:map * /api/v1/users/{id}
```

해당 경로의 모든 HTTP 메서드에 대한 매핑을 표시.

---

## 6. 코드 생성

엔드포인트 정의로부터 TypeScript 타입과 요청 함수를 생성합니다.

### 기본 사용법

```
/api:gen GET /api/v1/users/{id}
```

두 파일을 생성:
- `src/types/api/user.ts` — 타입 정의
- `src/api/user.ts` — 요청 함수

### 타입만 생성

```
/api:gen GET /api/v1/users/{id} --type-only
```

### 요청 함수만 생성

```
/api:gen GET /api/v1/users/{id} --request-only
```

### 일괄 생성

```
/api:gen --tag=사용자 관리        # 태그별 일괄
/api:gen * /api/v1/users          # 해당 경로의 모든 메서드
/api:gen * /api/v1/users/{id}     # 해당 경로의 모든 메서드
```

### 요청 라이브러리 어댑터

플러그인이 프로젝트의 요청 라이브러리를 자동 감지하여 해당 스타일의 코드를 생성:
- 커스텀 래퍼 파일 (예: `src/utils/request.ts`) — 직접 임포트
- axios — `axios.get/post` 스타일
- umi-request — `request()` 스타일
- `@tanstack/react-query` — `useQuery` / `useMutation` 훅
- swr — `useSWR` 훅
- 네이티브 fetch — async/await 스타일

---

## 7. 자동 감지

### 요청 라이브러리 감지

코드 생성 시 자동 감지, 설정 불필요. 감지 순서:

1. 프로젝트의 request 래퍼 파일 (최우선)
   - `src/utils/request.ts`
   - `src/lib/request.ts`
   - `src/services/request.ts`

2. `package.json` 의 의존성
   - axios / umi-request / `@tanstack/react-query` / swr / ky

3. 찾지 못함 → 네이티브 fetch

### Skill 자동 연결

프론트엔드 TypeScript/Vue 파일 편집 시, 플러그인이 API 호출을 감지하고 필드 매핑 관계와 불일치 가능성을 안내합니다.

트리거 조건: `src/**/*.ts`, `src/**/*.tsx`, `src/**/*.vue` 편집

---

## 8. FAQ

### Python 미설치

```
❌ Python 3 필요

해결: brew install python3 (macOS) 또는 apt install python3 (Linux)
```

### Swagger 주소 접근 불가

```
❌ http://localhost:8080/swagger/doc.json 접근 불가

확인:
- 백엔드 서비스가 실행 중인지
- URL 이 정확한지 (브라우저에서 검증)
- VPN / 프록시 필요 여부
```

### YAML 포맷 문서 파싱 실패

```
❌ YAML 포맷은 pyyaml 이 필요합니다

해결: pip3 install pyyaml
```

### 생성된 코드의 필드 스타일이 잘못됨

`.api-config.json` 의 `fieldCase` 수정:
- `"camelCase"` — 카멜 (기본)
- `"snake_case"` — 언더스코어
- `"original"` — 원본 유지

### 여러 백엔드 서비스

`.api-config.json` 의 `sources` 배열에 여러 데이터 소스를 추가하고, 각기 다른 `name` 과 `prefix` 를 지정한 뒤 검색 시 `--name` 으로 필터링합니다.
