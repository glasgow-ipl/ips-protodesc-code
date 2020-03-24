#!/usr/bin/python3

from dataclasses import dataclass, field
from datetime import datetime
import pathlib
import logging
import contextlib
import json
import os
import asyncio


@dataclass
class RootWorkingDir:
    root  : pathlib.Path = field( default_factory=lambda: pathlib.Path(pathlib.Path.cwd()))
    lock  : pathlib.Path = field(default=None, init=False)
    db    : pathlib.Path = field(default=None, init=False)
    rfc   : pathlib.Path = field(default=None, init=False)
    drafts: pathlib.Path = field(default=None, init=False)
    output: pathlib.Path = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.root = self.root.resolve()

        if not self.root.exists():
            logging.error(f"Root dir <{self.root}> does not exist.")
            if not self.root.is_dir():
                logging.error(f"<{self.root} is not a directory")
            raise AssertionError(f"Error writing to directory {self.root}")

        assert self.root.exists(), f"Root dir <{self.root}> does not exist."
        assert self.root.is_dir(), f"<{self.root} is not a directory"
        # TODO : Also add check to see if directory is writable
        self.lock = self.root / ".lock"
        self.db = self.root / ".db"
        self.rfc = self.root / "rfc"
        self.drafts = self.root / "drafts"
        self.output = self.root / "output"


@dataclass(frozen=True)
class FileSysLock(contextlib.ContextDecorator):
    fs      : RootWorkingDir
    pid     : int = field(default_factory = os.getpid, init = False)
    pid_lock: asyncio.locks.Lock = field(default_factory = asyncio.Lock, init = False )

    async def __aenter__(self):
        if self.fs.lock.exists():
            with open(self.fs.lock, 'r') as fp:
                _lock = json.load(fp)
                raise AssertionError( f"Process {_lock['pid']} holds lockfile {self.fs.lock}")
            raise AssertionError( f"Another Process holds lockfile {self.fs.lock}") 

        await self.pid_lock.acquire()  
        with open(self.fs.lock, 'w') as fp: 
            json.dump( { "start_time": datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M:%S"), 
                    "pid": self.pid }, fp)

        self.fs.drafts.mkdir(exist_ok=True) 
        self.fs.rfc.mkdir(exist_ok=True) 
        return self

    async def __aexit__(self, ex_type, ex, ex_tb):
        assert self.pid == os.getpid(), f"Only pid - {self.pid} allowed to remove {self.fs.lock}"
        self.fs.lock.unlink()
        logging.info(
            f"pid {self.pid} released {self.fs.lock} at"
            f" {datetime.strftime(datetime.utcnow(),'%Y-%m-%d %H:%M:%S')}")
        self.pid_lock.release()

async def debug():
    async with FileSysLock( RootWorkingDir( pathlib.Path(
                    "/home/dejice/../dejice/./work/ietf/ips-protodesc-code/ciserver/test_dir"))) as r3:
        print(f"root = {r3.fs.root},\n"
              f"lock = {r3.fs.lock},\n"
              f"db = {r3.fs.db},\n"
              f"rfc = {r3.fs.rfc},\n"
              f"drafts = {r3.fs.drafts},\n"
              f"output = {r3.fs.output}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop() 
    loop.run_until_complete(debug()) 
    loop.close()
