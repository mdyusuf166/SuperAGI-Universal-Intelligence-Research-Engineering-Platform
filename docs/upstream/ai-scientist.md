# ai-scientist

- Project name: ai-scientist
- GitHub URL: https://github.com/SakanaAI/AI-Scientist.git
- Purpose: Automated scientific discovery
- License: LICENSE
- Version/commit used: 1de1dbc1f4ee2c5f61e9c94348d55eb51d7fa2eb
- Dependencies: requirements.txt
- Python 3.11+ compatibility: Python compatibility requires review; do not assume Python 3.11+
- Why SuperAGI uses it: Hypothesis generation and paper-oriented evaluation
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/SakanaAI/AI-Scientist.git for upstream authorship and terms.
