# langgraph

- Project name: langgraph
- GitHub URL: https://github.com/langchain-ai/langgraph.git
- Purpose: Stateful graph-based agent workflows
- License: LICENSE
- Version/commit used: f09cfe8ffc1eeffd68f4b628ed69c30f7cad229f
- Dependencies: pyproject.toml
- Python 3.11+ compatibility: Python compatibility requires review; do not assume Python 3.11+
- Why SuperAGI uses it: Reasoning, planning, multi-agent workflow orchestration
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/langchain-ai/langgraph.git for upstream authorship and terms.
