# Change Log for Twitter Schedule Organizer Bot

Here's our plan and build progress on the Twitter+Slack Bot to manage and promote a self-service event schedule, using Twitter and Slack.

## Plan


### MVP (V0.1, April 1)

Need to prioritize tasks below and put only “must haves”.

Initial Release (V1, April 1)

[ ] AO: "reserve" several bot usernames on twitter: @openspaces, @pyconopenspaces, @pyconospace, @opensched, @openspacesched
[x] HL: daemon for snarfing tweets
[ ] HH: celery task for snarfing tweets
[x] HL: Django app + DB for storing/viewing tweet archive
[x] ZK: API for retrieving/searching tweets
[x] SA:integration with slack
[ ]  SA: Add twitter API out of the box filters for bot: (filter:safe, filter:url, filter:image, filter:media, result_type:popular etc.)
[x] ZK: API for retrieving labeled trainings sets (strict filter)
[ ] HL+ZK: Model trained to score tweets 0-1 for relevance to "pycon open space schedule"
[ ] HL+ZK: Model trained to score tweets 0-1 for spamminess (anti-socialness)
[ ] HL: Database table to hold outgoing tweet cue
[ ] SA? ZK?: Web interface for deleting tweets from cue (admin interface is fine)
[x] SA: schedule extractor (datetime and room number) from tweet
[ ] RR: database table for openspaces schedule
[ ] HL/RR: database table for history/log of edits to that schedule
[ ] HL/RR: database field/table for storing scores for tweets (spam-ness, openspaces-ness)
[ ] HL: Summarizing algorithm to combine neighboring schedule items (overlapping times, different room) into single tweet
[ ] SA? ZK?: Webapp control of throttle to determine tweet rate maximum (including off)
[ ] SA? ZK?: Webapp control of a spam-filtering threshold
[ ] SA? ZK?:  Web page presenting latest estimate of openspaces schedule
[ ] SA? ZK?:  Web page presenting image of official posterboard schedule 
[ ] HL: Twitter or Slack bot command for sending/sharing an image to be posted on the schedul page
[ ] ZK: API endpoint for uploading image of pycon openspaces posterboard schedule
[ ] SA: Configurable switches to control bot input and output (controled by django admin):
  1: accept input from 4 sources: DMs, @pyconopenspaces, #pyconopenspaces, and/or relevant but untagged tweets
  2: route output to one of 2 destinations: tweets to slack #twitter channel and/or actual twitter tweets

### Enhancements (V2)