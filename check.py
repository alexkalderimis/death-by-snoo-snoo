from snoosnoo import weapons

from intermine.webservice import Service

import logging

logger = logging.getLogger('snoosnoo')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

flymine = Service("www.flymine.org/query")

class Counter:
    def add(self, n):
        pass

w = weapons.Lists(flymine, Counter())

w.attack()

w = weapons.Search(flymine, Counter())

w.attack()
