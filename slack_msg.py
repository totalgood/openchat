from slackclient import SlackClient
import openspaces.secrets as s

slack_client = SlackClient(s.BOT_TOKEN)

attachments_json_drop_down = [
    {
        "text": "Tweet body here",
        "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "title": "User name here: fake-user",
        "callback_id": "message_type|12345",
        "actions": [
            {
                "name": "Time of event",
                "text": "Choose event time",
                "type": "select",
                "option_groups": [
                    {
                        "text": "Time of event",
                        "options": [
                            {
                                "text": "9:00",
                                "value": "09:00"
                            },
                            {
                                "text": "10:00",
                                "value": "10:00"
                            },
                            {
                                "text": "11:00",
                                "value": "11:00"
                            },
                            {
                                "text": "12:00",
                                "value": "12:00"
                            },
                            {
                                "text": "13:00",
                                "value": "13:00"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Room",
                "text": "Choose room",
                "type": "select",
                "option_groups": [
                    {
                        "text": "Event room",
                        "options": [
                            {
                                "text": "A112",
                                "value": "A112"
                            },
                            {
                                "text": "B114",
                                "value": "B114"
                            },
                            {
                                "text": "C115",
                                "value": "C115"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "approved",
                "text": "Needs approval",
                "type": "select",
                "option_groups": [
                    {
                        "text": "Approve/deny tweet",
                        "options": [
                            {
                                "text": "Approve",
                                "value": "Approve"
                            },
                            {
                                "text": "Deny",
                                "value": "Deny"
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Submit",
                "text": "Submit",
                "type": "button",
                "style": "primary",
                "value": "submit"
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
