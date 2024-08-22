# Grab the contents of the Paul Allen Auctions at Christies, August 2024
# Requires the requests package, which is not standard ("pip install requests")
# J. Peterson

import requests, re, os
from html.parser import HTMLParser

# Change this line to determine where you want the download to happen.
os.chdir("/Notes/Allen")

# Dump all the images with URLs matching imgRexex in lot_text
# to the images folder. HTML links to the images are appended to 'f'.
# lot_key is used to restrict images written to a particular lot
def process_images(f, imgRegex, lot_text, lot_key=None):
    imgFileExpr = re.compile('.+[/]([^?]+)')
    if (not os.path.exists("images")):
        os.mkdir("images")

    f.write("<h2>Images:</h2>\n")
    f.write("<p>\n")
    images = re.findall(imgRegex, lot_text)
    img_count = 1

    # Process the images
    for img_url in images:
        # If the image URL doesn't contain the lot key, then it's
        # advertising another lot and not related.
        if lot_key and img_url.find(lot_key) == -1:
            continue
        img_path = None
        m = re.search(imgFileExpr, img_url)
        if (m):
            img_path = m.group(1)
        if (not (img_path and os.path.exists("images" + os.sep + img_path))):  # Don't get the file if we already have it.
            img_data = requests.get(img_url)
            if (img_data.status_code != 200):
                print("error getting image %s: %d" % (img_url, img_data.status_code))
            else:
                open("images" + os.sep + img_path, 'wb').write(img_data.content)

        f.write('<a href="./images/' + img_path + '">Image %d</a>\n' % img_count)
        img_count += 1
    f.write("</p>\n")

# The web page describing the lots comes in two flavors; the online copy
# stores the lots as a JSON blob that's inflated on display. This fishes
# the info out of the JSON.
def grabOnlineAuction(auction_url, outputFile):
    baseURL = 'https://onlineonly.christies.com/'
    lotExpr = re.compile('"url"[:]"([^"]+)","title_primary_txt"[:]"([^"]+)"', flags=re.MULTILINE)
    imgExpr = re.compile('"image_url":"([^"]+)"', flags=re.MULTILINE)
    descExper = re.compile('"description_txt"[:]"((\\.|[^"])*)"', flags=re.MULTILINE)
    provExper = re.compile('"Provenance","content":"([^"]+)"', flags=re.MULTILINE)
    lotKeyExpr = re.compile('.+[/][^?]+-(\d+)') # Just grabs the lot number

    def write_attr(f, title, regex, data):
        m = re.search(regex, data)
        if m:
            f.write("<h3>" + title + "</h3>\n")
            f.write("<p>" + m.group(1).replace("\\n", "<br><br>") + "</p>\n")

    auction = requests.get(auction_url)
    if (auction.status_code != 200):
        print("Online auction error: %d" % auction.status_code)
    else:
        f = open(outputFile, 'w', encoding='utf-8')
        lotInfo = re.findall(lotExpr, auction.text)
        firstLot = lotInfo[0]
        start = True
        for lot in lotInfo:
            if not start and lot[0] == firstLot[0]:   # Two copies of the lot DB are included,
                break                                 # bail after processing the first one.
            start = False                 
            print("Processing: " + lot[1])
            f.write("<h2>" + lot[1] + "</h2>\n")
            lotData = requests.get(baseURL + lot[0])
            if (lotData.status_code != 200):
                print("error: %d" % lotData.status_code)
            else:
                write_attr(f, "Description", descExper, lotData.text)
                write_attr(f, "Provenance", provExper, lotData.text)

                # Keep track of the lot key, so we only download images
                # related to this lot. Otherwise it finds promo images for other lots.
                m = re.search(lotKeyExpr, lot[0])
                lot_key = None
                if (m):
                    lot_key = m.group(1)
                process_images(f, imgExpr, lotData.text, lot_key)
                f.write('<hr>\n')
            
        f.close()

# The "regular" Christie's lots are regular HTML, and the info
# can be parsed out of it.

class ChristieParser( HTMLParser ):
    def __init__(self):
        self.first_img_url = None
        self.in_section = None
        self.in_span = False
        self.in_header = False
        self.section_data = {}
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs_list):
        attrs = dict(attrs_list)
        def is_tag_combo(tag_name, attr_name, attr_value):
            return tag == tag_name and attr_name in attrs.keys() and attrs[attr_name] == attr_value
        
        if is_tag_combo('img', 'class', 'chr-img lazyload'):
            self.first_img_url = attrs['src']
        if is_tag_combo('div', 'slot', 'header'):
            self.in_header = True
        if is_tag_combo('span', 'class', 'chr-lot-section__accordion--text'):
            self.in_span = True

        if (tag in ['br', 'b', 'i', 'p'] and self.in_section):
            self.section_data[self.in_section] += "<" + tag + ">"

    def handle_data(self, data):
        if self.in_span:
            if self.in_section in self.section_data.keys():
                self.section_data[self.in_section] += data
            else:
                self.section_data[self.in_section] = data
        if self.in_header and (data in ["Details", "Provenance"]):
            self.in_section = data
        
    def handle_endtag(self, tag: str):
        if (tag in ['br', 'b', 'i', 'p'] and self.in_section):
            self.section_data[self.in_section] += "</" + tag + ">"

        if self.in_span and tag=="span" and self.in_section:
            self.in_span = False
            self.in_section = None
            self.in_header = False

# Christie's live auctions are regular HTML
def grabLiveAuction(auction_url, outputFile):
    lotExpr = re.compile('"url"[:]"([^"]+)","is_auction_over":false,"is_in_progress":false,"title_primary_txt"[:]"([^"]+)"', flags=re.MULTILINE)
    imgExpr = re.compile('"image_url":"([^"]+)"', flags=re.MULTILINE)

    auction = requests.get(auction_url)
    if (auction.status_code != 200):
        print("error: %d" % auction.status_code)
    else:
        f = open(outputFile, 'w', encoding='utf-8')
        lotInfo = re.findall(lotExpr, auction.text)
        for lot in lotInfo:
            print("Processing: " + lot[1])
            f.write("<h2>" + lot[1] + "</h2>\n")
            lotData = requests.get(lot[0])
            if (lotData.status_code != 200):
                print("error: %d" % lotData.status_code)
            else:
                parser = ChristieParser()
                parser.feed(lotData.text)

                f.write("<h3>Details</h3>\n")
                f.write("<p>" + parser.section_data['Details'] + "</p>\n")
                if ("Provenance" in parser.section_data.keys()):
                    f.write("<h3>Provenance</h3>\n")
                    f.write("<p>" + parser.section_data['Provenance'] + "</p>\n")

                process_images(f, imgExpr, lotData.text)
                f.write('<hr>\n')

        f.close()

grabOnlineAuction("https://onlineonly.christies.com/s/firsts-history-computing-paul-g-allen-collection/lots/3726?COSID=&cid=sh_hub&bid=", "AllenStuff1.html")
grabLiveAuction("https://www.christies.com/en/auction/pushing-boundaries-ingenuity-from-the-paul-g-allen-collection-30730/browse-lots", "AllenStuff2.html")

