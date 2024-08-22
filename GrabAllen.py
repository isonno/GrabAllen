# Grab Paul Allen stuff

import requests, re, os
from html.parser import HTMLParser

#    parser = AllenParser()
#    parser.feed(r.text)

# elem = '<a class="chr-lot-tile__link" href="/s/firsts-history-computing-paul-g-allen-collection/tates-arithmometer-101/230039?ldp_breadcrumb=back">A TATE\'S ARITHMOMETER</a>'

os.chdir("C:\\Temp")

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


def doAuction1(auction_url, outputFile):
    baseURL = 'https://onlineonly.christies.com/'
    lotExpr = re.compile('"url"[:]"([^"]+)","title_primary_txt"[:]"([^"]+)"', flags=re.MULTILINE)
    imgExpr = re.compile('"image_url":"([^"]+)"', flags=re.MULTILINE)
    descExper = re.compile('"description_txt"[:]"(.+deep)"', flags=re.MULTILINE) # Using 'deep' as a delimiter is such a hack
    provExper = re.compile('"Provenance","content":"([^"]+)"', flags=re.MULTILINE)
    lotKeyExpr = re.compile('.+[/][^?]+-(\d+)') # Just grabs the lot number

    def write_attr(f, title, regex, data):
        m = re.search(regex, data)
        if m:
            f.write("<h3>" + title + "</h3>\n")
            f.write("<p>" + m.group(1).replace("\\n", "<br><br>") + "</p>\n")

    auction = requests.get(auction_url)
    if (auction.status_code != 200):
        print("error: %d" % auction.status_code)
    else:
        f = open(outputFile, 'w', encoding='utf-8')
        lotInfo = re.findall(lotExpr, auction.text)
        for lot in lotInfo:
            print("Processing: " + lot[1])
            f.write("<h2>" + lot[1] + "</h2>\n")
            lotData = requests.get(baseURL + lot[0])
            if (lotData.status_code != 200):
                print("error: %d" % lotData.status_code)
            else:
                write_attr(f, "Description", descExper, lotData.text)
                write_attr(f, "Provenance", provExper, lotData.text)

                m = re.search(lotKeyExpr, lot[0])
                lot_key = None
                if (m):
                    lot_key = m.group(1)
                process_images(f, imgExpr, lotData.text, lot_key)
                f.write('<hr>\n')
        f.close()
                            
doAuction1("https://onlineonly.christies.com/s/firsts-history-computing-paul-g-allen-collection/lots/3726?COSID=&cid=sh_hub&bid=", "AllenStuff1.html")

# "url":"https://www.christies.com/en/lot/lot-6495034?ldp_breadcrumb=back",
# "is_auction_over":false,"is_in_progress":false,"title_primary_txt":"AN IBM SYSTEM 360 MODEL 91"


class ChristieParser( HTMLParser ):
    def __init__(self):
        self.first_img_url = None
        self.in_section = None
        self.in_span = False
        self.section_data = {}
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs_list):
        attrs = dict(attrs_list)
        def is_tag_combo(tag_name, attr_name, attr_value):
            return tag == tag_name and attr_name in attrs.keys() and attrs[attr_name] == attr_value
        
        if is_tag_combo('img', 'class', 'chr-img lazyload'):
            self.first_img_url = attrs['src']
        if is_tag_combo('div', 'slot', 'header'):
            self.find_header = True
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
        if data == "Details":
            self.in_section = "Details"
        if data == "Provenance":
            self.in_section = "Provenance"
        
    def handle_endtag(self, tag: str):
        if (tag in ['br', 'b', 'i', 'p'] and self.in_section):
            self.section_data[self.in_section] += "</" + tag + ">"

        if self.in_span and tag=="span" and self.in_section:
            self.in_span = False
            self.in_section = None



#parser = ChristieParser()
#parser.feed(src)

# Image regex: "image_url":"(.+mode=max)"

def doAuction2(auction_url, outputFile):
    lotExpr = re.compile('"url"[:]"([^"]+)","is_auction_over":false,"is_in_progress":false,"title_primary_txt"[:]"([^"]+)"', flags=re.MULTILINE)

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
        f.close()


# doAuction2("https://www.christies.com/en/auction/pushing-boundaries-ingenuity-from-the-paul-g-allen-collection-30730/browse-lots", "AllenStuff2.html")
