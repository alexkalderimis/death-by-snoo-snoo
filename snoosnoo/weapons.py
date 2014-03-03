import random
import logging
import json
import string

from contextlib import closing

from intermine.webservice import Service

log = logging.getLogger('snoosnoo.weapons')

class Weapon(object):

    def __init__(self, service, counter):
        self.service = service
        self.counter = counter

    def besiege(self):
        while True:
            try:
                self.attack()
            except Exception as e:
                log.error(e)

class Search(Weapon):

    LOG = logging.getLogger('snoosnoo.weapons.Search')

    def attack(self):
        self.do_search(random.choice(string.letters))
        self.counter.add(1)

        self.do_search(random.choice(string.letters) + random.choice(string.letters))
        self.counter.add(1)

    def do_search(self, term):
        service = self.service
        with closing(service.opener.open(service.root + "/search?q=" + term)) as sock:
            results = json.loads(sock.read())['results']
            Search.LOG.debug("Found %d results for %s", len(results), term)
            if results:
                Search.LOG.debug("First result: %s", results[0])
            self.counter.add(1)

class Lists(Weapon):

    LOG = logging.getLogger('snoosnoo.weapons.Lists')

    def attack(self):
        service = Service(self.service.root)
        self.counter.add(2)

        lists = list(l for l in service.get_all_lists() if l.size and l.status == 'CURRENT')
        Lists.LOG.debug("%d lists", len(lists))
        self.counter.add(1)

        target = random.choice(lists)

        classkeys = None
        with closing(service.opener.open(service.root + "/classkeys")) as sock:
            classkeys = json.loads(sock.read())['classes']
            Lists.LOG.debug("Classkeys for %s are %r", target.name, classkeys[target.list_type])
            self.counter.add(1)

        q = service.query(target.list_type).where(target.list_type, 'IN', target.name)

        index = random.randint(0, target.size - 1)
        rand_member = next(q.rows(size = 1, start = index))
        self.counter.add(1)
        Lists.LOG.debug(rand_member)

        target_keys = classkeys[target.list_type]
        if target_keys:
            lu_q = q.where(target.list_type, 'LOOKUP', rand_member[target_keys[0]])
            Lists.LOG.debug("lookup q: %s", lu_q)
            Lists.LOG.debug("%s should be one", lu_q.count())
            self.counter.add(1)

        suitable_widgets = list(w for w in service.widgets.values() if w['widgetType'] == 'enrichment' and target.list_type in w['targets'])
        self.counter.add(1)

        if not suitable_widgets:
            return

        widget = random.choice(suitable_widgets)

        Lists.LOG.debug("Calculating %s of %s", widget['name'], target.name)
        enriched = list(target.calculate_enrichment(widget['name']))
        self.counter.add(1)

        if enriched:
            Lists.LOG.debug(enriched[0])


class Queries(Weapon):

    LOG = logging.getLogger('snoosnoo.weapons.Queries')

    def attack(self):
        model = self.service.model

        table = random.choice(model.classes.values())
        query = self.service.query(table.name)

        c = query.count()
        self.counter.add(1)

        Queries.LOG.debug("%d instances of %s", c, table.name)

        value_attrs = list(a for a in table.attributes if a.name != 'id')

        if c and value_attrs:
            string_attrs = list(a for a in value_attrs if a.type_name == 'String')
            if string_attrs:
                attr = random.choice(string_attrs)
                values = filter(None, query.summarise(attr.name, size = 10).keys())
                self.counter.add(1)
                if values:
                    top_attr = random.choice(values)
                    q = query.where(attr.name, '=', top_attr)

                    cons_c = q.count()
                    self.counter.add(1)

                    Queries.LOG.debug("%d instances of %s where %s = %s", cons_c, table.name, attr.name, top_attr)
