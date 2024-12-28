import praw
import pandas as pd
import os

# # for post in top_posts:
# #     print("Title: ", post.title)
# #     print("ID: ", post.id)
# #     print("Author: ", post.author)
# #     print("URL - ", post.url)
# #     print("Score: ", post.score)
# #     print("Comment count: ", post.num_comments)
# #     print("Created: ", post.created_utc)
# #     print("\n")


reddit = praw.Reddit(
    client_id="7K1mdKwMS65ptK-vS7fdCg",
    client_secret="4yiGbtHYHXpADtfGqJgVC4pWOo2HQQ",
    user_agent="vid-maker by Law ",
    # username="",
    # password="",
)


post_id = input("Post ID 1dm430a: ")
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
