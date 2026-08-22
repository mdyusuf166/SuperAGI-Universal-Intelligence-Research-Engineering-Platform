$projects = @(
  @{ Category = 'agents'; Name = 'langgraph'; Url = 'https://github.com/langchain-ai/langgraph.git' },
  @{ Category = 'agents'; Name = 'letta'; Url = 'https://github.com/letta-ai/letta.git' },
  @{ Category = 'agents'; Name = 'autogen'; Url = 'https://github.com/microsoft/autogen.git' },
  @{ Category = 'agents'; Name = 'agent-framework-samples'; Url = 'https://github.com/microsoft/Agent-Framework-Samples.git' },
  @{ Category = 'research'; Name = 'open-deep-research'; Url = 'https://github.com/langchain-ai/open_deep_research.git' },
  @{ Category = 'research'; Name = 'denario'; Url = 'https://github.com/AstroPilot-AI/Denario.git' },
  @{ Category = 'research'; Name = 'cmbagent'; Url = 'https://github.com/CMBAgents/cmbagent.git' },
  @{ Category = 'research'; Name = 'ai-scientist'; Url = 'https://github.com/SakanaAI/AI-Scientist.git' },
  @{ Category = 'research'; Name = 'autonomous-physics-lab'; Url = 'https://github.com/open-agent-science/autonomous-physics-lab.git' },
  @{ Category = 'research'; Name = 'scientific-agent-skills'; Url = 'https://github.com/K-Dense-AI/scientific-agent-skills.git' },
  @{ Category = 'knowledge'; Name = 'graphrag'; Url = 'https://github.com/microsoft/graphrag.git' },
  @{ Category = 'biomedical'; Name = 'biomni'; Url = 'https://github.com/snap-stanford/Biomni.git' },
  @{ Category = 'molecular'; Name = 'deepchem'; Url = 'https://github.com/deepchem/deepchem.git' },
  @{ Category = 'molecular'; Name = 'chemprop'; Url = 'https://github.com/chemprop/chemprop.git' },
  @{ Category = 'molecular'; Name = 'rdkit'; Url = 'https://github.com/rdkit/rdkit.git' },
  @{ Category = 'neuro'; Name = 'brian2'; Url = 'https://github.com/brian-team/brian2.git' },
  @{ Category = 'neuro'; Name = 'nest-simulator'; Url = 'https://github.com/nest/nest-simulator.git' },
  @{ Category = 'quantum'; Name = 'qiskit'; Url = 'https://github.com/Qiskit/qiskit.git' },
  @{ Category = 'quantum'; Name = 'pennylane'; Url = 'https://github.com/PennyLaneAI/pennylane.git' },
  @{ Category = 'quantum'; Name = 'qiskit-aer'; Url = 'https://github.com/Qiskit/qiskit-aer.git' },
  @{ Category = 'robotics'; Name = 'ros2'; Url = 'https://github.com/ros2/ros2.git' },
  @{ Category = 'robotics'; Name = 'navigation2'; Url = 'https://github.com/ros-navigation/navigation2.git' },
  @{ Category = 'robotics'; Name = 'gazebo-sim'; Url = 'https://github.com/gazebosim/gz-sim.git' },
  @{ Category = 'robotics'; Name = 'isaac-lab'; Url = 'https://github.com/isaac-sim/IsaacLab.git' },
  @{ Category = 'simulation'; Name = 'gymnasium'; Url = 'https://github.com/Farama-Foundation/Gymnasium.git' },
  @{ Category = 'coding'; Name = 'openhands'; Url = 'https://github.com/All-Hands-AI/OpenHands.git' },
  @{ Category = 'coding'; Name = 'swe-agent'; Url = 'https://github.com/SWE-agent/SWE-agent.git' },
  @{ Category = 'computer_control'; Name = 'open-interpreter'; Url = 'https://github.com/OpenInterpreter/open-interpreter.git' },
  @{ Category = 'protocols'; Name = 'model-context-protocol'; Url = 'https://github.com/modelcontextprotocol.git' },
  @{ Category = 'evolution'; Name = 'coral'; Url = 'https://github.com/Human-Agent-Society/CORAL.git' }
)

$root = Split-Path -Parent $PSScriptRoot
foreach ($project in $projects) {
  $target = Join-Path $root "third_party\$($project.Category)\$($project.Name)"
  if ((Test-Path (Join-Path $target '.git')) -and (git -c safe.directory=* -C $target rev-parse --verify HEAD 2>$null)) {
    Write-Output "EXISTS $($project.Name)"
    continue
  }
  if (Test-Path $target) { Remove-Item -Recurse -Force $target }
  New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
  Write-Output "CLONING $($project.Name)"
  git clone --depth 1 $project.Url $target
  if ($LASTEXITCODE -ne 0) { Write-Output "FAILED $($project.Name)" }
}
