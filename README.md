# rest_api_template
팀내 신입 개발자를 위한 참고용 파이썬 REST API 템플릿, 엄밀히 말하면 HTTP API 템플릿 정도

### 개발 환경
회사에서는 낡은 Windows Laptop, 집에서는 낡은 MacBook이 사용됨
- WSL2 (Windows only)
- Python 3.8 (보통 이 버전이 설치되어 있음)
- Pipenv
- Git
- VSCode (옵션임, 최근까지 vi 사용했음)

참고로 추가로 설치, 사용된 파이썬 라이브러리는 아래와 같음
- fastapi
- fastapi-utils (UUID 키 때문에)
- uvicorn
- sqlalchemy
- pytest

### 사용 방법
1. 설치
```
$ git clone git@github.com:sanxoo/rest_api_template.git
$ cd rest_api_template
$ pipenv install
```
2. 테스트
```
$ pipenv shell
(rest_api_template) $ pytest
```
3. 실행
```
(rest_api_template) $ python main.py
```
4. 요청
```
$ curl -i http://localhost:8080/items
```

### 기타
VSCode에서 작업하려면 .vscode/settings.json 파일에 설정이 필요, 아래는 샘플
```
{
    "python.pythonPath": "/Users/sanxoo/.local/share/virtualenvs/rest_api_template-tlYvGguP/bin/python",
    "python.testing.pytestEnabled": true
}
```
궁굼한 것들은 Google에 다 있음
