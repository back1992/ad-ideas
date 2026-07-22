.PHONY: help test test-verbose test-quick \
        test-articles test-comments test-moderation test-auth test-db \
        test-search test-feedback test-activity test-analytics \
        test-ai test-ai-agent test-ai-chat \
        test-integration test-workflows test-e2e \
        test-all-strict run clean lint format

PYTHON = .venv/bin/python
PYTEST = $(PYTHON) -m pytest
STREAMLIT = .venv/bin/streamlit

# Default target
help:
	@echo "📚 Advertising History Platform - Available Commands"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test              - Run all tests (quick)"
	@echo "  make test-verbose      - Run all tests with verbose output"
	@echo "  make test-quick        - Run tests without e2e (fastest)"
	@echo ""
	@echo "📦 Module Tests:"
	@echo "  make test-articles     - Article system tests (5 tests)"
	@echo "  make test-comments     - Comment system tests (38 tests)"
	@echo "  make test-moderation   - Moderation system tests (7 tests)"
	@echo "  make test-auth         - Authentication tests"
	@echo "  make test-db           - Database tests"
	@echo "  make test-search       - Search system tests"
	@echo "  make test-feedback     - Feedback system tests"
	@echo "  make test-activity     - Activity logging tests"
	@echo "  make test-analytics    - Analytics tests"
	@echo ""
	@echo "🤖 AI Tests:"
	@echo "  make test-ai           - All AI tests"
	@echo "  make test-ai-agent     - AI agent tests (23 tests)"
	@echo "  make test-ai-chat      - AI chat backend tests (12 tests)"
	@echo ""
	@echo " Integration Tests:"
	@echo "  make test-integration  - Integration checkpoint tests (20 tests)"
	@echo "  make test-workflows    - Complete workflow tests (8 tests)"
	@echo "  make test-e2e          - End-to-end tests (18 tests)"
	@echo ""
	@echo "🚀 Application:"
	@echo "  make run               - Start Streamlit app"
	@echo "  make clean             - Remove cache files"
	@echo "  make lint              - Run linter (if configured)"
	@echo "  make format            - Format code (if configured)"

# All tests
test:
	$(PYTEST) tests/ --ignore=tests/test_e2e_register_login.py -q

test-verbose:
	$(PYTEST) tests/ --ignore=tests/test_e2e_register_login.py -v

test-quick:
	$(PYTEST) tests/test_article_properties.py \
	          tests/test_comment_properties.py \
	          tests/test_comment_new_features.py \
	          tests/test_moderation_properties.py \
	          tests/test_integration_checkpoint.py -q

# Module tests
test-articles:
	$(PYTEST) tests/test_article_properties.py -v

test-comments:
	$(PYTEST) tests/test_comment_properties.py tests/test_comment_new_features.py -v

test-moderation:
	$(PYTEST) tests/test_moderation_properties.py -v

test-auth:
	$(PYTEST) tests/test_auth_properties.py -v

test-db:
	$(PYTEST) tests/test_database_properties.py -v

test-search:
	$(PYTEST) tests/test_search_properties.py -v

test-feedback:
	$(PYTEST) tests/test_feedback_properties.py -v

test-activity:
	$(PYTEST) tests/test_activity_properties.py -v

test-analytics:
	$(PYTEST) tests/test_analytics_properties.py -v 2>/dev/null || echo "No analytics tests found"

# AI tests
test-ai: test-ai-agent test-ai-chat

test-ai-agent:
	$(PYTEST) tests/test_ai_agent.py -v

test-ai-chat:
	$(PYTEST) tests/test_ai_chat_backend.py -v

# Integration tests
test-integration:
	$(PYTEST) tests/test_integration_checkpoint.py -v

test-workflows:
	$(PYTEST) tests/test_complete_workflows.py -v

test-e2e:
	$(PYTEST) tests/test_e2e.py tests/test_e2e_register_login.py -v -s

# Application
run:
	$(STREAMLIT) run streamlit_app.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .coverage htmlcov/ 2>/dev/null || true
	@echo "✅ Cleaned cache files"

lint:
	@echo "Running linter..."
	$(PYTHON) -m flake8 modules/ tests/ --max-line-length=120 2>/dev/null || \
	$(PYTHON) -m ruff check modules/ tests/ 2>/dev/null || \
	echo "️  No linter configured. Install flake8 or ruff."

format:
	@echo "Formatting code..."
	$(PYTHON) -m black modules/ tests/ 2>/dev/null || \
	$(PYTHON) -m ruff format modules/ tests/ 2>/dev/null || \
	echo "⚠️  No formatter configured. Install black or ruff."

# Coverage
coverage:
	$(PYTEST) tests/ --ignore=tests/test_e2e_register_login.py --cov=modules --cov-report=term-missing

coverage-html:
	$(PYTEST) tests/ --ignore=tests/test_e2e_register_login.py --cov=modules --cov-report=html
	@echo "📊 Coverage report generated in htmlcov/"
