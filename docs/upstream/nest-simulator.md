# nest-simulator

- Project name: nest-simulator
- GitHub URL: https://github.com/nest/nest-simulator.git
- Purpose: Large-scale neural network simulation
- License: License file not detected; inspect upstream repository
- Version/commit used: Not cloned or incomplete
- Dependencies: No standard dependency manifest detected
- Python 3.11+ compatibility: Python 3.11+ compatibility requires project-specific review
- Why SuperAGI uses it: Neural dynamics and brain-model experiments
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/nest/nest-simulator.git for upstream authorship and terms.
