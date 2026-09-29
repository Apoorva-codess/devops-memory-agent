import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY"),
)

bank_id = os.getenv("HINDSIGHT_BANK_ID")

client.retain(
    bank_id=bank_id,
    content="Test deployment: payments-service had a database migration rollback. The team resolved it with a staged rollout.",
)

result = client.recall(
    bank_id=bank_id,
    query="What happened during the payments service database migration?",
)

print("Hindsight connected. Memories found:")
for memory in result.results:
    print("-", memory.text)
