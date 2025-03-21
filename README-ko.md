이 README는 한국어 버전입니다.  
[Click here for the English version.](./README.md)

![Contributors](https://img.shields.io/github/contributors/3x-haust/Python_Ezy_API_AI?style=flat)
![Forks](https://img.shields.io/github/forks/3x-haust/Python_Ezy_API_AI?style=social?style=flat)
[![Stars](https://img.shields.io/github/stars/3x-haust/Python_Ezy_API_AI?style=flat&logo=GitHub&color=yellow)](https://github.com/3x-haust/Python_Ezy_API/stargazers)
![License](https://img.shields.io/github/license/3x-haust/Python_Ezy_API_AI?style=flat)

</br>

# 목차
- [목차](#목차)
- [기여 방법](#기여-방법)
  - [브랜치 생성하기](#브랜치-생성하기)
    - [브랜치 네이밍 규칙](#브랜치-네이밍-규칙)
  - [작업하고 커밋하기](#작업하고-커밋하기)
    - [커밋 메시지 컨벤션](#커밋-메시지-컨벤션)
    - [커밋 예시](#커밋-예시)
  - [원격 저장소로 푸시](#원격-저장소로-푸시)
  - [Pull Request(PR) 올리기](#pull-requestpr-올리기)
  - [머지하기](#머지하기)

</br>
</br>
</br>

# 기여 방법

Ezy API는 누구나 자유롭게 기여할 수 있습니다!  
아래 절차를 따라 편하게 참여해 주세요.

## 브랜치 생성하기

새로운 작업을 시작할 때는 **브랜치**를 만들어 주세요. 브랜치는 보통 `feature/{기능명}` 형태로 작성합니다.

```bash
# 메인(main) 브랜치로 이동 후 최신 상태로 맞추기
$ git checkout main
$ git pull origin main

# 새 브랜치 생성 및 이동
$ git checkout -b feature/기능명
```

### 브랜치 네이밍 규칙

작업 성격에 맞게 브랜치명을 작성해 주세요.

| 타입 | 설명 | 예시 |
|:---:|:---|:---|
| `feature/` | 새로운 기능 개발 | `feature/login-api`, `feature/add-user-api` |
| `fix/` | 버그 수정 | `fix/login-bug`, `fix/routing-error` |
| `docs/` | 문서 작업 (README, 주석 등) | `docs/update-readme`, `docs/api-docs` |
| `refactor/` | 코드 리팩토링 | `refactor/login-service`, `refactor/db-helper` |
| `test/` | 테스트 코드 추가 및 수정 | `test/user-service-test` |
| `chore/` | 빌드 설정, 패키지 관리, 기타 잡무 | `chore/update-deps`, `chore/ci-config` |

> **팁**
> 
> 브랜치명은 작업 내용을 명확하게 드러내는 것이 좋습니다.


## 작업하고 커밋하기

작업을 마친 뒤, 커밋 메시지는 아래 **커밋 컨벤션**을 참고하여 작성해 주세요.

### 커밋 메시지 컨벤션

| 태그 | 설명 |
|:---:|:---|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 (README, 주석 등) |
| `style` | 코드 포맷팅, 스펠링 수정 등 코드에 영향을 주지 않는 변경 |
| `refactor` | 코드 리팩토링 (동작 변화 없이 내부 로직 개선) |
| `test` | 테스트 코드 추가 및 수정 |
| `chore` | 빌드 업무, 패키지 매니저 설정, 유지보수 작업 등 |

### 커밋 예시
```bash
$ git commit -m "feat: 사용자 API 추가"
$ git commit -m "fix: 잘못된 라우터 경로 수정"
$ git commit -m "docs: README에 설치 방법 추가"
```

## 원격 저장소로 푸시

작성한 브랜치를 원격 저장소에 푸시합니다.

```bash
$ git push origin feature/기능명
```

## Pull Request(PR) 올리기

- GitHub에서 **Pull Request**를 생성합니다.
- 어떤 작업을 했는지 PR 설명란에 간단하게 적어주세요.
- 이후 팀원들과 코드 리뷰를 진행합니다.

## 머지하기

- 리뷰가 끝나고 승인을 받으면 **main 브랜치로 머지**합니다.
- 머지 후에는 다른 작업 전에 항상 `main` 브랜치를 최신으로 맞춰주세요.

```bash
$ git checkout main
$ git pull origin main
```