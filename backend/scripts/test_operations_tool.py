import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.tools.operations_tool import OperationsTool

tool=OperationsTool()

result=tool.investigate_airport("HIS")

print(result.model_dump_json(indent=42))

