# -*- coding: utf-8 -*-

'''
    Filmking Add-on
    Copyright (C) 2020 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')

img_url = params.get('img_url')
hun_title = params.get('hun_title')
ep_title = params.get('ep_title')
year = params.get('year')
prov_server = params.get('prov_server')

if action is None:
    navigator.navigator().root()

elif action == 'movie_categories':
    navigator.navigator().getMovieCategories()

elif action == 'movie_categories_nums':
    navigator.navigator().getMovieCategoriesNums()

elif action == 'series_categories':
    navigator.navigator().getSeriesCategories()

elif action == 'series_categories_nums':
    navigator.navigator().getSeriesCategoriesNums()

elif action == 'get_movie_providers':
    navigator.navigator().getMovieProviders(url, hun_title, img_url, year)

elif action == 'get_series_providers':
    navigator.navigator().getSeriesProviders(url, hun_title, img_url, ep_title, prov_server)

elif action == 'items':
    navigator.navigator().getItems(url)

elif action == 'search':
    navigator.navigator().getSearches()

elif action == 'movie_items':
    navigator.navigator().getMovieItems(url, hun_title, img_url, year)

elif action == 'series_items':
    navigator.navigator().getSeriesItems(url, hun_title, img_url)

elif action == 'playmovie':
    navigator.navigator().playMovie(url)

elif action == 'newsearch':
    navigator.navigator().doSearch()