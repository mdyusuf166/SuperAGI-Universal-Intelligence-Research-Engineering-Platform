# autonomous-physics-lab

- Project name: autonomous-physics-lab
- GitHub URL: https://github.com/open-agent-science/autonomous-physics-lab.git
- Purpose: Autonomous physical experimentation
- License: LICENSE
- Version/commit used: 60f47e5ff7dae4035a8431448601fd60087b2062
- Dependencies: pyproject.toml
- Python 3.11+ compatibility: Python compatibility requires review; do not assume Python 3.11+
- Why SuperAGI uses it: Experiment planning with explicit safety controls
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/open-agent-science/autonomous-physics-lab.git for upstream authorship and terms.
