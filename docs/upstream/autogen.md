# autogen

- Project name: autogen
- GitHub URL: https://github.com/microsoft/autogen.git
- Purpose: Multi-agent conversation and orchestration
- License: LICENSE, LICENSE-CODE
- Version/commit used: 027ecf0a379bcc1d09956d46d12d44a3ad9cee14
- Dependencies: EnvironmentSpecificFactAttribute.cs, pyproject.toml, setup.py, requirements.txt
- Python 3.11+ compatibility: Python compatibility requires review; do not assume Python 3.11+
- Why SuperAGI uses it: Multi-agent coordination
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/microsoft/autogen.git for upstream authorship and terms.
