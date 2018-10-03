# -*- coding: utf-8 -*-
from akad.ttypes import TalkException, ShouldSyncException
from .client import LINE
from types import *
from threading import Thread
import os, sys, threading, time

import os, sys, threading, time

class OEPoll(object):
    OpInterrupt = {}
    client = None
    __squareSubId = {}
    __squareSyncToken = {}

    def __init__(self, client):
        if type(client) is not LINE:
            raise Exception('You need to set LINE instance to initialize OEPoll')
        self.client = client
    
    def __fetchOperation(self, revision, count=1):
        return self.client.poll.fetchOperations(revision, count)
    
    def __execute(self, op, threading):
        try:
            if threading:
                _td = threading.Thread(target=self.OpInterrupt[op.type](op))
                _td.daemon = False
                _td.start()
            else:
                self.OpInterrupt[op.type](op)
        except Exception as e:
            self.client.log(e)

    def addOpInterruptWithDict(self, OpInterruptDict):
        self.OpInterrupt.update(OpInterruptDict)

    def addOpInterrupt(self, OperationType, DisposeFunc):
        self.OpInterrupt[OperationType] = DisposeFunc
    
    def setRevision(self, revision):
        self.client.revision = max(revision, self.client.revision)

    def singleTrace(self, count=1):
        try:
            operations = self.__fetchOperation(self.client.revision, count=count)
        except KeyboardInterrupt:
            exit()
        except:
            return
        
        if operations is None:
            return []
        else:
            return operations
class MultiThreads:
    threads = None
    max_threads = 0.2
    to_run = None

    def __init__(self):
        self.threads = []
        self.to_run = []
        try:
            import multiprocessing
            self.max_threads = multiprocessing.cpu_count()
        except Exception:
            pass

    def add(self, target: callable, args: tuple):
        self.threads.append(Thread(target=target, args=args))

    def _run_processes(self, callback: callable=None, n: int = None):
        for t in self.to_run:
            if not n:
                t.join()
                callback is not None and callback()

    def start(self, callback: callable=None):
        for n, t in enumerate(self.threads):  # starting all threads
            t.start()
            self.to_run.append(t)
            self._run_processes(callback, (n + 1) % self.max_threads)
        self._run_processes(callback)
        self.threads = []

    def trace(self, threading=False):
        try:
            operations = self.__fetchOperation(self.client.revision)
        except KeyboardInterrupt:
            exit()
        except:
            return
    def trace(self, threading=False):
        try:
            operations = self.__fetchOperation(self.client.revision)
        except KeyboardInterrupt:
            exit()
        except:
            return
        
        for op in operations:
            if op.type in self.OpInterrupt.keys():
                self.__execute(op, threading)
            self.setRevision(op.revision)

    def singleFetchSquareChat(self, squareChatMid, limit=1):
        if squareChatMid not in self.__squareSubId:
            self.__squareSubId[squareChatMid] = 0
        if squareChatMid not in self.__squareSyncToken:
            self.__squareSyncToken[squareChatMid] = ''
        
        sqcEvents = self.client.fetchSquareChatEvents(squareChatMid, subscriptionId=self.__squareSubId[squareChatMid], syncToken=self.__squareSyncToken[squareChatMid], limit=limit, direction=1)
        self.__squareSubId[squareChatMid] = sqcEvents.subscription
        self.__squareSyncToken[squareChatMid] = sqcEvents.syncToken

        return sqcEvents.events
