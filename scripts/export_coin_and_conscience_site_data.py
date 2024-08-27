from bs4 import BeautifulSoup
import re
import urllib.request
import pandas as pd

ARTIST_INDEX_URL = "https://www.library.hbs.edu/hc/cc/artistindex.html"
GALLERY_PAGES = {
    'Vanity and Virtue': 'https://www.library.hbs.edu/hc/cc/vanityvirtue.html',
    'Misers, Moneylenders, and Thieves': 'https://www.library.hbs.edu/hc/cc/misersmoneylenders.html',
    'Money Devil': 'https://www.library.hbs.edu/hc/cc/moneydevil.html',
    'Biblical and Mythological Scenes': 'https://www.library.hbs.edu/hc/cc/biblicalmythol.html',
    'Love and Money': 'https://www.library.hbs.edu/hc/cc/loveandmoney.html',
    'Politics and War': 'https://www.library.hbs.edu/hc/cc/politicsandwar.html',
    'Louis-Philippe': 'https://www.library.hbs.edu/hc/cc/louisphilippe.html',
    'Speculation and Credit': 'https://www.library.hbs.edu/hc/cc/specandcredit.html',
    'Bankers, Financiers, and Statesmen': 'https://www.library.hbs.edu/hc/cc/bankers.html',
    'Stock Exchanges': 'https://www.library.hbs.edu/hc/cc/stockexchanges.html'
}
OUTPUT_FILEPATH = 'coin_and_conscience_data.csv'

def read_in_html(input_url):
    fp = urllib.request.urlopen(input_url)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()

    soup = BeautifulSoup(mystr, 'html.parser')
    return soup

def main():
    # Extract artist names and related works from artist index
    artist_index_html = read_in_html(ARTIST_INDEX_URL)
    artist_elements = artist_index_html.find_all("div", "artistName")
    artist_elements_text = [x.text for x in artist_elements]
    artists = []
    for entry in artist_elements_text:
        artist_dict = {}
        artist_dict['artist_name'] = re.sub('(, [0-9]+)+', '', entry)
        artist_dict['related_work'] = re.findall('[0-9]+', entry)
        artists.append(artist_dict)
    artists_df = pd.DataFrame(artists).explode('related_work')

    # Extract artwork metadata from gallery pages by topic
    artworks = []
    for topic, page_url in GALLERY_PAGES.items():
        page_html = read_in_html(page_url)

        artwork_elements = page_html.find_all("dl")
        for artwork in artwork_elements:
            artwork_dict = {}
            artwork_dict['catalog_number'] = artwork.find("strong", "catalogNumber").text
            artwork_dict['title'] = artwork.find("dt").find("a").text
            artwork_dict['url'] = artwork.find("dd", "img").find("a")['href']
            artwork_dict['artist_info'] = artwork.find("div", "artistInfo").text
            artwork_dict['print_info'] = artwork.find("div", "printInfo").text
            artwork_dict['description'] = artwork.find("div", "description").text
            artwork_dict['topic'] = topic
            artworks.append(artwork_dict)
    artworks_df = pd.DataFrame(artworks)

    # Join artist and work data, write to CSV file
    works_by_artist = artists_df.join(artworks_df.set_index('catalog_number'), on='related_work', how='outer')
    works_by_artist.to_csv(OUTPUT_FILEPATH, na_rep='', index=False)

if __name__ == '__main__':
    main()
