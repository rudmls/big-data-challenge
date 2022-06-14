
iso_time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

media_fields = [
    "duration_ms", "height", "media_key", "preview_image_url",
    "type", "url", "width", "public_metrics", "alt_text"]

place_fields = [
    "contained_within", "country", "country_code",
    "full_name", "geo", "id", "name", "place_type"]

poll_fields = [
    "duration_minutes", "end_datetime", "id", "options", "voting_status"]

user_fields = [
    'created_at', 'description', 'entities', 'id', 'location',
    'name', 'pinned_tweet_id', 'profile_image_url', 'protected',
    'public_metrics', 'url', 'username', 'verified', 'withheld']

tweet_fields = [
    "created_at", "attachments", "geo", "author_id", "entities",
    "conversation_id", "in_reply_to_user_id", "lang", "public_metrics",
    "possibly_sensitive", "referenced_tweets", "reply_settings", "source", "withheld"]

expansions = [
    "attachments.poll_ids", "attachments.media_keys", "author_id", "entities.mentions.username",
    "geo.place_id", "in_reply_to_user_id", "referenced_tweets.id", "referenced_tweets.id.author_id"]
