# 탐구 실험실

[실험 모음 열기](https://learning-experiments-gc261103.incheon-seok-1409.chatgpt.site)

Node.js 22 이상에서 실행합니다.

```sh
npm start
```

서버 환경 변수 `GEMINI_API_KEY`를 설정해야 분석 기능을 사용할 수 있습니다. `GEMINI_MODEL`의 기본값은 `gemini-3.5-flash`입니다. 키를 웹 파일에 넣지 마세요.

```sh
npm run check
npm test
npm run build
```

`web/`은 각 실험 화면, `server/`는 Gemini 호출과 웹 서버입니다. 배포 결과물은 `dist/server/index.js`입니다.
