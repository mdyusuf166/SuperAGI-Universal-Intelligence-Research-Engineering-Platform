# agent-framework-samples

- Project name: agent-framework-samples
- GitHub URL: https://github.com/microsoft/Agent-Framework-Samples.git
- Purpose: Examples for Microsoft Agent Framework
- License: LICENSE
- Version/commit used: 5b854b7e1c3838f17f41bcf2412ef79d7662db37
- Dependencies: package.json, requirements.txt
- Python 3.11+ compatibility: Python compatibility requires review; do not assume Python 3.11+
- Why SuperAGI uses it: Agent framework patterns and interoperability research
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/microsoft/Agent-Framework-Samples.git for upstream authorship and terms.
