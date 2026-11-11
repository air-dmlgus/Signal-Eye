<div align="center">

# Signal Eye
### 교통표지판 후보 감지 & 음성 안내 · 포트폴리오 재구현

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv&logoColor=white)
![Demo](https://img.shields.io/badge/Type-Portfolio%20Demo-007F67)

**이미지 속 표지판 후보 영역을 찾고 간단한 주의사항을 음성으로 안내하는 웹 데모**

</div>

> **재구현 안내:** Microsoft AI School의 **Signal Eye 팀 프로젝트** 발표 자료를 바탕으로 기능을 축소해 새로 만든 코드입니다. 원본 Azure AI Vision · Azure Custom Vision · OpenAI · Azure Speech 모델 및 코드를 복원한 것이 아닙니다.
>
> **안전 고지:** 이 데모는 단순 색상·형태 기반 후보 감지입니다. 실제 교통표지판 종류를 정확히 판독하는 시스템이 아니며 **운전·도로 안전 판단에 절대 사용하면 안 됩니다.**

## 01. 프로젝트 배경

초보 운전자가 복잡한 도로에서 교통표지판을 놓치지 않도록 도와주는 **교통표지판 인식 및 음성 안내 시스템**을 목표로 진행한 팀 프로젝트입니다.

**원본 프로젝트의 처리 흐름**

1. 카메라 또는 영상에서 교통표지판 영역 탐색 — **Azure Computer Vision**
2. 표지판 이미지 영역을 잘라서 분류 — **Azure Custom Vision**
3. 표지판 종류에 따른 간결한 안내 문구 생성 — **OpenAI**
4. 안내 문구 음성 재생 — **Azure Speech**

원본 발표 자료에는 GTSRB 데이터셋, 이미지 좌표 전처리, API 연계, 실시간 영상 인식 테스트 등이 담겨 있습니다.

## 02. 이 저장소에서 구현한 기능

| 기능 | 설명 |
| --- | --- |
| 이미지 업로드 | JPG · PNG · WebP 파일을 웹 화면에서 선택 |
| 색상 추출 | OpenCV HSV 마스크로 적색·청색 영역 추출 |
| 형태 후보 분석 | 외곽선·다각형 근사·원형도를 사용해 표지 형태 추정 |
| 후보 위치 시각화 | 원본 이미지 위에 후보 영역 상자와 식별 번호 표시 |
| 안내 문구 표시 | 후보 유형별 사전 정의 안내 메시지 생성 |
| 음성 읽기 | 브라우저 `SpeechSynthesis` API를 통한 한국어 음성 재생 |

**중요:** 감지 결과는 '후보'이며 정밀한 모델 신뢰도나 실제 표지판 분류 결과가 아닙니다. 원본의 Azure Speech 대신 **브라우저 음성 합성**을 사용했습니다. 외부 API 키는 필요 없습니다.

## 03. 화면과 API 흐름

```text
JPG/PNG/WebP 업로드
        │
        ▼
Python HTTP API  (POST /api/analyze)
        │
        ▼
OpenCV HSV 색상 분리
        │
        ▼
윤곽선 추출 + 기초 형태 분석
        │
        ▼
표지판 후보 JSON 반환
        │
        ▼
브라우저 Canvas에 영역 표시
        │
        ▼
안내문 표시 + SpeechSynthesis 재생
```

## 04. 실행 방법

**Python 3.10 이상** 권장.

```bash
git clone https://github.com/air-dmlgus/Signal-Eye.git
cd Signal-Eye
python -m pip install -r requirements.txt
python app.py
```

브라우저에서 **http://127.0.0.1:8001** 에 접속합니다.

1. 사진 파일을 선택합니다.
2. **이미지 분석하기**를 누릅니다.
3. 후보 위치와 안내 문구를 확인합니다.
4. **안내 음성 듣기**를 누르면 브라우저가 문구를 읽어줍니다.

### 직접 생성한 예시 이미지로 시연하기

```bash
python tools/make_sample.py
```

생성된 `sample_signs.png` 파일을 웹 화면에 업로드하세요. 이 이미지는 테스트용 도형이며 실제 교통표지판 사진이 아닙니다.

### 테스트

```bash
python -m unittest discover -s tests -v
```

### API

```text
POST /api/analyze
Content-Type: application/octet-stream
Body: JPG/PNG/WebP 파일의 바이너리 데이터 (최대 5MB)
```

반환 예시:

```json
{
  "width": 900,
  "height": 520,
  "detections": [
    {
      "label": "원형 규제 표지 후보",
      "advice": "규제 표지로 보이는 영역이 있습니다. 표지 내용을 확인하세요.",
      "bbox": [145, 95, 230, 230],
      "color": "red"
    }
  ],
  "disclaimer": "색상·형태 기반 데모 결과"
}
```

예시 좌표와 실제 탐지 결과는 이미지에 따라 달라집니다.

## 05. 기술 스택

| 분류 | 기술 |
| --- | --- |
| Language | Python |
| Image Processing | OpenCV, NumPy |
| Backend | Python HTTP Server, JSON API |
| Frontend | HTML, CSS, JavaScript, Canvas |
| Speech | Web Speech API (`SpeechSynthesis`) |
| Testing | Python `unittest` |
| 원본 팀 프로젝트에서 다룬 기술 | Azure AI Vision, Azure Custom Vision, OpenAI, Azure Speech, Gradio |

## 06. 폴더 구조

```text
Signal-Eye/
├── app.py                 # 웹 페이지와 이미지 업로드 API
├── detector.py            # 색상·형태 기반 후보 감지
├── requirements.txt       # OpenCV, NumPy
├── tools/
│   └── make_sample.py     # 테스트용 가상 이미지 생성
├── tests/
│   └── test_detector.py   # 단위 테스트
├── .gitignore
└── README.md
```

## 07. 원본 팀 프로젝트에서의 담당 역할

**Microsoft AI School · Signal Eye · 이의현**

- **프로젝트 팀장 역할 수행** *(본인 확인 내용)*
- 데이터 전처리 및 **Vision 개발** 참여 *(발표 자료의 팀원 소개 기준)*
- 표지판 인식에서 음성 안내까지 이어지는 서비스의 기획·협업 경험

> 역할 표기 참고: 제공된 발표자료의 팀원 소개 슬라이드에는 **윤경록이 Project Manager**, **이의현이 데이터 전처리 및 Vision 개발**로 표시되어 있습니다. 따라서 이 README의 '팀장' 표기는 본인이 알려준 실무 역할을 반영한 것이며, 발표자료에 기재된 공식 PM 직함과 구분합니다.

## 08. 원본 프로젝트와 재구현의 차이

| 구분 | 원본 Signal Eye | 이 저장소 |
| --- | --- | --- |
| 이미지 인식 | Azure Computer Vision | OpenCV HSV 색상 마스크 |
| 종류 분류 | Azure Custom Vision | 외곽선·형태 후보 분류 |
| 안내문 생성 | OpenAI | 규칙 기반 고정 메시지 |
| 음성 | Azure Speech | 브라우저 Web Speech API |
| 데이터/운영 | 카메라 영상, API 연계 | 이미지 1장 업로드 |
| 목적 | 팀 프로젝트 시제품 | 실행 가능한 최소 포트폴리오 예제 |

## 09. 향후 개선 계획

- 실제 교통표지판 데이터셋 기반 분류 모델 또는 Azure Vision 연계
- 더 다양한 크기·조명·각도에서의 검출 정확도 측정
- 웹캠 연속 프레임 처리 및 응답시간 측정
- 잘못된 인식 결과 억제 및 신뢰도 임계치 도입
- 안전 고지와 사용자 동의 및 개인정보 보호 강화

---

**Portfolio reconstruction** · 원본 팀 프로젝트와 구분되는 학습용 재구현
