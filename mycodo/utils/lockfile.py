# coding=utf-8
import logging
import os
import time

import filelock

logger = logging.getLogger("mycodo.lockfile")

if logging.getLevelName(logging.getLogger().getEffectiveLevel()) == 'INFO':
    logger.setLevel(logging.INFO)


class LockFile:
    def __init__(self):
        self.lock = {}
        self.locked = {}

    def lock_acquire(self, lockfile, timeout):
        """ Non-blocking locking method """
        self.lock[lockfile] = filelock.FileLock(lockfile, timeout=1)
        self.locked[lockfile] = False
        timer = time.time() + timeout
        logger.debug("Acquiring lock for {} ({} sec timeout)".format(lockfile, timeout))
        while time.time() < timer:
            try:
                self.lock[lockfile].acquire()
                seconds = time.time() - (timer - timeout)
                logger.debug("Lock acquired for {} in {:.3f} seconds".format(lockfile, seconds))
                self.locked[lockfile] = True
                break
            except:
                pass
            time.sleep(0.05)
        if not self.locked[lockfile]:
            logger.debug("Lock unable to be acquired after {:.3f} seconds. Breaking lock.".format(timeout))
            self.lock_release(lockfile)

    def lock_release(self, lockfile):
        """ Release lock and force deletion of lock file """
        try:
            logger.debug("Releasing lock for {}".format(lockfile))
            self.lock[lockfile].release(force=True)
            os.remove(lockfile)
        except Exception:
            pass
        finally:
            self.locked[lockfile] = False
