# letta

- Project name: letta
- GitHub URL: https://github.com/letta-ai/letta.git
- Purpose: Stateful agents with long-term memory
- License: LICENSE
- Version/commit used: 87fd37aab68c7bdd0d66fe63751553756f6af3e5
- Dependencies: No standard dependency manifest detected
- Python 3.11+ compatibility: Python 3.11+ compatibility requires project-specific review
- Why SuperAGI uses it: Persistent agent memory and lifecycle
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/letta-ai/letta.git for upstream authorship and terms.
