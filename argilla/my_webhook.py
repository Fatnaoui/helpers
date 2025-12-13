# my_webhook.py
# export WEBHOOK_SERVER_URL=http://host.docker.internal:8000
# uvicorn my_webhook:server --host 0.0.0.0 --port 8000

import argilla as rg
from argilla.webhooks import webhook_listener, get_webhook_server
from datetime import datetime

API_URL = "http://localhost:6900"
API_KEY = "fatnaoui.apikey"

rg.Argilla(API_URL, API_KEY)

client = rg.Argilla(
    api_url=API_URL,
    api_key=API_KEY,
)

dataset = client.datasets(name="Darija_validation")

@webhook_listener(events=["record.completed"])
async def my_webhook_handler(record: rg.Record, type: str, timestamp: datetime):
    print("##########################")
    print(record)
    print(dataset)
    print("##########################")
    status = getattr(record, "status")
    print(str(status))
    fields = getattr(record, "fields")
    text = fields["text"]
    print(text)
    responses = getattr(record, "responses")
    language = responses["language"]
    value = language[0]
    value = getattr(value,"value")
    print(value)
    if str(status) == "completed":
    	print("everything is okay")
    	data = [{"text": text,"language": value}]
    	dataset.records.log(data)
    	
server = get_webhook_server()

