import re
import pandas as pd

def preprocess(data):
    # WhatsApp chat line pattern
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s[ap]m) - (.*)'

    matches = re.findall(pattern, data)

    # Create initial DataFrame
    df = pd.DataFrame(matches, columns=['date', 'time', 'user_message'])

    # Convert date and time properly
    # Try flexible date format because WhatsApp exports can be dd/mm/yy or dd/mm/yyyy
    df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
    df['time'] = pd.to_datetime(df['time'], format='%I:%M %p', errors='coerce').dt.time

    # Split user and message
    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
        if len(entry) > 2:   # If username and message both exist
            users.append(entry[1])
            messages.append(entry[2])
        else:                # System messages like "ABC left" or "Messages to this group..."
            users.append('group_notification')
            messages.append(entry[0])

    # Add user & message columns
    df['user'] = users
    df['message'] = messages

    # Drop the combined column
    df.drop(columns=['user_message'], inplace=True)

    # Add a combined datetime column
    df['datetime'] = pd.to_datetime(
        df['date'].astype(str) + ' ' + df['time'].astype(str),
        errors='coerce'
    )

    # Extract useful time components
    df['only_date'] = df['datetime'].dt.date
    df['year'] = df['datetime'].dt.year
    df['month_num'] = df['datetime'].dt.month
    df['month'] = df['datetime'].dt.month_name()
    df['day'] = df['datetime'].dt.day
    df['day_name'] = df['datetime'].dt.day_name()
    df['hour'] = df['datetime'].dt.hour
    df['minute'] = df['datetime'].dt.minute

    # Define time periods (hour ranges)
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour+1}")
    df['period'] = period

    return df

