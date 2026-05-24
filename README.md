# Lotto 6/45 Django Project

Django와 Docker Compose를 사용한 6/45 Lotto 웹 사이트입니다. 일반 사용자는 복권을 구매하고 당첨 결과를 확인할 수 있으며, 관리자는 Django admin에서 회차를 만들고 추첨을 실행할 수 있습니다.

## 주요 기능

- 회원가입, 로그인, 로그아웃
- 수동 번호 구매와 자동 번호 구매
- 내 복권 구매 내역 및 별도 당첨 확인 화면
- Django admin 기반 판매 내역 확인
- 회차별 추첨 admin action
- Docker Compose 기반 `web` + `db(PostgreSQL)` multi-container 구성

## 로컬 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.

## Docker 실행

```bash
cp .env.example .env
docker compose up --build
```

관리자 계정은 별도 터미널에서 생성합니다.

```bash
docker compose exec web python manage.py createsuperuser
```

## 사용 흐름

1. `/admin/`에서 관리자 계정으로 로그인합니다.
2. `Round`를 생성하고 판매 시작/종료 시각을 지정합니다.
3. 일반 사용자가 회원가입 후 `/tickets/buy/`에서 복권을 구매합니다.
4. 관리자 화면의 `회차` 목록에서 해당 회차를 선택하고 `선택한 회차 추첨 실행` action을 실행합니다.
5. 사용자는 `/tickets/check/`에서 당첨 결과를 확인합니다.

`추첨 결과` 메뉴는 생성된 결과를 확인하는 용도입니다. 당첨 번호는 관리자가 직접 입력하지 않고, `회차` 목록의 추첨 action으로 랜덤 생성합니다.

## 테스트

```bash
python manage.py test
```

Docker 환경에서는 다음 명령을 사용합니다.

```bash
docker compose exec web python manage.py test
```

## GitHub

소스 코드는 다음 저장소에 제출합니다.

https://github.com/PilSun100/Lotto
