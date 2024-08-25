# GrabAllen
## Download the Paul Allen auction Photos from Christies

In August 2024, the Christies auction house [posted auctions of Paul Allen's collection](https://www.christies.com/en/stories/gen-one-innovations-from-the-paul-g-allen-collection-1f0df60a726e4dcbabef3a91a57ef7ee)
of technology, history and science fiction memorabila. Along with the listings
are great high-res color photos of his collection.

Many of the items in this collection were displayed at the Living Computer Museum in Seattle,
which shut down for good in 2020. As [Jason Scott explains](https://ascii.textfiles.com/archives/5672), the LCM wasn't really
a "museum", it was just Paul letting people look at his cool collection of toys.

When Allen died in 2018, there was no plan in place to independently sustain the LCM,
hence its eventual closure and the auction of the major artifacts it displayed.

Now, Christie's is no more a "museum" than the LCM was, and the excellent photos they
took for the auction are irrelevant to them once the sales commission checks are cashed. Hence
this script to grab the photos before they go away. **Note:** Before running this script, edit
the line near the top calling `os.chdir` to specify where you want the files downloaded to.

An archive of the images from the August 2024 Paul Allen auctions as well as HTML files containing summary descriptions
of the auction lots is [posted on the Internet Archive](https://archive.org/details/PaulAllenCollectionPhotos).

Would this script work for other Christies auction listings? Maybe? Could Christies get upset
and make grabbing this info much harder by applying DRM or encription? Certainly. The code is a
bit messy, because Christies posts lots in two different formats.

**This is posted as-is, no warranty, no offer of support.** Once I've grabbed the data, I'm
done with it. I'm posting it here in case others are interested in fishing info off the site.

