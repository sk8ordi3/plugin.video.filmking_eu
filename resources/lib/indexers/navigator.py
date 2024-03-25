# -*- coding: utf-8 -*-

'''
    Filmking Addon
    Copyright (C) 2023 heg, vargalex

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

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import urllib.parse
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

version = xbmcaddon.Addon().getAddonInfo('version')
kodi_version = xbmc.getInfoLabel('System.BuildVersion')
base_log_info = f'Filmking.eu | v{version} | Kodi: {kodi_version[:5]}'

xbmc.log(f'{base_log_info}', xbmc.LOGINFO)

base_url = 'https://filmking.eu'

headers = {
    'authority': 'filmking.eu',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))

    def root(self):
        self.addDirectoryItem("Filmek", f"movie_items&url={base_url}/filmek-evszam-szerint/", '', 'DefaultFolder.png')
        self.addDirectoryItem("4K", f"movie_items&url={base_url}/4k/", '', 'DefaultFolder.png')
        self.addDirectoryItem("Kollekciók", f"movie_items&url={base_url}/kollekciok/", '', 'DefaultFolder.png')        
        self.addDirectoryItem("Film Kategóriák", "movie_categories", '', 'DefaultFolder.png')
        self.addDirectoryItem("Film (Évszám szerint)", "movie_categories_nums", '', 'DefaultFolder.png')
        self.addDirectoryItem("Sorozatok", f"series_items&url={base_url}/osszes-sorozat/", '', 'DefaultFolder.png')
        self.addDirectoryItem("Sorozat Kategóriák", "series_categories", '', 'DefaultFolder.png')
        self.addDirectoryItem("Sorozat (Évszám szerint)", "series_categories_nums", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "search", '', 'DefaultFolder.png')
        self.endDirectory()
        
    def getMovieCategories(self):
        
        genre_name = [
          'akcio',
          'csaladi',
          'drama',
          'fantasy',
          'horror',
          'kaland',
          'mese-filmek',
          'misztikus',
          'romantikus',
          'sci-fi',
          'thriller',
          'vigjatek'
        ]
        
        for genre in genre_name:
            url = f'{base_url}/{genre}/'
            self.addDirectoryItem(genre, f'movie_items&url={url}', '', 'DefaultFolder.png')

        self.endDirectory()

    def getMovieCategoriesNums(self):
        
        genre_nums = [
          '2024',
          '2023',
          '2022',
          '2021',
          '2020',
          '2019',
          '2018',
          '2017',
          '2016',
          '2015',
          '2014',
          '2013',
          '2012',
          '2011',
          '2010'
        ]
        
        for genre in genre_nums:
            url = f'{base_url}/{genre}/'
            self.addDirectoryItem(genre, f'movie_items&url={url}', '', 'DefaultFolder.png')

        self.endDirectory()        

    def getSeriesCategories(self):
        
        genre_name = [
          'sorozat-akcio',
          'sorozat-csaladi',
          'sorozat-dokumentum',
          'sorozat-drama',
          'sorozat-bunugyi',
          'sorozat-fantasy',
          'sorozat-haborus',
          'sorozat-horror',
          'sorozat-krimi',
          'sorozat-kaland',
          'sorozat-animacio',
          'sorozat-misztikus',
          'sorozat-romantikus',
          'sorozat-sci-fi',
          'sorozat-thriller',
          'sorozat-tortenelmi',
          'sorozat-vigjatek'
        ]
        
        for genre in genre_name:
            url = f'{base_url}/{genre}/'
            self.addDirectoryItem(genre, f'series_items&url={url}', '', 'DefaultFolder.png')

        self.endDirectory()

    def getSeriesCategoriesNums(self):
        
        genre_nums = [
          'sorozat-2024',
          'sorozat-2023',
          'sorozat-2022',
          'sorozat-2021',
          'sorozat-2020',
          'sorozat-2019',
          'sorozat-2018',
          'sorozat-2017',
          'sorozat-2016',
          'sorozat-2015',
          'sorozat-2014',
          'sorozat-2013',
          'sorozat-2012',
          'sorozat-2011',
          'sorozat-2010'
        ]
        
        for genre in genre_nums:
            url = f'{base_url}/{genre}/'
            self.addDirectoryItem(genre, f'series_items&url={url}', '', 'DefaultFolder.png')

        self.endDirectory()

    def getItems(self, url):
        import re
        
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        articles = soup.find_all('article')
        
        processed_urls = set()
        
        for article in articles:
            card_link_element = article.find('a', class_='elementor-post__thumbnail__link')
            if not card_link_element:
                continue
            
            card_link = card_link_element['href']
        
            if card_link in processed_urls:
                continue
        
            processed_urls.add(card_link)
        
            img_element = article.find('img')
            if not img_element:
                continue
            img_url = img_element['src']
            
            badge_element = article.find('div', class_='elementor-post__badge')
            if not badge_element:
                continue
            check_year = badge_element.text
            if re.search('(\d+)', check_year):
                year = check_year
                type = 'Film'
            else:
                type = 'Sorozat'
            
            title_element = article.find('h3', class_='elementor-post__title')
            if not title_element:
                continue
            hun_title = title_element.text.strip()
            hun_title = re.sub(r'( [0-9][0-9][0-9][0-9])', r'', hun_title)

            if type == 'Sorozat':
                self.addDirectoryItem(f'[B]|{type}| {hun_title}[/B]', f'get_series_providers&url={card_link}&img_url={img_url}&hun_title={hun_title}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})
            
            else:
                self.addDirectoryItem(f'[B]|{type:^10}| {hun_title} - {year}[/B]', f'get_movie_providers&url={card_link}&img_url={img_url}&hun_title={hun_title}&year={year}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})
        
        try:
            next_page_element = soup.find('a', class_='next')
            if next_page_element:
                next_page_url = next_page_element['href']
                self.addDirectoryItem('[I]Következő oldal[/I]', f'items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
            else:
                xbmc.log(f'{base_log_info}| getItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)
        except TypeError:
            xbmc.log(f'{base_log_info}| getItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)
        
        self.endDirectory('movies')

    def getMovieProviders(self, url, hun_title, img_url, year):
        import urllib.parse
        import requests
        import re
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        link = url
        links = soup.find_all('a', class_='elementor-button-link')
        for link in links:
            span_text = link.find('span', class_='elementor-button-text')
            if span_text and 'Beküldött linkek' in span_text.get_text():
                bekuldott_linkek = link['href']
        
                if re.search('videaletoltes', str(bekuldott_linkek)):
                    import requests          
                    
                    html_source_2 = requests.get(bekuldott_linkek)
                    soup2 = BeautifulSoup(html_source_2.text, 'html.parser')
                    table = soup2.find('div', class_='links_table')
        
                    data = []
        
                    rows = table.find_all('tr')
                    for row in rows:
                        link = row.find('a')
                        if link:
                            provider = link.text
                            provider_link = link['href']
                            quality = row.find('strong', class_='quality').text
                            language = row.find_all('td')[2].text
                            
                            data.append({
                                'provider': provider,
                                'provider_link': provider_link,
                                'quality': quality,
                                'language': language
                            })                    
                    
                    filtered_data = []
                    
                    for item in data:
                        if all(item.values()):
                            filtered_data.append(item)
                
                elif re.search('filmking.eu', str(bekuldott_linkek)):
                    
                    html_source_2 = requests.get(bekuldott_linkek)
                    soup_2 = BeautifulSoup(html_source_2.text, 'html.parser')
                    
                    data = []
                    
                    sections = soup_2.find_all('section', class_='ob-is-breaking-bad')
                    for section in sections:
                        provider_element = section.find('h2', class_='elementor-heading-title')
                        provider = provider_element.text.strip() if provider_element else None
                    
                        provider_link_element = section.find('a', class_='elementor-button-link')
                        provider_link = provider_link_element['href'] if provider_link_element else None
                    
                        siblings = section.find_all_next('div', class_='elementor-column')
                        quality_element = siblings[2].find('h2', class_='elementor-heading-title') if len(siblings) > 1 else None
                        quality = quality_element.text.strip() if quality_element else None
                        
                        siblings = section.find_all_next('div', class_='elementor-column')
                        language_element = siblings[1].find('h2', class_='elementor-heading-title') if len(siblings) > 1 else None
                        language = language_element.text.strip() if language_element else None                
                    
                        data.append({
                            'provider': provider,
                            'provider_link': provider_link,
                            'quality': quality,
                            'language': language
                        })
                    
                    filtered_data = []
                    
                    for item in data:
                        if all(item.values()):
                            filtered_data.append(item)          
        
        if 'filtered_data' not in locals():
            filtered_data = []
        
        def fix_iframe_link(iframe_link):
            if not iframe_link.startswith("https:"):
                iframe_link = "https:" + iframe_link
            return iframe_link
        
        if re.search('<iframe', str(soup), flags=re.IGNORECASE): # iframe
        
            iframe = re.findall(r'<iframe.*</iframe>', str(soup), flags=re.IGNORECASE)[0].strip()
            iframe_server = re.findall(r'//(.*?)/', iframe, flags=re.IGNORECASE)[0].strip()
            
            if re.search('onelineplayer', iframe):
                frame_link = re.findall(r'url=(.*?)&', iframe)[0].strip()
                decoded_url = urllib.parse.unquote(frame_link)
                
                resp_something = requests.get(decoded_url, allow_redirects=False)
                
                iframe_link = resp_something.headers['Location']
            
            elif re.search(iframe_server, str(iframe)):
                iframe_link = re.findall(r'src=\"(.*?)\"', iframe, flags=re.IGNORECASE)[0].strip()
            
            iframe_link = fix_iframe_link(iframe_link)
            
            filtered_data.append({
                'provider': iframe_server,
                'provider_link': iframe_link,
                'quality': 'ismeretlen',
                'language': 'Magyar',
            })
            
        if re.search('\.mp4\" type=\"video/mp4', str(soup), flags=re.IGNORECASE): # video/mp4
        
            unkown_mp4 = re.findall(r'\"(http.*?mp4)\" type=\"video/mp4\"', str(soup), flags=re.IGNORECASE)[0].strip()
            unkown_mp4_server = re.findall(r'//(.*?)/', unkown_mp4, flags=re.IGNORECASE)[0].strip()
            
            if re.search('od.lk', unkown_mp4):
                decoded_url = urllib.parse.unquote(unkown_mp4)
                
                resp_something = requests.get(decoded_url, allow_redirects=False)
                
                unkown_mp4_link = resp_something.headers['Location']
            
            filtered_data.append({
                'provider': unkown_mp4_server,
                'provider_link': unkown_mp4_link,
                'quality': 'ismeretlen',
                'language': 'Magyar',
            })            
        
        categories = soup.find_all('span', class_='elementor-icon-list-text')
        description_tag = soup.find('div', class_='movies-data')
        
        if description_tag:
            description = description_tag.text.strip()
        else:
            description = None
        
        if description is None:
            meta_tag = soup.find('meta', property='og:description')
            if meta_tag and 'content' in meta_tag.attrs:
                description = meta_tag['content'].strip()
        
        if description is None:
            description_match = re.search(r'<strong>Film leírás</strong></h2><p><strong>(.*?)</strong></p>', str(soup))
            if description_match:
                description = description_match.group(1).strip()
        
        data_list = {'categories': [category.text for category in categories], 'description': description}
        
        filtered_data.append(data_list)

        providers = filtered_data[:-1]
        title_infos = filtered_data[-1]
        
        result = {'providers': providers, 'title_infos': title_infos}
        
        content = result['title_infos']['description']
        
        # Concatenating categories into a comma-separated string
        #categories = ", ".join(result['title_infos']['categories'])
        
        providers = result['providers']

        for extr_prov in providers:
            provider = extr_prov['provider']
            provider_link = extr_prov['provider_link']
            quali_category = extr_prov['quality']
            lang_category = extr_prov['language']

            self.addDirectoryItem(f'[B][COLOR lightblue]{quali_category}[/COLOR] | [COLOR orange]{lang_category}[/COLOR] | [COLOR red]{provider}[/COLOR] | {hun_title} - {year}[/B]', f'playmovie&url={quote_plus(provider_link)}&img_url={img_url}&hun_title={hun_title}&content={content}&provider={provider}', img_url, 'DefaultMovies.png', isFolder=False, meta={'title': f'{hun_title} - {year} ({provider})', 'plot': content})

        self.endDirectory('movies')

    def getSeriesProviders(self, url, hun_title, img_url, ep_title, prov_server):

        from bs4 import BeautifulSoup
        import urllib.parse
        import requests
        import re
        
        link = url
        
        def fix_iframe_link(src_link):
            if not src_link.startswith("https:"):
                src_link = "https:" + src_link
            return src_link
        
        def append_links_to_json(data, title, links):
            for episode in data['episodes']:
                if episode['title'] == title:
                    episode['links'] = links
                    break
            else:
                data['episodes'].append({'title': title, 'links': links})
        
        def extract_links_from_first_part(soup):
            final_appended_data = {"episodes": []}
            season_pattern = re.compile(r'\d+ Évad')
            accordion_items = soup.find_all(class_='elementor-accordion-item')
            links_found = False
            for accordion_item in accordion_items:
                main_season_title_tag = accordion_item.find_previous(class_='elementor-heading-title', string=season_pattern)
                main_season_title = main_season_title_tag.get_text(strip=True) if main_season_title_tag else None
                main_season_num = int(re.findall(r'(\d) évad', main_season_title, flags=re.IGNORECASE)[0].strip())
        
                episode_title_tag = accordion_item.find(class_='elementor-accordion-title')
                episode_title = episode_title_tag.get_text(strip=True) if episode_title_tag else None
                episode_num = int(re.findall(r'(\d+) epizód', episode_title, flags=re.IGNORECASE)[0].strip())
                
                title = f'{main_season_num}. Évad {episode_num}. rész'
        
                episode_links_list = []
                iframe = accordion_item.find('iframe')
                if iframe:
                    src_link = iframe['src']
                    if re.search('onelineplayer', src_link):
                        frame_link = re.findall(r'url=(.*?)&', src_link)[0].strip()
                        decoded_url = urllib.parse.unquote(frame_link)             
                        episode_links_list.append({"LINK": decoded_url})
                        links_found = True
                    else:
                        src_link = fix_iframe_link(src_link)
                        episode_links_list.append({"LINK": src_link})
                        links_found = True
        
                episode_links = accordion_item.find_all('a', href=True)
                if episode_links:
                    for link in episode_links:
                        src_link = link['href']
                        src_link = fix_iframe_link(src_link)
                        episode_links_list.append({f"LINK": src_link})
                        links_found = True
                
                if links_found:
                    append_links_to_json(final_appended_data, title, episode_links_list)
            return final_appended_data, links_found
        
        def extract_links_from_second_part(soup):
            final_appended_data = {"episodes": []}
            main_season_title = soup.find('h2', class_='elementor-heading-title elementor-size-default').text
        
            season_number_match = re.search(r"(\d+) évad", main_season_title)
            if season_number_match:
                season_number = season_number_match.group(1)
        
            episode_titles = re.findall(r'(\d+) epizód', str(soup))
            if episode_titles:
                episode_iframes = soup.find_all('iframe')
                if episode_iframes:
                    num_episodes = min(len(episode_titles), len(episode_iframes))
                    for i in range(num_episodes):
                        episode_title = episode_titles[i]
                        src_link = episode_iframes[i]['src']
                        src_link = fix_iframe_link(src_link)
                        title = f'{main_season_title} {episode_title}. rész'
                        episode_links_list = [{f"LINK": src_link}]
                        append_links_to_json(final_appended_data, title, episode_links_list)
                        links_found = True
            return final_appended_data, links_found
        
        def extract_links(link):
            headers = {
                'authority': 'filmking.eu',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            }
        
            response = requests.get(link, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            categories = soup.find_all('span', class_='elementor-icon-list-text')
        
            categories_filtered = [category.text for category in categories if not re.match(r'\b\d+\b', category.text)]
            
            description_tag = soup.find('div', class_='movies-data')
            
            if description_tag:
                description = description_tag.text.strip()
            else:
                description = None
            
            if description is None:
                meta_tag = soup.find('meta', property='og:description')
                if meta_tag and 'content' in meta_tag.attrs:
                    description = meta_tag['content'].strip()
            
            if description is None:
                description_match = re.search(r'<strong>Film leírás</strong></h2><p><strong>(.*?)</strong></p>', str(soup))
                if description_match:
                    description = description_match.group(1).strip()
            
            data_list = {'categories': categories_filtered, 'description': description}
            
            final_appended_data = {"episodes": []}

            first_part_data, links_found = extract_links_from_first_part(soup)
            if links_found:
                final_appended_data = first_part_data
            else:
                second_part_data, links_found = extract_links_from_second_part(soup)
                if links_found:
                    final_appended_data = second_part_data
            
            final_appended_data.update(data_list)
            
            return final_appended_data
            
        def color_and_concatenate(ep_title):
            episode_matches = re.findall(r'(\d+)\. rész', ep_title)
            colored_text = ""
            for episode_number in episode_matches:
                color_code = "lightgreen" if int(episode_number) % 2 == 0 else "lightblue"
                colored_text += f"[COLOR {color_code}]{ep_title}[/COLOR] "
            return colored_text.strip()
        
        final_appended_data = extract_links(link)

        content = final_appended_data['description']
        
        for episode in final_appended_data['episodes']:
            ep_title = episode['title']
            for link_info in episode['links']:
                prov_link = link_info['LINK']
                prov_server = re.findall(r'//(.*?)/', str(prov_link))[0].strip()
                
                colored_text = color_and_concatenate(ep_title)

                title_text = f'[B]{colored_text} - {hun_title} # ([COLOR orange]{prov_server}[/COLOR])[/B]'
                url_params = f'playmovie&url={quote_plus(prov_link)}&img_url={img_url}&hun_title={hun_title}&content={content}&ep_title={ep_title}&prov_server={prov_server}'

                metadata = {'title': f'{ep_title} - {hun_title}', 'plot': content}

                self.addDirectoryItem(title_text, url_params, img_url, 'DefaultMovies.png', isFolder=False, meta=metadata)

        self.endDirectory('movies')

    def getMovieItems(self, url, hun_title, img_url, year):
        
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        articles = soup.find_all('article')
        processed_urls = set()
        
        for article in articles:
            card_link = article.find('a', class_='elementor-post__thumbnail__link')['href']
        
            if card_link in processed_urls:
                continue
            
            processed_urls.add(card_link)
            
            img_url = article.find('img')['src']
            if '╤' in img_url:
                first_img_link = soup.find("a", class_="elementor-post__thumbnail__link").find("img")
                if first_img_link:
                    img_url = first_img_link["src"]
            
            year = article.find('div', class_='elementor-post__badge').text
            hun_title = article.find('h3', class_='elementor-post__title').text.strip()
            hun_title = re.sub(r'( [0-9][0-9][0-9][0-9])', r'', hun_title)
            
            self.addDirectoryItem(f'[B]{hun_title} - {year}[/B]', f'get_movie_providers&url={card_link}&hun_title={hun_title}&img_url={img_url}&year={year}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})

        try:
            load_more_anchor = soup.find('div', class_='e-load-more-anchor')
            if load_more_anchor:
                next_page_url = load_more_anchor.get('data-next-page')
                if next_page_url:
                    self.addDirectoryItem('[I]Következő oldal[/I]', f'movie_items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
        
        except:
            xbmc.log(f'{base_log_info}| getMovieItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)

        self.endDirectory('movies')

    def getSeriesItems(self, url, hun_title, img_url):
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        articles = soup.find_all('article')
        processed_urls = set()
        
        for article in articles:
            card_link = article.find('a', class_='elementor-post__thumbnail__link')['href']
        
            if card_link in processed_urls:
                continue
            
            processed_urls.add(card_link)
            
            img_url = article.find('img')['src']
            cim_element = article.find('h3', class_='elementor-post__title')
            if cim_element:
                hun_title = cim_element.text.strip()
            else:
                cim_element = article.find('h2', class_='elementor-post__title')
                hun_title = cim_element.text.strip()

            
            self.addDirectoryItem(f'[B]{hun_title}[/B]', f'get_series_providers&url={card_link}&hun_title={hun_title}&img_url={img_url}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})

        try:
            load_more_anchor = soup.find('div', class_='e-load-more-anchor')
            if load_more_anchor:
                next_page_url = load_more_anchor.get('data-next-page')
                if next_page_url:
                    self.addDirectoryItem('[I]Következő oldal[/I]', f'series_items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
        
        except:
            xbmc.log(f'{base_log_info}| getSeriesItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)

        self.endDirectory('movies')

    def playMovie(self, url):

        if re.search('iframe.mediadelivery', url):
            try:
                import requests
                
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                }
                
                response_3 = requests.get(url, headers=headers).text
                m3u8_url = re.findall(r'src=\"(.*?playlist.m3u8)\"', str(response_3))[0].strip()
                
                extended_m3u8 = f'{m3u8_url}|Referer=https://iframe.mediadelivery.net/'
                
                play_item = xbmcgui.ListItem(path=extended_m3u8)
                if 'm3u8' in m3u8_url:
                    from inputstreamhelper import Helper
                    is_helper = Helper('hls')
                    if is_helper.check_inputstream():
                        play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
                        play_item.setProperty('inputstream.adaptive.stream_headers', 'Referer=https://iframe.mediadelivery.net/')
                xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
            except:
                xbmc.log(f'{base_log_info}| playMovie | name: No video sources found', xbmc.LOGINFO)
                notification = xbmcgui.Dialog()
                notification.notification("Filmking.eu", "Törölt tartalom", time=5000)                
        else:
            try:
                direct_url = urlresolver.resolve(url)
                xbmc.log(f'{base_log_info}| playMovie | direct_url: {direct_url}', xbmc.LOGINFO)
                play_item = xbmcgui.ListItem(path=direct_url)
                if 'm3u8' in direct_url:
                    from inputstreamhelper import Helper
                    is_helper = Helper('hls')
                    if is_helper.check_inputstream():
                        play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
                xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
            except:
                   try:
                       xbmc.log(f'{base_log_info}| playMovie | url: {url}', xbmc.LOGINFO)
                       
                       play_item = xbmcgui.ListItem(path=url)
                       xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
                   except:
                       xbmc.log(f'{base_log_info}| playMovie | name: No video sources found', xbmc.LOGINFO)
                       notification = xbmcgui.Dialog()
                       notification.notification("Filmking.eu", "Törölt tartalom", time=5000)

    def getSearches(self):
        self.addDirectoryItem('[COLOR lightgreen]Új keresés[/COLOR]', 'newsearch', '', 'DefaultFolder.png')
        try:
            file = open(self.searchFileName, "r")
            olditems = file.read().splitlines()
            file.close()
            items = list(set(olditems))
            items.sort(key=locale.strxfrm)
            if len(items) != len(olditems):
                file = open(self.searchFileName, "w")
                file.write("\n".join(items))
                file.close()
            for item in items:
                url_p = f"{base_url}/?post_type=page&s={item}"
                enc_url = quote_plus(url_p)                
                self.addDirectoryItem(item, f'items&url={url_p}', '', 'DefaultFolder.png')

        except:
            pass
        self.endDirectory()

    def doSearch(self):
        search_text = self.getSearchText()
        if search_text != '':
            if not os.path.exists(self.base_path):
                os.mkdir(self.base_path)
            url = f"{base_url}/?post_type=page&s={search_text}"
            self.getItems(url)

    def getSearchText(self):
        search_text = ''
        keyb = xbmc.Keyboard('', u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        keyb.doModal()
        if keyb.isConfirmed():
            search_text = keyb.getText()
        return search_text

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)