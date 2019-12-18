#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A simple web crawler. What I need for basic KW analysis, nothing more.

#  I m p o r t s

import os, sys
import traceback
import unicodedata
from urllib.parse import urlparse, urlunparse, urljoin
from time import time, sleep

import requests
from bs4 import BeautifulSoup

# C l a s s e s

class Crawler(object):
    def __init__(self, seeds, delay=5.0, domain=None, page_limit=None, time_limit=None):
        self.delay = delay
        self.seen = set()
        self.queue = []
        if domain is not None:
            domain = domain.lower()
        self.domain = domain
        self.page_limit = page_limit
        self.time_limit = time_limit
        for seed in seeds:
            self.enqueue(seed)

    def visit(self, url, raw, parsed):
        """
        Do something when we visit a page.
        """
        raise NotImplementedError("You must override the visit method!")

    def crawl(self):
        """
        Launch a crawl.
        """
        start_time = time()
        pages = 0
        last_time = 0.0
        while self.queue:
            # Bail with non-empty queue if a limit has been reached
            if self.page_limit is not None and pages >= self.page_limit:
                self.message("info", "page limit reached")
                break
            if self.time_limit is not None and time() - start_time >= self.time_limit:
                self.message("info", "time limit reached")
                break
            # Be polite
            elapsed = time() - last_time
            if elapsed < self.delay:
                sleep_time = self.delay - elapsed
                self.message("info", "sleeping {0:.3f} second{1}".format(
                    sleep_time, "" if sleep_time == 1 else "s"))
                sleep(sleep_time)
            last_time = time()
            # Get a response
            pages += 1
            url = self.queue.pop(0)
            self.message("info", "requesting " + repr(url))
            try:
                response = requests.get(url, allow_redirects=False)
            except:
                self.message("warning", "exception requesting page:\n{0}".format(
                    traceback.format_exc()))
                continue
            # If we got a redirect, process it
            if 300 <= response.status_code <= 399:
                if "location" not in response.headers:
                    self.message("warning",
                        "got {0} redirect without location for {1!r}".format(
                            response.status_code, url))
                    continue
                location = urljoin(url, response.headers["location"])
                self.message("info", "got {0} redirect to {1!r}".format(
                    response.status_code, location))
                self.enqueue(location)
                continue
            # If we got a non-200 response, log it
            if response.status_code != 200:
                self.message("warning", "got {0} response for {1!r}".format(
                    response.status_code, url))
                continue
            # If we get non-HTML, log it
            if "content-type" not in response.headers:
                self.message("warning", "no Content-Type, assuming HTML")
            else:
                raw_content_type = response.headers["content-type"]
                content_type = raw_content_type.split(';')[0].strip().lower()
                if content_type not in set(["text/html", "application/xhtml+xml"]):
                    self.message("info", "Content-Type is {0!r}, skipping".format(
                        raw_content_type))
                    continue
            # If we get here, it's a normal response and needs to be parsed.
            raw = response.text
            try:
                parsed = BeautifulSoup(raw, 'html.parser')
            except:
                self.message("warning", "exception parsing page:\n{0}".format(
                    traceback.format_exc()))
                continue
            # Detect META nofollow tags
            follow = True
            for meta in parsed.find_all("meta"):
                name = self._scalar(meta.get("name"))
                content = self._scalar(meta.get("content"))
                if name is not None and content is not None:
                    if name.lower() == "robots" and content.lower() == "nofollow":
                        follow = False
                        break
            # Enqueue all followable URL's found
            if follow:
                for link in parsed.find_all("a"):
                    rel = self._scalar(link.get("rel"))
                    if rel is not None and rel.lower() == "nofollow":
                        continue
                    href = self._scalar(link.get("href"))
                    if href is not None:
                        self.message("info", "found link to " + repr(href))
                        self.enqueue(urljoin(url, href))
            # Issue callback
            self.message("info", "issuing callback for " + repr(url))
            self.visit(url, raw, parsed)
            # end crawling loop

    def _scalar(self, v):
        if isinstance(v, list) or isinstance(v, tuple):
            return v[0]
        return v

    def enqueue(self, url):
        """
        Enqueue a single normalized URL to be crawled, if it has not
        already been done so.
        """
        # Parse the url
        parsed = urlparse(url)
        # Reject non-HTTP(s) URLs
        scheme = parsed.scheme
        if scheme is None:
            return
        scheme = scheme.lower()
        if scheme not in set(["http", "https"]):
            return
        # Reject domains outside our scope, if requested
        if self.domain is not None:
            host = parsed.hostname.lower()
            if host is None:
                return
            if not(host == self.domain or host.endswith('.' + self.domain)):
                return
        # Canonicalize
        rcanon = list(parsed)
        rcanon[5] = ""  # Delete any URL fragment
        canonical = urlunparse(rcanon)
        # Reject things already enqueued for crawling
        if canonical in self.seen:
            return
        # If we get here, it should be enqueued
        self.queue.append(url)
        self.seen.add(canonical)

    def message(self, level, text):
        """
        Log a message.
        """
        # By default, we are silent
        pass
