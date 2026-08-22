# gymnasium

- Project name: gymnasium
- GitHub URL: https://github.com/Farama-Foundation/Gymnasium.git
- Purpose: Reinforcement learning environment API
- License: License file not detected; inspect upstream repository
- Version/commit used: Not cloned or incomplete
- Dependencies: No standard dependency manifest detected
- Python 3.11+ compatibility: Python 3.11+ compatibility requires project-specific review
- Why SuperAGI uses it: Simulation AGI and reinforcement learning
- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.
- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.
- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.
- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.
- Attribution: Copyright and license notices remain in the upstream checkout. See https://github.com/Farama-Foundation/Gymnasium.git for upstream authorship and terms.
