from slackclient import SlackClient
import openspaces.secrets as s

slack_client = SlackClient(s.BOT_TOKEN)

attachments_json_button = [
    { 
        "fallback": "You are unable to appove a tweet", 
        "callback_id": "tweet_approval", 
        "color": "#3AA3E3", 
        "attachment_type": "default",
        "actions": [
            {
                "name": "approval", 
                "text": "Yes", 
                "type": "button", 
                "value": "yes"
            }, 
            {
                "name": "approval", 
                "text": "No", 
                "type": "button", 
                "value": "no"
            }
        ]
    }
]

attachments_json_drop_down = [
    {
        "text": "Choose a game to play",
        "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "callback_id": "message_type|12345",
        "actions": [
            {
                "name": "options1",
                "text": "Needs action",
                "type": "select",
                "options": [
                    {
                        "text": "A",
                        "value": "A"
                    },
                    {
                        "text": "B",
                        "value": "B"
                    },
                    {
                        "text": "C",
                        "value": "C"
                    }
                ]
            },
            {
                "name": "approved",
                "text": "Needs action",
                "type": "select",
                "options": [
                    {
                        "text": "Needs action",
                        "value": "Needs action"
                    },
                    {
                        "text": "Approved",
                        "value": "Approved"
                    },
                    {
                        "text": "Denied",
                        "value": "Denied"
                    }
                ]
            },
            {
                "name": "approval",
                "text": "Yes",
                "type": "button",
                "value": "yes"
            }
        ]
    }
]

slack_client.api_call(
    "chat.postMessage",
    channel="C9F750BQW",
    text="Do you approve this tweet?",
    #replace_original=True,
    #response_type="in_channel",
    attachments=attachments_json_drop_down
)

# slack_client.api_call(
#     "chat.postMessage",
#     channel="C9F750BQW",
#     text="Would you like to play a game?",
#     attachments=attachements_json_drop_down
# )
