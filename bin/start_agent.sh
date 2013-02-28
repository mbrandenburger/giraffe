#!/usr/bin/env python

"""
Starts a Giraffe agent, reading configuration parameters from a 'giraffe.cfg'
file (by default, expected to be found at os.sep.join(__file__.split(os.sep)
[0:-3] + ['bin', path]) - optionally, a different location can be passed
through --config.

Dependencies: psutil, pika
"""


if __name__ == '__main__':

    import os
    import sys

    possible_topdir = os.path.normpath(os.path.join(
                                            os.path.abspath(sys.argv[0]),
                                            os.pardir,
                                            os.pardir))

    if os.path.exists(os.path.join(possible_topdir, 'giraffe', '__init__.py')):
        sys.path.append(possible_topdir)

    # -------------------------------------------------------------------------

    from argparse import ArgumentParser

    parser = ArgumentParser(description='Start a new Giraffe agent instance.')
    parser.add_argument('--config', action='store', default='giraffe.cfg', \
                        help='path to giraffe.cfg file')
    parser.add_argument('--debug', action='store_true', \
                        help='logging level =DEBUG, else =INFO')
    parser.add_argument('--stream', action='store_true', \
                        help='stream logging output to sys.stdout')
    args = parser.parse_args()

    # -------------------------------------------------------------------------

    import logging

    logger = logging.getLogger('agent')
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('agent.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    if args.stream:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    # -------------------------------------------------------------------------    

    from giraffe.agent import agent

    logger.info('Starting Giraffe agent...')
    
    try:
        agent = agent.Agent(cfg=args.config)
        agent.launch()
    except (Exception, SystemExit):
        logger.exception(('Failed to load %s') % 'agent.')
