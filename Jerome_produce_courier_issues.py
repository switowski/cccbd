# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Script to create the main MARCXML record for a CERN Courier issue
based on the files provided by the Indians on the individual articles.
"""

import os
import sys
from invenio.bibrecord import create_record, record_order_fields, field_xml_output, record_get_field_value

def main(top_path):
    print 'Starting...'
    print 'Reading from %s' % top_path


    for (dirpath, dirnames, filenames) in os.walk(top_path, topdown=True, onerror=None, followlinks=False):
        splitted_dirpath = dirpath.split(os.sep)
        if splitted_dirpath[-1] == 'XML':
            new_xml_filename = splitted_dirpath[-2] + '.xml'
            new_xml_filepath = os.path.join(dirpath, new_xml_filename)
            if not os.path.exists(new_xml_filename):
                pdf_path = os.sep.join(splitted_dirpath[:-1]) + os.path.sep + 'PDF' + os.path.sep + splitted_dirpath[-2] + '.pdf'
                # We take one of the articles inside directory (doesn't matter which one) and create a record based on the XML of this article
                sample_article_path_for_issue = os.path.join(dirpath, [filename for filename in filenames if filename.endswith('.xml')][0])
                sample_article_xml_for_issue = open(sample_article_path_for_issue).read()
                sample_article_record_for_issue = create_record(sample_article_xml_for_issue)[0]
                collection = record_get_field_value(sample_article_record_for_issue, tag='980', ind1=" ", ind2=" ", code="a")
                # We now have a record for an article. Now we modify some fields and we get the XML for whole issue

                if 'COURIER' in collection:
                    reused_fields = record_xml_output(sample_article_record_for_issue, ['041', '773'])
                    journal_collection = 'CERN_COURIER_ISSUE'
                    email = "cern.courier@cern.ch"
                    language = record_get_field_value(sample_article_record_for_issue, tag='041', ind1=" ", ind2=" ", code="a")
                    year = record_get_field_value(sample_article_record_for_issue, tag='260', ind1=" ", ind2=" ", code="c")
                    volume = record_get_field_value(sample_article_record_for_issue, tag='773', ind1=" ", ind2=" ", code="v")
                    number = record_get_field_value(sample_article_record_for_issue, tag='773', ind1=" ", ind2=" ", code="n")
                    date = record_get_field_value(sample_article_record_for_issue, tag='269', ind1=" ", ind2=" ", code="c")
                    # From October 1998, the publisher is IOP
                    if year > '1998' or (year == '1998' and date[:-5] in ['October', 'November', 'December', 'Octobre', 'Novembre', 'Décembre']):
                        publication_place = 'Bristol'
                        publisher = 'IOP'
                    else:
                        publication_place = 'Geneva'
                        publisher = 'CERN'

                    if language == "eng":
                        new_title = "CERN Courier Volume %(vol)s, Number %(num)s, %(date)s" % {
                            'vol': volume,
                            'num': number,
                            'date': date
                        }
                    elif language == "fre":
                        new_title = "Courrier CERN Volume %(vol)s, N° %(num)s, %(date)s" % {
                            'vol': volume,
                            'num': number,
                            'date': date
                        }
                    publication = \
'''<datafield tag="260" ind2=" " ind1=" ">
    <subfield code="a">%(publication_place)s</subfield>
    <subfield code="b">%(publisher)s</subfield>
    <subfield code="c">%(year)s</subfield>
    </datafield>'''     % {'publication_place': publication_place,
                           'publisher': publisher,
                           'year': year}

                else:
                    # Bulletin
                    reused_fields = \
'''<datafield tag="041" ind1=" " ind2=" ">
    <subfield code="a">eng</subfield>
  </datafield>
  <datafield tag="041" ind1=" " ind2=" ">
    <subfield code="a">fre</subfield>
  </datafield>
'''

                    reused_fields += record_xml_output(sample_article_record_for_issue, ['773'])
                    journal_collection = 'CERN_BULLETIN_ISSUE'
                    email = "bulletin-editors@cern.ch"
                    year = record_get_field_value(sample_article_record_for_issue, tag='260', ind1=" ", ind2=" ", code="c")
                    number = record_get_field_value(sample_article_record_for_issue, tag='773', ind1=" ", ind2=" ", code="n")
                    new_title = "CERN Bulletin Issue No. %(num)s/%(year)s" % {
                        'num': number,
                        'year': year
                    }
                    publication = \
'''<datafield tag="260" ind2=" " ind1=" ">
    <subfield code="a">Geneva</subfield>
    <subfield code="b">CERN</subfield>
    <subfield code="c">%s</subfield>
    </datafield>''' % year

                # Create new XML file
                new_xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<record>
  <datafield tag="110" ind2=" " ind1=" ">
    <subfield code="a">CERN</subfield>
  </datafield>
  <datafield tag="245" ind2=" " ind1=" ">
    <subfield code="a">%(title)s</subfield>
  </datafield>
  %(publication)s
  %(other)s
  <datafield tag="856" ind2=" " ind1="0">
    <subfield code="f">%(email)s</subfield>
  </datafield>
  <datafield tag="FFT" ind1=" " ind2=" ">
    <subfield code="a">%(mainfile)s</subfield>
    <subfield code="t">Main</subfield>
  </datafield>
  <datafield tag="980" ind2=" " ind1=" ">
    <subfield code="a">%(collection)s</subfield>
  </datafield>
</record>
    ''' % {'other': reused_fields,
           'publication': publication,
           'title': new_title,
           'collection': journal_collection,
           'email': email,
           'mainfile': pdf_path}
                fd = file(new_xml_filepath, 'w')
                fd.write(new_xml_content)
                fd.close()
                print "Created %s" % new_xml_filepath

    print 'Finished.'


def record_xml_output(rec, tags=None, order_fn=None):
    """Generates the XML for record 'rec' and returns it as a string
    @rec: record
    @tags: list of tags to be printed"""
    if tags is None:
        tags = []
    if isinstance(tags, str):
        tags = [tags]

    marcxml = []

    # Add the tag 'tag' to each field in rec[tag]
    fields = []
    if rec is not None:
        for tag in rec:
            if not tags or tag in tags:
                for field in rec[tag]:
                    if tag == '773':
                        field = ([subfield for subfield in field[0] if subfield[0] != 'c'], field[1], field[2], field[3], field[4])
                    fields.append((tag, field))
        if order_fn is None:
            record_order_fields(fields)
        else:
            record_order_fields(fields, order_fn)
        for field in fields:
            marcxml.append(field_xml_output(field[1], field[0]))
    return '\n'.join(marcxml)

if __name__ == "__main__":
    main(sys.argv[-1])
