from flask import Flask, render_template, request
from .tools.web_scraping import get_urls
from .tools.web_scraping import web_scrape
from time import time


app = Flask(__name__)


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



@app.route("/")
def hello():
    searches_db = list(open('app/tools/web_scraping/searches.txt').read().split('!|?'))
    searches_maxes = calc_maxes(searches_db, 4)
    searches_maxes = [(i+1, searches_maxes[i].title()) for i in range(len(searches_maxes))]
    chosen_anime_db = list(open('app/tools/web_scraping/chosen_anime.txt').read().split('!|?'))
    chosen_anime_maxes = calc_maxes(chosen_anime_db, 8)
    anime_data = web_scrape.give_image(chosen_anime_maxes)
    return render_template('indexv2.html', data=[searches_maxes, anime_data])

big_d = [[], []]


@app.route("/result", methods=["POST", "GET"])
def result():
  # 1. Get the urls from the urls scraper
  if request.method == 'POST':

    search = request.form['anime_name']
    with open(f'app/tools/web_scraping/searches.txt', 'a') as f:
                
        f.write(f'{search}!|?')
        f.close()
    urls = get_urls.method2(f'${search} titles')

    # 2. Using the urls to scrape data, and get the data back.
    
    data = web_scrape.scrapeUrlsv2(urls)
    big_d[0] = data
    big_d[1] = data

  else:
    data = big_d[0]
    big_d[1] = data


  # 3. Send data back and render it.
  return render_template('queries.html', data=data)


@app.route("/filter/<name>")
def filters(name):
  data = big_d[1]
  if name in ['shounen', 'seinen', 'action', 'adventure', 'romance', 'isekai']:
    filtered_data = [anime for anime in data if name.title() in anime[4].split('!?|')]
  elif name in ['pg-13', 'r', 'r+', 'pg']:
    mapper = {
      'pg-13': 'PG-13 - Teens 13 or older',
      'r': 'R - 17+ (violence &amp; profanity)',
      'r+': 'R+ - Mild Nudity',
      'pg': 'PG - Children'
    }
    mapped_val = mapper[name]
    filtered_data = [anime for anime in data if mapped_val == anime[5]]
  else:
    lower_limit = int(name.split('-')[0])
    if 'current' in name:
      upper_limit = 2030
    else:
      upper_limit = int(name.split('-')[1])
    filtered_data = [anime for anime in data if anime[3].isdigit() and lower_limit <= int(anime[3]) <= upper_limit]
  big_d[1] = filtered_data
  print([entry[0] for entry in filtered_data])
  return render_template('queries.html', data=filtered_data)
  
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


