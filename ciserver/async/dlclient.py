#!/usr/bin/python3

import asyncio
import aiohttp
import contextlib
import pathlib
from dataclasses import dataclass, field
from collections import OrderedDict
from typing import List, Iterator, Tuple, Optional
from ietfdata import datatracker

import paths  


@dataclass(frozen=True)
class URI:
    uri: str


@dataclass(frozen=True)
class DocURI(URI):
    def __post_init__(self) -> None:
        assert self.uri.startswith("https://www.ietf.org/archive/id")

    def doc_preference( self ): 
        uri_p = pathlib.Path( self.uri )

        # these alternates are in descending order of preference 
        # Please maintain order of preference 
        alternates = OrderedDict() 
        alternates['.xml'] = URIxml 
        alternates['.txt'] = URItext 
        return [ obj( str(uri_p.parent / ( uri_p.stem + ext ))) 
                for ext, obj in alternates.items() if ext != uri_p.stem ]



@dataclass(frozen=True)
class URIxml(DocURI):
    def __post_init__(self) -> None :
        assert str(pathlib.Path( self.uri ).stem ) == '.xml', f"uri {self.uri} does not end in .xml"



@dataclass(frozen=True)
class URItext(DocURI):
    def __post_init__(self) -> None :
        assert str(pathlib.Path( self.uri ).stem ) == '.txt', f"uri {self.uri} does not end in .txt"


@dataclass(frozen=True)
class DownloadOptions:
    force: bool = False  # if set to True, override files in cache


@dataclass
class DownloadClient:
    fslock: paths.FileSysLock
    request_limit: Optional[int] = 10
    dlopts: Optional[DownloadOptions] = field(default_factory=DownloadOptions)
    lock: asyncio.locks.Lock = field(default_factory=asyncio.Lock)

    async def __aenter__(self) -> None:
        await self.lock.acquire()
        self.req_limit = asyncio.Semaphore(self.request_limit)
        return self

    async def __aexit__(self, ex_type, ex, ex_tb) -> None:
        self.lock.release()

    async def _download_url(self, session, url: str,
                            dl_filename: str) -> Tuple[int, str, str, str]:
        print(f"downloading --> {url}")
        stat, data = (None, None)
        async with self.req_limit as _sem:
            async with session.get(url) as response:
                data = await response.text()
                return (response.status, url, dl_filename, data)
        return (stat, url, dl_filename, data)

    async def download_urls(self, urls: List[Tuple[str, str]]) -> None:
        async with aiohttp.ClientSession() as session:
            dl_tasks = [ self._download_url(session, url[0], url[1]) for url in urls ]
            alt_url = None
            for doc in asyncio.as_completed(dl_tasks):
                stat, url, filename, data = await doc
                assert stat == 200, f"Fetching url {url} Failed, err = {stat}"
                # Write text file to lock structure
                _filename = str(self.fslock.fs.drafts) + f"/{filename}"
                with open(_filename, 'w') as fp:
                    fp.write(data)


async def download_urls(urls):
    async with paths.FileSysLock( paths.RootWorkingDir(pathlib.Path.cwd() / "test_dir")) as fslock, \
                    DownloadClient( fslock, request_limit=10) as dlclient:
        await dlclient.download_urls(urls)


def download_draft_daterange(
        since: str = "1970-01-01T00:00:00",
        until: str = "2038-01-19T03:14:07",
        dlopts: DownloadOptions = DownloadOptions()) -> None:
    track = datatracker.DataTracker()
    draft_itr = track.documents(since=since,
                                until=until,
                                doctype=track.document_type("draft"))
    urls = []
    for draft in draft_itr:
        _url = draft.document_url()
        if not dlopts.force:
            # TODO : check whether the file was already downloaded
            # We could use an initial synchronisation run to sha-256 every file in the directory
            # to ensure consistency
            # For now just check the file names
            pass
        urls.append((_url, f"{pathlib.Path( _url ).name}"))
    # Download files in parallel
    evloop = asyncio.get_event_loop()
    evloop.run_until_complete(download_urls(urls))
    evloop.close()



#async def get_url(session, url: str, rate_limit):
#    print(f"{url}")
#    stat, data = (None, None)
#    async with rate_limit as _sem:
#        async with session.get(url) as response:
#            data = await response.text()
#            return (response.status, url, data)
#    return (stat, url, data)
#
##
#async def batch_download(urls, max_download: int) -> None:
#    rate_limit = asyncio.Semaphore(max_download)
#    async with aiohttp.ClientSession() as session:
#        dl_tasks = [get_url(session, url, rate_limit) for url in urls]
#        for doc in asyncio.as_completed(dl_tasks):
#            stat, url, data = await doc
#            assert stat == 200, f"Fetching url {url} Failed, err = {stat}"
#            print("======================================")
#            print(f"url = {url} , stat = {stat}")
#            with open("./test_dir/" + pathlib.Path(url).name, 'w') as fp:
#                fp.write(data)
#
#    await session.close()
#

#def get_urls():
#    track = datatracker.DataTracker()
#    draft_itr = track.documents(since='2020-03-24T00:00:00',
#                                doctype=track.document_type("draft"))
#    draft = []
#    for idx, itr in enumerate(draft_itr):
#        print(f"Doc-[{idx}] --> {itr.document_url()}")
#        draft.append(itr.document_url())
#    return draft


if __name__ == '__main__':
    #urls = [
    #    'http://cnn.com',
    #    'http://nytimes.com',
    #    'http://google.com',
    #    'http://leagueoflegends.com',
    #    'http://python.org']

    #evloop = asyncio.get_event_loop()
    #evloop.run_until_complete( batch_download(get_urls(), 2 ))
    #evloop.close()
    #debug()
    download_draft_daterange(since="2020-03-23T00:00:00")

    #print("get-urls returned = \n{durls}".format(durls=get_urls()))
