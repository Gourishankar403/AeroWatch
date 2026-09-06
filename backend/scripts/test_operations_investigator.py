from app.agents.operations_investigator import OperationsInvestigator


investigator = OperationsInvestigator()

result = investigator.investigate("HTS")

print(result.model_dump_json(indent=2))