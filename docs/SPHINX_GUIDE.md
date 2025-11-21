# Sphinx 문서화 가이드

## 📚 목차

1. [Sphinx란?](#sphinx란)
2. [설치](#설치)
3. [프로젝트 설정](#프로젝트-설정)
4. [Google Style Docstring 연동](#google-style-docstring-연동)
5. [문서 빌드](#문서-빌드)
6. [GitHub Pages 배포](#github-pages-배포)
7. [문서 작성 팁](#문서-작성-팁)

---

## Sphinx란?

**Sphinx**는 Python 프로젝트를 위한 문서 생성 도구입니다.

### 주요 기능
- ✅ Python 코드의 docstring을 자동으로 읽어 API 문서 생성
- ✅ Markdown 및 reStructuredText 지원
- ✅ HTML, PDF, ePub 등 다양한 형식으로 출력
- ✅ 코드 하이라이팅 및 크로스 레퍼런스
- ✅ 테마 커스터마이징 가능

### Google Style Docstring과의 관계

이 프로젝트는 **Google Style docstring**을 사용합니다:

```python
def adjust_balance(self, user_id: str, amount: int) -> Dict[str, Any]:
    """
    유저 잔액을 조정하고 거래 기록을 생성합니다.

    Args:
        user_id: 유저의 Mastodon ID
        amount: 조정할 금액 (양수: 입금, 음수: 출금)

    Returns:
        업데이트된 유저와 생성된 거래 정보를 담은 딕셔너리

    Raises:
        ValueError: 잔액이 음수가 되는 경우
    """
```

Sphinx는 **Napoleon 확장**을 통해 Google Style docstring을 파싱합니다.

---

## 설치

### 1. Sphinx 및 필수 패키지 설치

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

**패키지 설명:**
- `sphinx`: 핵심 Sphinx 도구
- `sphinx-rtd-theme`: Read the Docs 테마 (가장 인기 있는 테마)
- `sphinx-autodoc-typehints`: Python 타입 힌트를 문서에 자동 포함

### 2. requirements.txt에 추가

```bash
# requirements.txt에 추가
echo "sphinx>=7.0.0" >> requirements.txt
echo "sphinx-rtd-theme>=2.0.0" >> requirements.txt
echo "sphinx-autodoc-typehints>=1.25.0" >> requirements.txt
```

---

## 프로젝트 설정

### 1. Sphinx 초기화

프로젝트 루트에서 실행:

```bash
mkdir docs
cd docs
sphinx-quickstart
```

**대화형 질문 응답:**
```
> Separate source and build directories (y/n) [n]: y
> Project name: CommuManager
> Author name(s): Your Name
> Project release []: 1.0.0
> Project language [en]: ko
```

### 2. 디렉토리 구조

초기화 후 구조:
```
docs/
├── source/           # 문서 소스 파일
│   ├── conf.py      # Sphinx 설정
│   ├── index.rst    # 메인 페이지
│   └── _static/     # CSS, 이미지 등
├── build/           # 빌드 결과물
│   └── html/        # HTML 문서
└── Makefile         # 빌드 명령어
```

### 3. conf.py 설정

`docs/source/conf.py`를 수정:

```python
# -*- coding: utf-8 -*-
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
project = 'CommuManager'
copyright = '2024, Your Name'
author = 'Your Name'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',        # 자동 문서화
    'sphinx.ext.napoleon',       # Google/NumPy Style docstring 지원
    'sphinx.ext.viewcode',       # 소스 코드 링크
    'sphinx.ext.todo',           # TODO 항목 표시
    'sphinx.ext.coverage',       # 문서 커버리지 체크
    'sphinx_autodoc_typehints',  # 타입 힌트 자동 포함
]

# Napoleon 설정 (Google Style docstring 파싱)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# 템플릿 경로
templates_path = ['_templates']

# 제외할 파일 패턴
exclude_patterns = []

# 언어 설정
language = 'ko'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Read the Docs 테마
html_static_path = ['_static']

# 테마 옵션
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
}

# -- Extension configuration -------------------------------------------------
# autodoc 설정
autodoc_default_options = {
    'members': True,           # 모든 멤버 포함
    'member-order': 'bysource',  # 소스 파일 순서대로
    'special-members': '__init__',
    'undoc-members': False,      # docstring 없는 멤버 제외
    'exclude-members': '__weakref__'
}

# 타입 힌트 설정
autodoc_typehints = 'description'  # 타입 힌트를 설명에 포함
```

---

## Google Style Docstring 연동

### Napoleon 확장

`conf.py`에 이미 `sphinx.ext.napoleon` 확장이 포함되어 있습니다. 이것이 Google Style docstring을 자동으로 파싱합니다.

### Docstring 예시

프로젝트의 모든 모델, 서비스, 레포지토리는 이미 Google Style로 작성되어 있습니다:

**admin_web/services/user_service.py 예시:**
```python
def adjust_balance(self, user_id: str, amount: int, ...) -> Dict[str, Any]:
    """
    유저 잔액을 조정하고 거래 기록을 생성합니다.

    Args:
        user_id: 유저의 Mastodon ID
        amount: 조정할 금액 (양수: 입금, 음수: 출금)
        transaction_type: 거래 유형 (purchase, refund, adjustment)
        description: 거래 설명
        admin_name: 관리자 이름

    Returns:
        다음 키를 포함하는 딕셔너리:
        - user: 업데이트된 User 객체
        - transaction: 생성된 Transaction 객체

    Raises:
        ValueError: 잔액이 음수가 되는 경우
    """
```

Sphinx는 이 docstring을 다음과 같이 렌더링합니다:

![예시 이미지](https://www.sphinx-doc.org/en/master/_images/napoleon_google_docstring.png)

---

## 문서 빌드

### 1. index.rst 작성

`docs/source/index.rst`를 수정:

```rst
CommuManager 문서
==================

마스토돈 커뮤니티 관리 시스템

.. toctree::
   :maxdepth: 2
   :caption: 목차:

   installation
   user_guide
   api/modules

설치
----

.. code-block:: bash

   pip install -r requirements.txt
   python init_db.py

빠른 시작
---------

.. code-block:: bash

   docker-compose up -d

인덱스
======

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

### 2. API 문서 자동 생성

```bash
cd docs
sphinx-apidoc -o source/api ../admin_web
```

이 명령은 `admin_web` 패키지의 모든 모듈에 대한 `.rst` 파일을 자동 생성합니다:

```
docs/source/api/
├── modules.rst
├── admin_web.models.rst
├── admin_web.repositories.rst
├── admin_web.services.rst
└── admin_web.controllers.rst
```

### 3. HTML 빌드

```bash
cd docs
make html
```

또는 Windows에서:
```bash
.\make.bat html
```

빌드 결과는 `docs/build/html/index.html`에 생성됩니다.

### 4. 로컬에서 확인

```bash
# Python 내장 서버로 확인
cd docs/build/html
python -m http.server 8000

# 브라우저에서 http://localhost:8000 접속
```

---

## GitHub Pages 배포

### 방법 1: gh-pages 브랜치 사용

#### 1. sphinx-build로 직접 빌드

```bash
# docs 디렉토리로 이동
cd docs

# HTML 빌드
sphinx-build -b html source build/html

# gh-pages 브랜치로 배포
cd ..
git checkout --orphan gh-pages
git rm -rf .
cp -r docs/build/html/* .
touch .nojekyll  # GitHub Pages에서 _static 디렉토리 무시 방지
git add .
git commit -m "docs: Sphinx 문서 배포"
git push origin gh-pages
git checkout main
```

#### 2. GitHub Actions로 자동 배포

`.github/workflows/docs.yml` 생성:

```yaml
name: Deploy Sphinx Docs

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

      - name: Build Sphinx documentation
        run: |
          cd docs
          sphinx-build -b html source build/html

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/build/html
```

### 방법 2: Read the Docs 연동

1. [Read the Docs](https://readthedocs.org)에 가입
2. GitHub 저장소 연동
3. `.readthedocs.yaml` 생성:

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"

sphinx:
  configuration: docs/source/conf.py

python:
  install:
    - requirements: requirements.txt
```

4. 푸시하면 자동 빌드 및 배포

---

## 문서 작성 팁

### 1. 모듈 문서 작성

`docs/source/api/custom.rst` 생성:

```rst
사용자 관리 모듈
================

.. automodule:: admin_web.services.user_service
   :members:
   :undoc-members:
   :show-inheritance:

예제
----

.. code-block:: python

   from admin_web.services import UserService

   service = UserService()
   user = service.get_user('user_id_123')
   print(user.balance)
```

### 2. 클래스 문서 작성

```rst
User 모델
=========

.. autoclass:: admin_web.models.User
   :members:
   :special-members: __init__
   :show-inheritance:
```

### 3. 함수 문서 작성

```rst
.. autofunction:: admin_web.services.user_service.UserService.adjust_balance
```

### 4. 코드 예제 포함

```rst
사용 예제
=========

잔액 조정
---------

.. code-block:: python

   from admin_web.services import UserService

   service = UserService()
   result = service.adjust_balance(
       user_id='user123',
       amount=100,
       transaction_type='adjustment',
       description='관리자 지급'
   )
   print(f"새 잔액: {result['user'].balance}")
```

### 5. 경고 및 주의사항

```rst
.. warning::
   잔액이 음수가 되지 않도록 주의하세요!

.. note::
   모든 거래는 데이터베이스에 기록됩니다.

.. tip::
   대량 작업 시 트랜잭션을 사용하세요.
```

---

## 빌드 자동화 스크립트

### build_docs.sh

```bash
#!/bin/bash

# Sphinx 문서 빌드 스크립트

set -e

echo "📚 Sphinx 문서 빌드 시작..."

# API 문서 자동 생성
echo "🔧 API 문서 생성 중..."
cd docs
sphinx-apidoc -f -o source/api ../admin_web

# HTML 빌드
echo "🏗️  HTML 빌드 중..."
make clean
make html

echo "✅ 빌드 완료!"
echo "📖 문서 확인: docs/build/html/index.html"
```

### 사용법

```bash
chmod +x build_docs.sh
./build_docs.sh
```

---

## 문서 커버리지 체크

문서화되지 않은 코드 찾기:

```bash
cd docs
make coverage

# 결과 확인
cat build/coverage/python.txt
```

---

## 자주 묻는 질문

### Q1: Docstring이 표시되지 않아요

**A:** `conf.py`에서 `sys.path`가 올바르게 설정되었는지 확인:

```python
sys.path.insert(0, os.path.abspath('../..'))
```

### Q2: 한글이 깨져요

**A:** `conf.py`에서 언어 설정 확인:

```python
language = 'ko'
```

### Q3: 타입 힌트가 표시되지 않아요

**A:** `sphinx-autodoc-typehints` 설치 및 설정:

```bash
pip install sphinx-autodoc-typehints
```

```python
# conf.py
extensions = [
    'sphinx_autodoc_typehints',
]
autodoc_typehints = 'description'
```

### Q4: Private 메서드도 문서화하고 싶어요

**A:** `conf.py` 수정:

```python
autodoc_default_options = {
    'private-members': True,
}
```

---

## 추가 리소스

- [Sphinx 공식 문서](https://www.sphinx-doc.org/)
- [Napoleon 확장 가이드](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- [Google Style Docstring 예시](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
- [Read the Docs 테마 문서](https://sphinx-rtd-theme.readthedocs.io/)

---

## 이 프로젝트에 적용하기

### 1단계: 설치

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

### 2단계: 초기화

```bash
cd docs
sphinx-quickstart
# 위의 설정대로 응답
```

### 3단계: conf.py 설정

위의 "프로젝트 설정" 섹션의 `conf.py` 내용 복사

### 4단계: API 문서 생성

```bash
sphinx-apidoc -o source/api ../admin_web
```

### 5단계: 빌드

```bash
make html
```

### 6단계: 확인

```bash
cd build/html
python -m http.server 8000
```

브라우저에서 `http://localhost:8000` 접속

---

**모든 코드의 docstring이 이미 Google Style로 작성되어 있으므로, Sphinx만 설정하면 바로 아름다운 문서가 생성됩니다!** ✨
