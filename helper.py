from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
from emoji import EMOJI_DATA
import os



extract = URLExtract()

# ---------------------- Fetch Stats ----------------------
def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'].str.contains('<Media omitted>', case=False, na=False)].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


# ---------------------- Most Busy Users ----------------------
def most_busy_users(df):
    # top 5 most active users
    x = df['user'].value_counts().head()
    # percentage contribution of each user
    df_percent = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    # rename columns properly
    df_percent.columns = ['name', 'percent']

    return x, df_percent


# ---------------------- WordCloud ----------------------
def create_wordcloud(selected_user, df):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stopwords_path = os.path.join(base_dir, "stop_hinglish.txt")

    with open(stopwords_path, "r", encoding="utf-8") as f:
        stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    text = " ".join(temp['message'])

    wc = WordCloud(
        width=500,
        height=500,
        min_font_size=10,
        background_color='white',
        stopwords=set(stop_words.split())
    )

    df_wc = wc.generate(text)
    return df_wc



# ---------------------- Most Common Words ----------------------
def most_common_words(selected_user, df):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stopwords_path = os.path.join(base_dir, "stop_hinglish.txt")

    with open(stopwords_path, "r", encoding="utf-8") as f:
        stop_words = f.read().split()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words and word not in ('<media', 'omitted>'):
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []

    for message in df['message']:
        emojis.extend([c for c in message if c in EMOJI_DATA])

    emoji_df = pd.DataFrame(
        Counter(emojis).most_common(),
        columns=['Emoji', 'Count']
    )

    return emoji_df


def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap