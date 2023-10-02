# THE PYTHON SDK IS IN PREVIEW. FOR NON-PRODUCTION USE ONLY
from msgraph import GraphServiceClient
import asyncio

graph_client = GraphServiceClient(request_adapter)

request_body = Message(
	subject = "Did you see last night's game?",
	importance = Importance.Low,
	body = ItemBody(
		content_type = BodyType.Html,
		content = "They were <b>awesome</b>!",
	),
	to_recipients = [
		Recipient(
			email_address = EmailAddress(
				address = "luis.herrera@axity.com",
			),
		),
	]
)

result = await graph_client.me.messages.post(body = request_body)





def send_msteams_card(card,url):
    card_msteams = {
        "type":"message",
        "attachments":[card]
    }
    msteams_payload = json.dumps(card_msteams)
    msteams_headers = {
        "Content-Type": "application/json"
    }
    msteams_msg = requests.request('POST', msteamsurl, headers=msteams_headers, data=msteams_payload)