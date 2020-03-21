#!/usr/bin/python3 

import asyncio
import aiohttp
import contextlib 


async def debug(arg1, arg2):
    print(f"{arg1} -- {arg2}")
    async with aiohttp.ClientSession() as session :
        async with session.get('https://api.github.com/events') as response:
            print(f"status = {response.status}")
            print(await response.text()) 
    await session.close() 

if __name__ == '__main__':
    evloop = asyncio.get_event_loop()
    evloop.run_until_complete( debug("hello", "world") )
    evloop.close() 

 
