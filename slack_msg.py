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

attachements_json_drop_down = [
    {
        "text": "Choose a game to play",
        "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "callback_id": "game_selection",
        "actions": [
            {
                "name": "games_list",
                "text": "Pick a game...",
                "type": "select",
                "options": [
                    {
                        "text": "Hearts",
                        "value": "hearts"
                    },
                    {
                        "text": "Bridge",
                        "value": "bridge"
                    },
                    {
                        "text": "Checkers",
                        "value": "checkers"
                    },
                    {
                        "text": "Chess",
                        "value": "chess"
                    },
                    {
                        "text": "Poker",
                        "value": "poker"
                    },
                    {
                        "text": "Falken's Maze",
                        "value": "maze"
                    },
                    {
                        "text": "Global Thermonuclear War",
                        "value": "war"
                    }
                ]
            }
        ]
    }
]

slack_client.api_call(
    "chat.postMessage",
    channel="C9F750BQW",
    text="Do you approve this tweet?",
    attachments=attachments_json_button
)

# slack_client.api_call(
#     "chat.postMessage",
#     channel="C9F750BQW",
#     text="Would you like to play a game?",
#     attachments=attachements_json_drop_down
# )
