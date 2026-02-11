.PHONY: help run dev install clean env info format lint test

# Load environment variables from .env if it exists
ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

# Help function
HELP_FUN = \
    %help; \
    printf "\n${BLUE}DevOps Info Service${RESET}\n\n"; \
    printf "${BLUE}Usage:${RESET}\n  make ${YELLOW}<target>${RESET}\n\n"; \
    while(<>) { \
        if(/^([a-zA-Z0-9_-]+):.*\#\#(?:@([a-zA-Z0-9_-]+))?\s(.*)$$/) { \
            push(@{$$help{$$2 // 'Other'}}, [$$1, $$3]); \
        } \
    }; \
    printf "${BLUE}Targets:${RESET}\n"; \
    for (sort keys %help) { \
        printf "${GREEN}%s:${RESET}\n", $$_; \
        printf "  ${YELLOW}%-12s${RESET} %s\n", $$_->[0], $$_->[1] for @{$$help{$$_}}; \
        print "\n"; \
    }

help: ##@Help Show this help message
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

env: ##@Setup Create .env file from .env.example
	@if [ -f .env ]; then \
		echo "${YELLOW}⚠️  .env file already exists${RESET}"; \
	else \
		cp .env.example .env; \
		echo "${GREEN}✓ Created .env file${RESET}"; \
	fi

install: ##@Setup Install dependencies
	@echo "${BLUE}Installing dependencies...${RESET}"
	@uv sync
	@echo "${GREEN}✓ Dependencies installed${RESET}"

run: ##@Run Run the application
	@echo "${BLUE}Starting application...${RESET}"
	@uv run -m app

dev: ##@Run Run in development mode (auto-reload)
	@echo "${BLUE}Starting in dev mode...${RESET}"
	@DEBUG=true uv run -m app

format: ##@Code Format and fix code with ruff
	@echo "${BLUE}Formatting code...${RESET}"
	@uv run ruff check --fix app/
	@echo "${GREEN}✓ Code formatted${RESET}"

lint: ##@Code Lint code with ruff (no fixes)
	@echo "${BLUE}Linting code...${RESET}"
	@uv run ruff check app/ tests/
	@echo "${GREEN}✓ Lint completed${RESET}"

test: ##@Code Run unit tests
	@echo "${BLUE}Running tests...${RESET}"
	@uv run pytest -q
	@echo "${GREEN}✓ Tests passed${RESET}"

clean: ##@Cleanup Clean up cache files
	@echo "${BLUE}Cleaning up...${RESET}"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "${GREEN}✓ Cleanup completed${RESET}"

info: ##@Info Show environment information
	@echo "${BLUE}Environment:${RESET}"
	@echo "Python: $$(python3 --version 2>&1)"
	@echo "uv: $$(uv --version 2>&1)"
	@echo "Directory: $$(pwd)"
	@if [ -f .env ]; then \
		echo "Config: HOST=${HOST:-0.0.0.0} PORT=${PORT:-5000} DEBUG=${DEBUG:-false}"; \
	else \
		echo "${YELLOW}No .env file found. Run 'make env' to create one.${RESET}"; \
	fi

.DEFAULT_GOAL := help
