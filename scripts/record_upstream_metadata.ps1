$projects = @(
  @{ Name = 'langgraph'; Category = 'agents'; Url = 'https://github.com/langchain-ai/langgraph.git'; Purpose = 'Stateful graph-based agent workflows'; Integration = 'Reasoning, planning, multi-agent workflow orchestration' },
  @{ Name = 'letta'; Category = 'agents'; Url = 'https://github.com/letta-ai/letta.git'; Purpose = 'Stateful agents with long-term memory'; Integration = 'Persistent agent memory and lifecycle' },
  @{ Name = 'autogen'; Category = 'agents'; Url = 'https://github.com/microsoft/autogen.git'; Purpose = 'Multi-agent conversation and orchestration'; Integration = 'Multi-agent coordination' },
  @{ Name = 'agent-framework-samples'; Category = 'agents'; Url = 'https://github.com/microsoft/Agent-Framework-Samples.git'; Purpose = 'Examples for Microsoft Agent Framework'; Integration = 'Agent framework patterns and interoperability research' },
  @{ Name = 'open-deep-research'; Category = 'research'; Url = 'https://github.com/langchain-ai/open_deep_research.git'; Purpose = 'Open deep-research agent workflows'; Integration = 'Research search, retrieval, analysis, synthesis' },
  @{ Name = 'denario'; Category = 'research'; Url = 'https://github.com/AstroPilot-AI/Denario.git'; Purpose = 'Agentic scientific research workflow'; Integration = 'Scientific hypothesis and experiment workflows' },
  @{ Name = 'cmbagent'; Category = 'research'; Url = 'https://github.com/CMBAgents/cmbagent.git'; Purpose = 'Research agents for computational science'; Integration = 'Scientific analysis orchestration' },
  @{ Name = 'ai-scientist'; Category = 'research'; Url = 'https://github.com/SakanaAI/AI-Scientist.git'; Purpose = 'Automated scientific discovery'; Integration = 'Hypothesis generation and paper-oriented evaluation' },
  @{ Name = 'autonomous-physics-lab'; Category = 'research'; Url = 'https://github.com/open-agent-science/autonomous-physics-lab.git'; Purpose = 'Autonomous physical experimentation'; Integration = 'Experiment planning with explicit safety controls' },
  @{ Name = 'scientific-agent-skills'; Category = 'research'; Url = 'https://github.com/K-Dense-AI/scientific-agent-skills.git'; Purpose = 'Reusable scientific agent skills'; Integration = 'Scientific tool and workflow skill catalog' },
  @{ Name = 'graphrag'; Category = 'knowledge'; Url = 'https://github.com/microsoft/graphrag.git'; Purpose = 'Graph-based retrieval augmented generation'; Integration = 'Knowledge graph indexing and retrieval' },
  @{ Name = 'biomni'; Category = 'biomedical'; Url = 'https://github.com/snap-stanford/Biomni.git'; Purpose = 'Biomedical research agent'; Integration = 'Biomedical AGI and bioinformatics research' },
  @{ Name = 'deepchem'; Category = 'molecular'; Url = 'https://github.com/deepchem/deepchem.git'; Purpose = 'Machine learning for molecular and chemical science'; Integration = 'Molecular modeling and drug discovery research' },
  @{ Name = 'chemprop'; Category = 'molecular'; Url = 'https://github.com/chemprop/chemprop.git'; Purpose = 'Molecular property prediction'; Integration = 'Chemistry property prediction adapter' },
  @{ Name = 'rdkit'; Category = 'molecular'; Url = 'https://github.com/rdkit/rdkit.git'; Purpose = 'Cheminformatics and molecular representations'; Integration = 'Molecular graph and descriptor operations' },
  @{ Name = 'brian2'; Category = 'neuro'; Url = 'https://github.com/brian-team/brian2.git'; Purpose = 'Python simulator for spiking neural networks'; Integration = 'Neurocomputing experiments' },
  @{ Name = 'nest-simulator'; Category = 'neuro'; Url = 'https://github.com/nest/nest-simulator.git'; Purpose = 'Large-scale neural network simulation'; Integration = 'Neural dynamics and brain-model experiments' },
  @{ Name = 'qiskit'; Category = 'quantum'; Url = 'https://github.com/Qiskit/qiskit.git'; Purpose = 'Quantum computing SDK'; Integration = 'Quantum circuit and algorithm research' },
  @{ Name = 'pennylane'; Category = 'quantum'; Url = 'https://github.com/PennyLaneAI/pennylane.git'; Purpose = 'Quantum machine learning and differentiable programming'; Integration = 'Hybrid quantum-classical research' },
  @{ Name = 'qiskit-aer'; Category = 'quantum'; Url = 'https://github.com/Qiskit/qiskit-aer.git'; Purpose = 'High-performance quantum circuit simulation'; Integration = 'Local quantum simulation backend' },
  @{ Name = 'ros2'; Category = 'robotics'; Url = 'https://github.com/ros2/ros2.git'; Purpose = 'Robotics middleware and ecosystem'; Integration = 'Robotics AGI messaging and control boundary' },
  @{ Name = 'navigation2'; Category = 'robotics'; Url = 'https://github.com/ros-navigation/navigation2.git'; Purpose = 'ROS 2 navigation stack'; Integration = 'Autonomous navigation planning' },
  @{ Name = 'gazebo-sim'; Category = 'robotics'; Url = 'https://github.com/gazebosim/gz-sim.git'; Purpose = 'Robotics simulation'; Integration = 'Simulated robot environments' },
  @{ Name = 'isaac-lab'; Category = 'robotics'; Url = 'https://github.com/isaac-sim/IsaacLab.git'; Purpose = 'GPU-accelerated robot learning framework'; Integration = 'Robot learning and embodied simulation' },
  @{ Name = 'gymnasium'; Category = 'simulation'; Url = 'https://github.com/Farama-Foundation/Gymnasium.git'; Purpose = 'Reinforcement learning environment API'; Integration = 'Simulation AGI and reinforcement learning' },
  @{ Name = 'openhands'; Category = 'coding'; Url = 'https://github.com/All-Hands-AI/OpenHands.git'; Purpose = 'Software engineering agent platform'; Integration = 'Programming AGI and engineering workflows' },
  @{ Name = 'swe-agent'; Category = 'coding'; Url = 'https://github.com/SWE-agent/SWE-agent.git'; Purpose = 'Agent for software engineering tasks'; Integration = 'Issue resolution and code maintenance research' },
  @{ Name = 'open-interpreter'; Category = 'computer_control'; Url = 'https://github.com/OpenInterpreter/open-interpreter.git'; Purpose = 'Natural-language computer control'; Integration = 'Sandboxed computer-control tools' },
  @{ Name = 'model-context-protocol'; Category = 'protocols'; Url = 'https://github.com/modelcontextprotocol.git'; Purpose = 'Tool and context interoperability protocol'; Integration = 'MCP tool and resource interoperability' },
  @{ Name = 'coral'; Category = 'evolution'; Url = 'https://github.com/Human-Agent-Society/CORAL.git'; Purpose = 'Agent evaluation and evolution research'; Integration = 'Continuous evaluation and controlled self-improvement' }
)

