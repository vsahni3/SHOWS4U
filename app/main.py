from flask import Flask, render_template, request
from .tools.web_scraping import get_urls
from .tools.web_scraping import web_scrape
from time import time
from math import ceil
import sqlite3
app = Flask(__name__)
# uss css media queries and class_name depending on the image number
# eg i=0, i=1 -> class column1 column2, etc
conn = sqlite3.connect('titles.db')

cursor = conn.cursor()
cursor.execute("""DROP TABLE IF EXISTS ANIME_FILTERED""")
cursor.execute("""DROP TABLE IF EXISTS ANIME_FULL""")
cursor.execute('''CREATE TABLE IF NOT EXISTS ANIME_FULL(name TEXT PRIMARY KEY, image TEXT, duration TEXT, year TEXT, genres TEXT, age_rating TEXT, rating TEXT, id TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS ANIME_FILTERED(name TEXT PRIMARY KEY, image TEXT, duration TEXT, year TEXT, genres TEXT, age_rating TEXT, rating TEXT, id TEXT)''')
conn.commit()
conn.close()
def calc_maxes(data, num_maxes):
  mapper = {}
  for item in data:
      if item in mapper:
        mapper[item] += 1
      else:
        mapper[item] = 1

  mapper[''] = 0
  maxes = [''] * num_maxes
  for search in mapper:
    count = mapper[search]
    
    for i in range(len(maxes)):
        if count > mapper[maxes[i]]:
            for j in range(len(maxes) - 1, i, -1):
                maxes[j] = maxes[j - 1]
            maxes[i] = search
            break
  return maxes


def sort_data(data):
  if len(data) <= 3:
    return data
  else: 
    num_rows = ceil(len(data) / 3)
    num_cols = ceil(len(data) / num_rows)
    new_data = []
    for i in range(num_cols):
      for j in range(num_rows):
        if i + j * num_cols < len(data):
          new_data.append(data[i + j * num_cols])
    if len(new_data) != len(data):
      return data
    return new_data


@app.route("/")
def hello():
    searches_db = list(open('app/tools/web_scraping/searches.txt').read().split('!|?'))
    searches_maxes = calc_maxes(searches_db, 4)
    searches_maxes = [(i+1, searches_maxes[i].title()) for i in range(len(searches_maxes))]
    chosen_anime_db = list(open('app/tools/web_scraping/chosen_anime.txt').read().split('!|?'))
    chosen_anime_maxes = calc_maxes(chosen_anime_db, 8)
    anime_data = web_scrape.give_image(chosen_anime_maxes)
    return render_template('indexv2.html', data=[searches_maxes, anime_data])




@app.route("/result", methods=["POST", "GET"])
def result():
  # 1. Get the urls from the urls scraper
  if request.method == 'POST':

    search = request.form['anime_name']
    if 'anime' not in search.lower():
      search = 'anime ' + search
    with open(f'app/tools/web_scraping/searches.txt', 'a') as f:
                
        f.write(f'{search}!|?')
        f.close()
    urls = get_urls.method2(f'${search} titles')

    # 2. Using the urls to scrape data, and get the data back.
    
    data = web_scrape.scrapeUrlsv2(urls)
    data.sort(key=lambda x: x[6], reverse=True)
    conn = sqlite3.connect('titles.db')
    cursor = conn.cursor()
    for i in data:
      try:
        cursor.execute(f'''INSERT INTO ANIME_FULL VALUES ("{i[0]}", "{i[1]}", "{i[2]}", "{i[3]}", "{i[4]}", "{i[5]}", "{i[6]}", "{i[7]}")''')
        cursor.execute(f'''INSERT INTO ANIME_FILTERED VALUES ("{i[0]}", "{i[1]}", "{i[2]}", "{i[3]}", "{i[4]}", "{i[5]}", "{i[6]}", "{i[7]}")''')
      except:
        print(i)
    conn.commit()
    conn.close()



  else:
    conn = sqlite3.connect('titles.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ANIME_FULL")
    data = cursor.fetchall()
    cursor.execute("DELETE FROM ANIME_FILTERED")
    for i in data:
      try:
        cursor.execute(f'''INSERT INTO ANIME_FILTERED VALUES ("{i[0]}", "{i[1]}", "{i[2]}", "{i[3]}", "{i[4]}", "{i[5]}", "{i[6]}", "{i[7]}")''')
      except:
        print(i)
    conn.commit()
    conn.close()


  # 3. Send data back and render it.
  return render_template('queries.html', data=sort_data(data))


@app.route("/filter/<name>")
def filters(name):
  conn = sqlite3.connect('titles.db')
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM ANIME_FILTERED")
  data = cursor.fetchall()
  if name in ['shounen', 'seinen', 'action', 'adventure', 'romance', 'isekai']:
    filter_data = [anime for anime in data if name.title() in anime[4].split('!?|')]
  elif name in ['pg-13', 'r', 'r+', 'pg']:
    mapper = {
      'pg-13': 'PG-13 - Teens 13 or older',
      'r': 'R - 17+ (violence &amp; profanity)',
      'r+': 'R+ - Mild Nudity',
      'pg': 'PG - Children'
    }
    mapped_val = mapper[name]
    filter_data = [anime for anime in data if mapped_val == anime[5]]
  else:

    lower_limit = int(name.split('-')[0])
    if 'current' in name:
      upper_limit = 2030
    else:
      upper_limit = int(name.split('-')[1])
    filter_data = [anime for anime in data if anime[3].isdigit() and lower_limit <= int(anime[3]) <= upper_limit]
  cursor.execute("DELETE FROM ANIME_FILTERED")
  for i in filter_data:
    try:
      cursor.execute(f'''INSERT INTO ANIME_FILTERED VALUES ("{i[0]}", "{i[1]}", "{i[2]}", "{i[3]}", "{i[4]}", "{i[5]}", "{i[6]}", "{i[7]}")''')
    except:
      print(i)
  conn.commit()
  conn.close()
  return render_template('queries.html', data=sort_data(filter_data[:12]))
  
if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
# movie_name = global_data[0].replace('+', ' ')
# anime = global_data[1]
# with open(f'app/tools/web_scraping/searches.txt', 'a') as f:

#   f.write(f"{movie_name}|!? ")
#   f.close()

# for res in anime:
#   name = res[0]
#   with open(f'app/tools/web_scraping/chosen_anime.txt', 'a') as f:
          
#     f.write(f"{name}|!? ")
#     f.close()


