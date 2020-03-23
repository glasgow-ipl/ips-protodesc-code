#!/usr/bin/python3 

import asyncio
import aiohttp
import contextlib 
import pathlib
from ietfdata import datatracker







async def get_url(session, url: str):
    print(f"{url}") 
    stat, data = (None, None)
    async with session.get(url) as response: 
        data = await response.text()
        return (response.status, url, data)
    return (stat, url, data)

async def batch_download( urls , max_download:int) -> None :
    rate_limit = asyncio.Semaphore( max_download )
    async with aiohttp.ClientSession() as session :
        dl_tasks = [ get_url(session, url) for url in urls ]
        for doc in asyncio.as_completed( dl_tasks ):
            stat, url, data = await doc 
            assert stat == 200, f"Fetching url {url} Failed, err = {stat}"
            print("======================================")
            print(f"url = {url} , stat = {stat}")
            with open( pathlib.Path(url).name, 'w') as fp:
                fp.write(data)
            
    await session.close() 

def get_urls():
    track = datatracker.DataTracker()
    draft_itr = track.documents(since='2020-03-22T00:00:00', doctype = track.document_type("draft"))
    draft = [] 
    for idx, itr in enumerate(draft_itr):
        print(f"Doc-[{idx}] --> {itr.document_url()}")
        draft.append(itr.document_url()) 
    return draft
   


if __name__ == '__main__':
    evloop = asyncio.get_event_loop()
    #urls = [
    #    'http://cnn.com',
    #    'http://nytimes.com',
    #    'http://google.com',
    #    'http://leagueoflegends.com',
    #    'http://python.org'
    #]
    evloop.run_until_complete( batch_download(get_urls(), 3 ))
    evloop.close() 

    #print("get-urls returned = \n{durls}".format(durls=get_urls()))
