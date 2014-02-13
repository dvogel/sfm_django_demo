import re
import os.path

import lxml.html

from superfastmatch.djangomodelmixin import DjangoModelMixin
from django.db import models


class USBill(DjangoModelMixin, models.Model):
    text = models.TextField()
    bill_type = models.CharField(max_length=7)
    number = models.IntegerField()
    congress = models.IntegerField()
    text_version = models.CharField(max_length=4)

    GPO_HTM_File_Pattern = re.compile(ur'^BILLS-(\d+)(hjres|hconres|hres|hr|sjres|sconres|sres|s)(\d+)([a-z]+)\.htm$')

    @classmethod
    def from_gpo_htm_file(cls, path):
        filename = os.path.basename(path)
        match = cls.GPO_HTM_File_Pattern.match(filename)
        if match is None:
            raise Exception(ur"Invalid filename: {}".format(filename))

        ident_values = {'congress': match.group(1),
                        'bill_type': match.group(2),
                        'number': match.group(3),
                        'text_version': match.group(4)}
        (bill_mdl, created) = USBill.objects.get_or_create(**ident_values)
        with open(path, 'r') as htmfile:
            html = lxml.html.parse(htmfile)
            bill_mdl.text = html.find('body').find('pre').text
            bill_mdl.save()

        return bill_mdl

    def sfm_text(self):
        return self.text

    def sfm_attributes(self):
        return {
            u'bill_type': self.bill_type,
            u'number': unicode(self.number),
            u'text_version': self.text_version
        }