$root = Split-Path -Parent $PSScriptRoot
$docs = Join-Path $root 'docs\upstream'
New-Item -ItemType Directory -Force -Path $docs | Out-Null
$rows = [System.Collections.Generic.List[string]]::new()
$rows.Add('| Project | URL | Category | License | Purpose | SuperAGI Integration |')
$rows.Add('|---|---|---|---|---|---|')
$matrix = [System.Collections.Generic.List[string]]::new()
$matrix.Add('# Integration Matrix')
$matrix.Add('')
$matrix.Add('SuperAGI is an experimental modular AGI research and scientific intelligence platform. The mappings below describe study and adapter targets, not claims of human-level AGI.')
$matrix.Add('')
foreach ($project in $projects) {
  $path = Join-Path $root "third_party\$($project.Category)\$($project.Name)"
  $commit = 'Not cloned or incomplete'
  if (Test-Path (Join-Path $path '.git')) {
    $commitResult = git -c safe.directory=* -C $path rev-parse HEAD 2>$null
    if ($LASTEXITCODE -eq 0) { $commit = ($commitResult | Out-String).Trim() }
  }
  $licenseFiles = @(Get-ChildItem -Path $path -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(LICENSE|COPYING)' } | Select-Object -ExpandProperty Name)
  $license = if ($licenseFiles.Count) { $licenseFiles -join ', ' } else { 'License file not detected; inspect upstream repository' }
  $dependencyFiles = @(Get-ChildItem -Path $path -File -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^(pyproject.toml|setup.py|setup.cfg|requirements.*|environment.*|package.json|CMakeLists.txt|package.xml)$' } | Select-Object -First 8 -ExpandProperty Name -Unique)
  $deps = if ($dependencyFiles.Count) { $dependencyFiles -join ', ' } else { 'No standard dependency manifest detected' }
  $compatibility = if ($dependencyFiles -match 'pyproject.toml|setup.py|setup.cfg|requirements|environment') { 'Python compatibility requires review; do not assume Python 3.11+' } else { 'Python 3.11+ compatibility requires project-specific review' }
  $content = @("# $($project.Name)", '', "- Project name: $($project.Name)", "- GitHub URL: $($project.Url)", "- Purpose: $($project.Purpose)", "- License: $license", "- Version/commit used: $commit", "- Dependencies: $deps", "- Python 3.11+ compatibility: $compatibility", "- Why SuperAGI uses it: $($project.Integration)", '- Capabilities: Study the upstream project through an adapter boundary for the integration targets above.', '- What we will NOT copy: No blind source copying, no removal of notices, and no upstream implementation details in SuperAGI core.', '- Integration strategy: Keep the checkout under `third_party/`; expose a narrow optional adapter under `src/superagi/integrations/`; add focused tests before enabling runtime use.', '- Limitations: Licensing, platform support, transitive dependencies, model/provider requirements, and operational safety remain project-specific.', "- Attribution: Copyright and license notices remain in the upstream checkout. See $($project.Url) for upstream authorship and terms.")
  Set-Content -Path (Join-Path $docs "$($project.Name).md") -Value $content -Encoding utf8
  $rows.Add("| $($project.Name) | $($project.Url) | $($project.Category) | $license | $($project.Purpose) | $($project.Integration) |")
  $matrix.Add("## $($project.Name)")
  $matrix.Add("- Category: $($project.Category)")
  $matrix.Add("- Maps to: $($project.Integration)")
  $matrix.Add('')
}
Set-Content -Path (Join-Path $root 'docs\UPSTREAM_PROJECTS.md') -Value ($rows -join "`n") -Encoding utf8
Set-Content -Path (Join-Path $root 'docs\INTEGRATION_MATRIX.md') -Value ($matrix -join "`n") -Encoding utf8
