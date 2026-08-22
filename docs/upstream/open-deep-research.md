# open-deep-research

- Project name: open-deep-research
- GitHub URL: https://github.com/langchain-ai/open_deep_research.git
- Purpose: Open deep-research agent workflows
- License: LICENSE
- Version/commit used: 1b7d2e80db9faa586165c60e09096dbbfd483a64
- Dependencies: pyproject.toml
- Python 3.11+ compatibility: Python compatibility requires review; do not assume Python 3.11+
- Why SuperAGI uses it: Research search, retrieval, analysis, synthesis
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/langchain-ai/open_deep_research.git for upstream authorship and terms.
