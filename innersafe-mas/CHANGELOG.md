# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-22

### Added
- Initial release of innersafe-mas
- Privacy module with `InformationBottleneckPrivacyGate`
  - PII detection and anonymization (names, IDs, emails, phones)
  - Information bottleneck loss calculation
  - Client-side reconstruction capability
- Copyright module with `AdaptiveKGWWatermark`
  - Knowledge graph adapter interface
  - Adaptive watermark injection based on semantic centrality
  - Watermark verification with statistical testing
- Governance module with `GameTheoryRouter`
  - Pareto-optimal response selection
  - Dynamic weight adjustment for privacy/copyright trade-offs
  - Utility calculation and frontier analysis
- Comprehensive test suite with 80%+ coverage
- Medical MAS demo example
- Documentation and architecture guide
- CI/CD pipeline with GitHub Actions

### Features
- Domain-agnostic design (medical, legal, financial, etc.)
- Minimal dependencies (no heavy ML frameworks required)
- Type-annotated codebase for better IDE support
- Extensible knowledge graph adapter system

[0.1.0]: https://github.com/your-org/innersafe-mas/releases/tag/v0.1.0
