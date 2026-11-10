# ==============================================================================
# SpatialForge AI: Unified Platform Orchestration & Build System
# Multi-Service Architecture: Go Gateway, Rust Crypto Enclave, Stealth Crawler,
# Python Intelligence Engine, PostgreSQL + PostGIS, and Vue 3 / TypeScript 3D GIS
# ==============================================================================

SHELL := /bin/bash
.DEFAULT_GOAL := all

# Colors for terminal output
CYAN    := \033[1;36m
GREEN   := \033[1;32m
YELLOW  := \033[1;33m
RED     := \033[1;31m
RESET   := \033[0m

.PHONY: all build test benchmark clean services-up services-down db-init \
        backend-gateway backend-crypto backend-crawler python-test client-build client-dev

all: build test ## Build all services and run entire verification test suite
	@echo -e "$(GREEN)[SpatialForge AI] All platform services compiled and verified successfully!$(RESET)"

# ------------------------------------------------------------------------------
# 1. Compilation & Build Targets
# ------------------------------------------------------------------------------
build: backend-gateway backend-crypto backend-crawler client-build ## Build all service binaries and frontend bundle
	@echo -e "$(GREEN)[Build] All binaries and assets built cleanly.$(RESET)"

backend-gateway: ## Compile Go Core API Gateway & Orchestration Router
	@echo -e "$(CYAN)[Building] Go Core Gateway (services/core-gateway)...$(RESET)"
	@cd services/core-gateway && go build -o bin/gateway cmd/server/main.go
	@echo -e "$(GREEN)✓ Go Core Gateway binary ready: services/core-gateway/bin/gateway$(RESET)"

backend-crypto: ## Compile Rust Cryptographic Enclave (Release profile)
	@echo -e "$(CYAN)[Building] Rust Crypto Enclave (services/crypto-enclave)...$(RESET)"
	@cd services/crypto-enclave && cargo build --release
	@echo -e "$(GREEN)✓ Rust Crypto Enclave binary ready: services/crypto-enclave/target/release/spatialforge-crypto$(RESET)"

backend-crawler: ## Compile Go Stealth Scraping & Crawling Engine
	@echo -e "$(CYAN)[Building] Stealth Crawler Engine (services/stealth-crawler)...$(RESET)"
	@cd services/stealth-crawler && go build -o bin/crawler cmd/crawler/main.go
	@echo -e "$(GREEN)✓ Stealth Crawler binary ready: services/stealth-crawler/bin/crawler$(RESET)"

client-build: ## Build Vue 3 + TypeScript 3D Cesium Web Client
	@echo -e "$(CYAN)[Building] SpatialForge 3D Client...$(RESET)"
	@npm run build
	@echo -e "$(GREEN)✓ Client production bundle ready: dist/$(RESET)"

# ------------------------------------------------------------------------------
# 2. Testing & Verification Targets
# ------------------------------------------------------------------------------
test: test-gateway test-crypto test-crawler test-python ## Execute test suites across all backend and intelligence modules
	@echo -e "$(GREEN)[Test] All test suites passed with 0 failures.$(RESET)"

test-gateway: ## Test Go Core Gateway and Dispatcher
	@echo -e "$(CYAN)[Testing] Go Core Gateway...$(RESET)"
	@cd services/core-gateway && go test -v ./...

test-crypto: ## Test Rust Crypto Enclave & Merkle Proofs
	@echo -e "$(CYAN)[Testing] Rust Crypto Enclave...$(RESET)"
	@cd services/crypto-enclave && cargo test

test-crawler: ## Test Stealth Crawler & Fingerprint Engine
	@echo -e "$(CYAN)[Testing] Stealth Crawler Engine...$(RESET)"
	@cd services/stealth-crawler && go test -v ./...

test-python: ## Test Python Intelligence Engine & Root Verification Suites
	@echo -e "$(CYAN)[Testing] Python Intelligence & Adjudication Engine...$(RESET)"
	@cd services/python-intelligence && python3 -m unittest -v test_intelligence.py
	@python3 -m unittest discover -s engine -p 'test_*.py'

benchmark: ## Execute streaming throughput and risk-coverage decision benchmarks
	@echo -e "$(CYAN)[Benchmark] Executing Streaming Throughput & Ingest-to-Visible Latency Benchmark...$(RESET)"
	@python3 engine/benchmark_throughput.py
	@echo -e "$(CYAN)[Benchmark] Executing Decision Risk vs. Coverage Adversarial Benchmark...$(RESET)"
	@python3 engine/benchmark_risk_coverage.py
	@echo -e "$(GREEN)✓ All benchmark gates passed successfully.$(RESET)"

# ------------------------------------------------------------------------------
# 3. Infrastructure & Database Targets
# ------------------------------------------------------------------------------
services-up: ## Start PostgreSQL with PostGIS and Redis via Docker Compose
	@echo -e "$(CYAN)[Infra] Starting PostGIS and Redis containers...$(RESET)"
	@docker compose up -d
	@echo -e "$(GREEN)✓ PostgreSQL/PostGIS (port 5432) and Redis (port 6379) active.$(RESET)"

services-down: ## Stop local infrastructure containers
	@echo -e "$(YELLOW)[Infra] Stopping containers...$(RESET)"
	@docker compose down

db-init: ## Initialize PostGIS database schema and partitioned telemetry tables
	@echo -e "$(CYAN)[DB] Applying PostgreSQL + PostGIS schema...$(RESET)"
	@docker exec -i spatialforge-postgis psql -U spatialforge_admin -d spatialforge < storage/postgres/init_postgis.sql
	@echo -e "$(GREEN)✓ PostGIS spatial schema applied successfully.$(RESET)"

# ------------------------------------------------------------------------------
# 4. Runtime & Development Targets
# ------------------------------------------------------------------------------
run-all: ## Launch all microservices (Go Gateway, Python Intel, 3D Client) simultaneously
	@./scripts/start-all.sh

run-gateway: backend-gateway ## Run Go API Gateway & Reverse-Proxy Router on port 8080
	@echo -e "$(GREEN)[Run] Starting SpatialForge Gateway on :8080...$(RESET)"
	@./services/core-gateway/bin/gateway

run-crawler: backend-crawler ## Run Military-Grade Stealth Crawler daemon
	@echo -e "$(GREEN)[Run] Launching SOTA Stealth Crawler daemon...$(RESET)"
	@./services/stealth-crawler/bin/crawler

run-client: ## Run Vite development server for 3D Cesium Client
	@echo -e "$(GREEN)[Run] Launching SpatialForge 3D UI on :4173 / :5173...$(RESET)"
	@npm run dev

# ------------------------------------------------------------------------------
# 5. Cleanup
# ------------------------------------------------------------------------------
clean: ## Remove compiled binaries, test caches, and build artifacts
	@rm -rf services/core-gateway/bin services/stealth-crawler/bin
	@rm -rf dist .spatialforge-logs .spatialforge-cache
	@echo -e "$(YELLOW)✓ Cleaned build artifacts.$(RESET)"

help: ## Show this help message
	@echo -e "$(CYAN)SpatialForge AI Platform Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
