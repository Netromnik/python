# -*- coding: utf-8 -*-

import yaml
import os.path
import collections

from django.conf import settings

from irk.utils.files.helpers import static_link


class Smile(collections.namedtuple('Smile', ['id', 'title', 'code', 'image_code'])):

    def __init__(self, *args, **kwargs):
        super(Smile, self).__init__(*args, **kwargs)
        self._prepared_html = None

    @property
    def url(self):
        # TODO: кэшировать это значение
        return static_link('img/smiles/{0}.gif'.format(self.image_code))

    def __unicode__(self):
        if self._prepared_html is None:
            self._prepared_html = u'<img title="{0}" src="{1}" alt="{0}" />'.format(self.title, self.url)
        return self._prepared_html


# Список всех смайлов
smiles = []

# Список смайлов, где на одну картинку приходится только один код.
# Например, для /img/smiles/bn.gif есть только код *WASSUP*, но не *SUP*
simple_smiles = []

with open(os.path.join(settings.BASE_PATH, 'smiles.yaml'), 'r') as f:
    smiles_fixture = yaml.safe_load(f)

    idx = 0
    for image_code, data in smiles_fixture.items():
        for pos, code in enumerate(data['code']):
            smile = Smile(idx, data['title'], code, image_code)
            smiles.append(smile)

            if pos == 0:
                simple_smiles.append(smile)

            idx += 1

    del smiles_fixture

smiles = frozenset(smiles)
simple_smiles = frozenset(simple_smiles)
