# Test Structure Reorganization Plan

## Current State
- **Total test files**: 101
- **Issues**: 
  - Tests scattered across multiple directories
  - Duplicate WebSocket tests (20+ files)
  - Import and environment tests mixed with functional tests
  - No clear separation between unit, integration, and system tests

## Target Structure

```
tests/
├── __init__.py
├── conftest.py                    # Global test configuration
├── pytest.ini                    # Moved from root
├── unit/                         # Unit tests (isolated, fast)
│   ├── __init__.py
│   ├── core/
│   │   ├── test_algorithms.py
│   │   ├── test_cache.py
│   │   ├── test_config.py
│   │   └── test_validators.py
│   ├── services/
│   │   ├── test_nft_service.py
│   │   ├── test_portfolio_service.py
│   │   ├── test_price_service.py
│   │   └── test_security_analyzer.py
│   └── utils/
│       ├── test_address_symmetry.py
│       ├── test_entropy.py
│       └── test_simhash.py
├── integration/                  # Integration tests (moderate speed)
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── test_assets.py
│   │           ├── test_collections.py
│   │           ├── test_markets.py
│   │           ├── test_nfts.py
│   │           ├── test_portfolios.py
│   │           ├── test_ranking.py
│   │           ├── test_traits.py
│   │           ├── test_wallet_analysis.py
│   │           └── test_wallets.py
│   ├── live/
│   │   ├── test_blockchain_integration.py
│   │   └── test_event_listener.py
│   └── portfolio/
│       ├── test_portfolio_integration.py
│       └── test_analytics_integration.py
├── system/                       # End-to-end system tests (slow)
│   ├── __init__.py
│   ├── test_full_api_workflow.py
│   ├── test_websocket_system.py
│   └── test_security_system.py
├── performance/                  # Performance tests
│   ├── __init__.py
│   ├── test_api_performance.py
│   └── test_websocket_load.py
├── fixtures/                     # Test data and fixtures
│   ├── __init__.py
│   ├── api_responses/
│   ├── blockchain_data/
│   └── portfolio_data/
└── deprecated/                   # Temporary holding for old tests
    └── websocket_legacy/
```

## Reorganization Strategy

### Phase 1: Create New Structure
1. Create target directories
2. Move properly organized tests first
3. Create comprehensive conftest.py

### Phase 2: Consolidate WebSocket Tests
1. Merge 20+ WebSocket test files into:
   - `unit/test_ws_manager.py`
   - `integration/test_websocket_api.py` 
   - `system/test_websocket_system.py`

### Phase 3: Categorize Remaining Tests
1. **Unit tests**: Core logic, utilities, individual services
2. **Integration tests**: API endpoints, database interactions
3. **System tests**: Full workflows, security scenarios

### Phase 4: Remove Duplicates and Diagnostics
1. Remove diagnostic tests (test_imports.py, test_env.py, etc.)
2. Remove duplicate tests
3. Archive legacy tests in deprecated folder

## Success Metrics
- ✅ Reduce from 101 to ~40 meaningful test files
- ✅ Clear separation of concerns
- ✅ Fast unit tests (<1s each)
- ✅ Reliable integration tests
- ✅ Comprehensive system tests
- ✅ Easy test discovery and execution

## Test Execution Strategy
```bash
# Run all tests
pytest

# Run only fast unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run system tests (slow)
pytest tests/system/

# Run performance tests
pytest tests/performance/ --slow
```
