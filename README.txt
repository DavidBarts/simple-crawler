IN GENERAL

This package consists of a simple web crawler written in Python and a
simple keyword analyzer that makes use of it. I wrote it because I
needed something simpler than Scrapy to crank out a few quick crawls to
do some analysis on some small sites. It is NOT intended for use as a
general-purpose crawler; see the LIMITATIONS section for more
information.

The web crawler is unithreaded. It is intended for crawling a single
site, so being multithreaded is unnecessary. In fact, a multithreaded
crawler is more challenging to then make polite (i.e. not hammer the
site being crawled with an excessive volume of requests).

To use the crawler, you must subclass it, then override the visit
method. This is what gets called once for each visited page. It gets
passed the following parameters:
    self        Reference to this object
    url         Fully qualified URL of page that was crawled
    raw         String containing HTML text of crawled page
    parsed      The above string, as parsed by Beautiful Soup

It is not necessary to discover links and enqueue them for crawling; the
crawler already does that (that's what crawlers do, after all). The
rel=nofollow attribute is honored for links. Only HTML pages are
crawled; i.e. the Content-Type header of the HTTP response must indicate
it is an HTML document. Once a page is crawled once, it will not be
crawled again in that same crawl.

The other method you can override is the the message method. It gets
passed a level and a message text. Both are strings. The level will be
one of info, warning, or error. The message text will be a free-form
message. If you do not override this method, any crawler you create will
be completely silent and not log anything.

To launch a crawl, first call its constructor to create a crawler
object, then request it start a crawling, e.g.:
    c = SomeCrawler(["http://koosah.info"], domain="koosah.info")
    c.crawl()

When constructing a crawler object, you must furnish a list of crawl
seeds. These are the initial URL's the crawl queue will get populated
with. Typically this will be a 1-item list consisting of the page you
wish to begin the crawl at.

Crawls can have a few optional parameters, which are specified via
keyword options to the constructor:
    delay       A floating-point number, giving the crawl delay
                (minimum interval in seconds between successive HTTP
                requests). This defaults to 5.0 seconds.
    domain      A string giving the Internet domain which the crawl
                will be restricted to. For example, if you specify
                "google.com", then "http://google.com",
                "http://www.google.com/index.html", and
                "http://m.mail.google.com" are allowed, but not
                "http://yahoo.com". By default, there is no domain
                restriction on crawls. The use of this feature to limit
                the scope of crawls is HIGHLY recommended.
    page_limit  If the crawl attempts to fetch more than the specified
                number of pages, it will be ended.
    time_limit  A floating-point value in seconds; if the crawl lasts
                longer than this time, it will be ended.

It is legal to specify both a page and a time limit. In this case,
whichever limit is reached first will end the crawl. By default, or if
the limits are set to None, there are no page or time limits.

LIMITATIONS

As mentioned before, this crawler is unithreaded. That's fine for small,
one-off crawls, which are the intended purpose of this package. It's
almost certainly not what you want if you're crawling many pages all
over the web.

This crawler doesn't know about either robots.txt or sitemap files. This
is a known limitation. The lack of robots.txt support in particular
means YOU SHOULD NOT USE THIS CRAWLER AS-IS FOR GENERAL-PURPOSE
CRAWLING, as it is very bad form to ignore robots.txt when doing so.

This crawler uses a Python list for representing the queue of URLs to
crawl, and a Python set for remembering the URLs that have already been
seen. Neither choice is likely to scale well for crawls of many
thousands of pages.

PREREQUISITES

This crawler requires the requests and bs4 (Beautiful Soup) packages.