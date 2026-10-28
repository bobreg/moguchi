from dataclasses import dataclass

@dataclass
class MoguchiData:
	flow_temperature: float
	burner_modulation: float
	burner_state: bool