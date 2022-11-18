def testing_final(url):
    
    soup = base_testing(url)
    terms = ('', '')
    
        
    if 'https://www.fandomspot.' in url or 'https://www.imdb' in url or 'https://www.cbr.' in url:

        if 'https://www.cbr.' in url:
            terms = (soup.select('h2'), 'h2')
            res, response = testing_cbr(terms)
        else:
            terms = (soup.select('h3'), 'h3')
            if 'https://www.fandomspot.' in url:
                res, response = testing_fandom(terms)
            else:
                res, response = testing_imdb(terms)

        if response:
            return res
    def give_final(type):
        final = terms[0]
        if terms[1] != type:
            final = soup.select(type)
        return final

    final = give_final('h2')


    res, response = testing2(final)
    if response:
        return res

    res, response = testing(soup)
    if response:
        return res
    
    final = give_final('h3 ')

    res, response = testing2(final)
    if response:
        return res


def base_filterv2(results, type, func, *args):

    final_results = []
    function = functions_dict[type]
    for result in results:
        data = function(result)
        condition = func(data, *args)
        if condition:
            final_results.append(result)
    return final_results

# sample specific filter funcs
def year_filterv2(data, lower_bound, upper_bound):
    year = int(data['releaseDate'][:4])
    condition = lower_bound <= year <= upper_bound
    return condition

def match_year_tvshows(lower_bound, upper_bound, results):
    return base_filterv2(results, 'Series', year_filterv2, lower_bound, upper_bound)



import matplotlib.pyplot as plt
points = [-0.015625, -0.0078125]
start = 1
for i in range(1000):
    diff = (points[-1] - points[-2]) / 2
    points.append(points[-1] + diff)
    


new_points = [-1 * x for x in points]
# points = list(points) + new_points[::-1]
y = [0.015625]

# print(max(points), min(points))

newx = []
for i in range(1, len(points)):
    if i % 2 == 0:
        y.append(points[i] * -1)
    else:
        y.append(y[-1])

new_points = [-1 * x for x in points]
new_y = [-1 * x for x in y]
points += new_points[::-1]
y += new_y[::-1]
print(points)
print(y)
plt.plot(points, y)
plt.show()
