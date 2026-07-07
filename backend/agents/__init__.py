"""
FitMind AI — Multi-Agent System Package

Ekspor semua komponen agent agar mudah diimport dari luar.

Hierarki:
  SupervisorAgent  (Orchestrator)
    ├── FitnessAgent   (Spesialis latihan & gym)
    ├── NutritionAgent (Spesialis nutrisi & makanan)
    └── HealthAgent    (Spesialis BMI & analisis kesehatan)
"""
from agents.base_agent import BaseAgent
from agents.fitness_agent import FitnessAgent
from agents.nutrition_agent import NutritionAgent
from agents.health_agent import HealthAgent
from agents.supervisor import SupervisorAgent, AGENT_REGISTRY

__all__ = [
    "BaseAgent",
    "FitnessAgent",
    "NutritionAgent",
    "HealthAgent",
    "SupervisorAgent",
    "AGENT_REGISTRY",
]
