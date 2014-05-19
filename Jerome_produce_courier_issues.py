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
                sample_article_path_for_issue = os.path.join(dirpath, [filename for filename in filenames if filename.endswith('.xml')][0])
                sample_article_xml_for_issue = open(sample_article_path_for_issue).read()
                sample_article_record_for_issue = create_record(sample_article_xml_for_issue)[0]
                collection = record_get_field_value(sample_article_record_for_issue, tag='980', ind1=" ", ind2=" ", code="a")

                if 'COURIER' in collection:
                    reused_fields = record_xml_output(sample_article_record_for_issue, ['041', '260', '269', '690', '773'])
                    journal_collection = 'COURIERISSUEARCHIVE'
                    ln = record_get_field_value(sample_article_record_for_issue, tag='041', ind1=" ", ind2=" ", code="a")
                    ln_long = ln
                    if ln.lower().startswith('fr'):
                        ln_long = "Français"
                    elif ln.lower().startswith('en'):
                        ln_long = "English"
                    new_title = record_get_field_value(sample_article_record_for_issue, tag='773', ind1=" ", ind2=" ", code="p") + \
                    ' n° ' + record_get_field_value(sample_article_record_for_issue, tag='773', ind1=" ", ind2=" ", code="n") + \
                    ' vol. ' + record_get_field_value(sample_article_record_for_issue, tag='773', ind1=" ", ind2=" ", code="v") + \
                    ' ' + record_get_field_value(sample_article_record_for_issue, tag='269', ind1=" ", ind2=" ", code="c") + \
                    ' (%s)' % ln_long

                else:
                    reused_fields = '''<datafield tag="041" ind1=" " ind2=" "><subfield code="a">en</subfield></datafield>
    <datafield tag="041" ind1=" " ind2=" "><subfield code="a">fr</subfield></datafield>
'''
                    reused_fields += record_xml_output(sample_article_record_for_issue, ['260', '269', '690', '773'])
                    journal_collection = 'BULLETINISSUEARCHIVE'
                    new_title = record_get_field_value(sample_article_record_for_issue, tag='773', ind1=" ", ind2=" ", code="t") + \
                        ' Issue No. ' + record_get_field_value(sample_article_record_for_issue, tag='773', ind1=" ", ind2=" ", code="n")

                new_xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<record>
    <datafield tag="245" ind2=" " ind1=" "><subfield code="a">%(title)s</subfield></datafield>
    %(other)s
    <datafield tag="980" ind2=" " ind1=" "><subfield code="a">%(collection)s</subfield></datafield>
    <datafield tag="FFT" ind1=" " ind2=" ">
    <subfield code="a">%(mainfile)s</subfield>
    <subfield code="t">Main</subfield>
    </datafield>
</record>
    ''' % {'other': reused_fields,
           'title': new_title,
           'collection': journal_collection,
           'mainfile': pdf_path}
                fd = file(new_xml_filepath, 'w')
                fd.write(new_xml_content)
                fd.close()
                print "Created %s" % new_xml_filepath

    print 'Finished.'

def remove_page_field(matchobj):
    print 'found ' + matchobj.group()
    return matchobj.group().replace(matchobj.group('pagefield'), '')

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
