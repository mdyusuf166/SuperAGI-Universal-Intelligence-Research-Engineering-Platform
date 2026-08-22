# cmbagent

- Project name: cmbagent
- GitHub URL: https://github.com/CMBAgents/cmbagent.git
- Purpose: Research agents for computational science
- License: LICENSE
- Version/commit used: 423a41dc11627fa57cef3ba6874b57ea8cd71aa2
- Dependencies: pyproject.toml, requirements.txt
- Python 3.11+ compatibility: Python compatibility requires review; do not assume Python 3.11+
- Why SuperAGI uses it: Scientific analysis orchestration
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/CMBAgents/cmbagent.git for upstream authorship and terms.
