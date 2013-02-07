#!/usr/bin/env python

import os
import sys
import logging

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(
        sys.argv[0]), os.pardir, os.pardir))

if os.path.exists(os.path.join(possible_topdir, "giraffe", "__init__.py")):
    sys.path.append(possible_topdir)


from giraffe.client import client

if __name__ == '__main__':

    logger = logging.getLogger("client")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    fh = logging.FileHandler("client.log")

    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info("Starting Giraffe Client")

    # creating a client
    app = client.GiraffeClientApp()
    
    try:
        # setting up the application
        app.setup()
        app.run()
    except Exception:
        logger.exception(('Failed to load %s') % 'Client')
    finally:
        # closing the application
        app.close()
