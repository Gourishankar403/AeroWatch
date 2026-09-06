import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.providers.faa_provider import FAAProvider


provider = FAAProvider()

result = provider.get_airport_status("HTS")

print(result.model_dump_json(indent=2))