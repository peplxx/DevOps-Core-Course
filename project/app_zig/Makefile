.PHONY: help build run clean release install

# Colors
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

help: ##@Help Show this help message
	@echo ""
	@echo "${BLUE}DevOps Info Service (Zig)${RESET}"
	@echo ""
	@echo "${BLUE}Targets:${RESET}"
	@echo "  ${YELLOW}build${RESET}          Build in debug mode"
	@echo "  ${YELLOW}release${RESET}        Build optimized (ReleaseSmall)"
	@echo "  ${YELLOW}release-fast${RESET}   Build optimized (ReleaseFast)"
	@echo "  ${YELLOW}run${RESET}            Build and run"
	@echo "  ${YELLOW}install${RESET}        Install to system (requires sudo)"
	@echo "  ${YELLOW}clean${RESET}          Clean build artifacts"
	@echo "  ${YELLOW}size${RESET}           Show binary size"
	@echo "  ${YELLOW}test${RESET}           Test endpoints"
	@echo ""

build: ##@Build Build in debug mode
	@echo "${BLUE}Building (debug)...${RESET}"
	@zig build
	@echo "${GREEN}✓ Build complete${RESET}"
	@ls -lh zig-out/bin/devops-info-service

release: ##@Build Build optimized (ReleaseSmall - smallest binary)
	@echo "${BLUE}Building (release small)...${RESET}"
	@zig build -Doptimize=ReleaseSmall
	@echo "${GREEN}✓ Build complete${RESET}"
	@ls -lh zig-out/bin/devops-info-service

release-fast: ##@Build Build optimized (ReleaseFast - fastest execution)
	@echo "${BLUE}Building (release fast)...${RESET}"
	@zig build -Doptimize=ReleaseFast
	@echo "${GREEN}✓ Build complete${RESET}"
	@ls -lh zig-out/bin/devops-info-service

run: build ##@Run Build and run the service
	@echo "${BLUE}Starting service...${RESET}"
	@zig build run

clean: ##@Cleanup Clean build artifacts
	@echo "${BLUE}Cleaning...${RESET}"
	@rm -rf zig-out zig-cache .zig-cache
	@echo "${GREEN}✓ Cleanup complete${RESET}"

install: release ##@Install Install to /usr/local/bin
	@echo "${BLUE}Installing...${RESET}"
	@sudo cp zig-out/bin/devops-info-service /usr/local/bin/
	@echo "${GREEN}✓ Installed to /usr/local/bin/devops-info-service${RESET}"

size: ##@Info Show binary size and comparison
	@echo "${BLUE}Binary Sizes:${RESET}"
	@if [ -f zig-out/bin/devops-info-service ]; then \
		ls -lh zig-out/bin/devops-info-service | awk '{print "  Zig binary:  " $$5}'; \
	else \
		echo "  ${YELLOW}Build first with 'make build'${RESET}"; \
	fi
	@if command -v python3 >/dev/null 2>&1; then \
		python3 -c "import sys; print(f'  Python:      {round(sys.getsizeof(1)*1000000/1024/1024, 1)} MB (approx)')"; \
	fi

test: ##@Test Test the endpoints
	@echo "${BLUE}Testing endpoints...${RESET}"
	@echo "\n${YELLOW}Main endpoint:${RESET}"
	@curl -s http://localhost:8080/ | python3 -m json.tool 2>/dev/null || curl http://localhost:8080/
	@echo "\n${YELLOW}Health endpoint:${RESET}"
	@curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl http://localhost:8080/health
	@echo "\n${YELLOW}404 test:${RESET}"
	@curl -s http://localhost:8080/nonexistent | python3 -m json.tool 2>/dev/null || curl http://localhost:8080/nonexistent

.DEFAULT_GOAL := help
