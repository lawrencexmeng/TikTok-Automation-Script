import praw
import pandas as pd
import os



reddit = praw.Reddit(
    client_id="REDDIT_CLIENT_ID",
    client_secret="REDDIT_CLIENT_SECRET",
    user_agent="vid-maker by Law ",
    # username="",
    # password="",
)


post_id = input("Post ID: ")
csv_file_path = r'C:\Users\lawre\Desktop\TikTok Posting Script\post_info.csv'

if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path, index_col = 0)
else:
    df = pd.DataFrame(columns = ['Title', 'Author', 'Content', 'ID'])

post = reddit.submission(id=post_id)

data = {
    'Title': post.title,
    'Author': post.author,
    'Content': post.selftext,
    'ID': post.id
}

if post.id not in df['ID'].values:
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
else:
    print("Post already stored")   

df.to_csv('post_info.csv')
print(df)
