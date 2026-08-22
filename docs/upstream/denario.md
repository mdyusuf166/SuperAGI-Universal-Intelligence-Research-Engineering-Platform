# denario

- Project name: denario
- GitHub URL: https://github.com/AstroPilot-AI/Denario.git
- Purpose: Agentic scientific research workflow
- License: LICENSE
- Version/commit used: be9d00856c96c0c1002427629b181606fb364995
- Dependencies: pyproject.toml, requirements.txt
- Python 3.11+ compatibility: Python compatibility requires review; do not assume Python 3.11+
- Why SuperAGI uses it: Scientific hypothesis and experiment workflows
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/AstroPilot-AI/Denario.git for upstream authorship and terms.
