from dataclasses import dataclass

@dataclass
class MoguchiData:
	flow_temperature: float = 0
	burner_modulation: float = 0
	burner_state: bool = False
	heating_circuit_state: bool = False
	water_circuit_state: bool = False