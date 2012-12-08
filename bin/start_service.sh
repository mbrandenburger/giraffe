#!/usr/bin/env python

import os
import sys
import logging

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))

if os.path.exists(os.path.join(possible_topdir, "giraffe", "__init__.py")):
    sys.path.append(possible_topdir)

from giraffe.service import service

if __name__ == '__main__':

    logger = logging.getLogger("service")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    fh = logging.FileHandler("service.log")

    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info("Start Giraffe Service")

    try:
            service = service.Service()
            service.launch()
    except (Exception, SystemExit):
            logger.exception(('Failed to load %s') % 'Service')


