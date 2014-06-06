#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
from optparse import OptionParser
from lxml import etree
import Levenshtein

CFG_CCCBD_MARCXML_ISSUE_CONTENT_CERN_COURIER = "vol%s-issue%s.xml"

CFG_CCCBD_MARCXML_ISSUE_CONTENT_CERN_COURIER = """
<record>
  <datafield tag="???" ind2=" " ind1=" ">
    <subfield code="?">...........</subfield>
  </datafield>
</record>
"""

CFG_CCCBD_MONTHS_ENG = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
    'January-February',
    'February-March',
    'March-April',
    'April-May',
    'May-June',
    'June-July',
    'July-August',
    'August-September',
    'September-October',
    'October-November',
    'November-December',
    'December-January',
    'Winter',
    'Summer',
]

CFG_CCCBD_MONTHS_FRE = [
    'Janvier',
    'Février',
    'Mars',
    'Avril',
    'Mai',
    'Juin',
    'Juillet',
    'Août',
    'Septembre',
    'Octobre',
    'Novembre',
    'Décembre',
    'Janvier-Février',
    'Février-Mars',
    'Mars-Avril',
    'Avril-Mai',
    'Mai-Juin',
    'Juin-Juillet',
    'Juillet-Août',
    'Août-Septembre',
    'Septembre-Octobre',
    'Octobre-Novembre',
    'Novembre-Décembre',
    'Décembre-Janvier',
    'Hiver',
    'Été',
]

CFG_CCCBD_PUBLICATIONS_CERN_BULLETIN = 'CERN_BULLETIN'
# CFG_CCCBD_PUBLICATIONS_CERN_COURRIER = 'COURRIER_CERN'
CFG_CCCBD_PUBLICATIONS_CERN_COURRIER = 'F'
CFG_CCCBD_PUBLICATIONS = (
    CFG_CCCBD_PUBLICATIONS_CERN_BULLETIN,
    CFG_CCCBD_PUBLICATIONS_CERN_COURRIER,
)

CFG_CCCBD_LANGUAGES_ENG = 'E'
CFG_CCCBD_LANGUAGES_FRE  = 'F'
CFG_CCCBD_LANGUAGES = (
    CFG_CCCBD_LANGUAGES_ENG,
    CFG_CCCBD_LANGUAGES_FRE,
)


CFG_CCCBD_FORMATS_TIFF = 'TIFF'
CFG_CCCBD_FORMATS_PDF  = 'PDF'
CFG_CCCBD_FORMATS_OCR  = 'OCR'
CFG_CCCBD_FORMATS_XML  = 'XML'
CFG_CCCBD_FORMATS_PNG  = 'PNG'
CFG_CCCBD_FORMATS = (
    CFG_CCCBD_FORMATS_TIFF,
    CFG_CCCBD_FORMATS_PDF,
    CFG_CCCBD_FORMATS_OCR,
    CFG_CCCBD_FORMATS_XML,
    CFG_CCCBD_FORMATS_PNG,
)

# Set this to False to ignore a lot of "Incorrect value () in ..." warnings
CFG_NO_EMPTY_FIELDS = True

CFG_CCCBD_MARC_FIELDS_ALLOWED = {
    '041__' : (
        'a',
    ),
    '100__' : (
        'a',
    ),
    '245__' : (
        'a',
    ),
    '246__' : (
        'a',
    ),
    '246_1': (
        'a',
    ),
    '260__' : (
        'c',
    ),
    '269__' : (
        'a',
        'b',
        'c',
    ),
    '520__' : (
        'b',
    ),
    '590__' : (
        'b',
    ),
    '690__' : (
        'a',
    ),
    '773__' : (
        'c',
        'n',
        'p',
        't',
        'v',
        'y',
    ),
    '980__' : (
        'a',
    ),
    'FFT__' : (
        'a',
        't',
        'd',
    ),
# NOTE: Accept FTT for now to avoid the huge amount of errors
    'FTT__' : (
        'a',
        't',
        'd',
    ),
}
CFG_CCCBD_MARC_FIELDS_MINIMUM = {
}
# Some warnings should be ignored in the output but we should remember them later
# British at CERN and a deceased person
CORNER_CASE_WARNINGS_TO_IGNORE = [
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-IXcaptions.xml",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-IXfig.png",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-IXfigcaption.txt",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-pvol24figacaption.txt",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-VIIIcaptions.xml",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-VIIIfig.png",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-VIIIfigcaption.txt",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-Xcaptions.xml",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-Xfiga.png",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-Xfigacaption.txt",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-Xfigb.png",
"There is an unexpected file in COURRIER_CERN/F/1984/vol24-issue8/PNG : vol24-issue8-Xfigbcaption.txt",
"There is an unexpected file in /dfs/cern.ch/COURRIER_CERN/E/1990/vol30-issue7/OCR : vol30-issue7-VII-e.ocr",
"There is an unexpected file in /dfs/cern.ch/COURRIER_CERN/E/1990/vol30-issue7/PDF : vol30-issue7-VII-e.pdf",
"There is an unexpected file in /dfs/cern.ch/COURRIER_CERN/E/1990/vol30-issue7/PNG : vol30-issue7-VIIcaptions.xml",
"There is an unexpected file in /dfs/cern.ch/COURRIER_CERN/E/1990/vol30-issue7/PNG : vol30-issue7-VIIfig.png",
"There is an unexpected file in /dfs/cern.ch/COURRIER_CERN/E/1990/vol30-issue7/PNG : vol30-issue7-VIIfigcaption.txt",
"There is an unexpected file in /dfs/cern.ch/COURRIER_CERN/E/1990/vol30-issue7/XML : vol30-issue7-VII-e.xml"]

# Pattern for checking pagination in subfield 773__c
#PATTERN_PAGINATION = re.compile('(?:[0-9IVX]{1,4}|[0-9IVX]{1,4}-[0-9IVX]{1,4})$')
PATTERN_PAGINATION = re.compile('(?:[0-9IVX]{1,4}|([0-9IVX]{1,4})-([0-9IVX]{1,4}))$')


def _check_if_file_exists_in_other_language(filename, filetype, directory):
    """
    """
    current_file = os.path.sep.join((directory, filename))
    # Change language folder (if we are in folder /E/, change it to /F/ and vice versa)
    # And change the "-e" to "-f" and vice versa in file name
    if filetype == CFG_CCCBD_FORMATS_TIFF:
        # Ignore TIFF files since English version of courier has different publicities than French version,
        # which results in different TIFF files in both directories
        return
    if current_file.find("/E/") != -1:
        other_file = current_file.replace("/E/", "/F/")
        other_file = other_file.replace("-e.", "-f.")
    else:
        other_file = current_file.replace("/F/", "/E/")
        other_file = other_file.replace("-f.", "-e.")
    if not os.path.isfile(other_file):
        _report("[%s] File: %s does not exist in other language" % (filetype, current_file), warn = True)


def _execute_on_each_file(filename, filetype, directory):
    """
    This function is executed for each file.
    You can put more functions here, depending on, for example, the file type.
    This function was created because I was too lazy to refactor all those
    "elif current_dir == CFG_CCCBD_FORMATS_PDF:" statements.
    @param filename: name of the current filename
    @type filename: string
    @param filetype: type of the current filename (PDF, XML, etc.)
    @type filetype: string
    @param directory: name of the current directory
    @type directory: string

    """
    # _check_if_file_exists_in_other_language(filename, filetype, directory)
    pass

def _execute_on_each_directory(current_dir, dirpath):
    """
    Similar to the _execute_on_each_file, but this function is executed once
    inside each PDF, PNG, TIFF, etc. directory
    @param current_dir: name of the directory (for example PDF, TIFF, PNG, etc.)
    @type current_dir: string
    @param dirpath: path to the current directory
    @type dirpath: string
    """
    # compare_number_of_files(dirpath)
    pass

def compare_number_of_files(directory):
    """
    Function that compares the number of files in English and French version of
    a directory and prints a warning when they are different
    """
    if directory.find("/E/") != -1:
        other_directory = directory.replace("/E/", "/F/")
    else:
        other_directory = directory.replace("/F/", "/E/")
    number_of_files_in_dirrectory = len([name for name in os.listdir(directory) \
                                         if os.path.isfile(os.sep.join((directory, name)))])
    try:
        number_of_files_in_other_dirrectory = len([name for name in os.listdir(other_directory)\
                                                   if os.path.isfile(os.sep.join((other_directory, name)))])
    except OSError:
        # the other_directory doesn't exists
        return
    if number_of_files_in_dirrectory != number_of_files_in_other_dirrectory:
        _report("There are %s file in %s and %s files in %s" %\
               (number_of_files_in_dirrectory, directory,
                number_of_files_in_other_dirrectory, other_directory), warn=True)

def _check_marc_content(datafield, subfield, value,
                        current_language, current_volume, current_issue,
                        current_year, directory, is_courier, is_bulletin):
    """
    """

    value = value is not None and value.strip().encode("utf-8") or ""

    (result, error) = (True, "")

    if datafield == "041__":
        if subfield == "a":
            result = ( is_courier  and ( ( current_language.lower() == "e" and value == "en" ) or \
                                         ( current_language.lower() == "f" and value == "fr" ) ) ) or \
                     ( is_bulletin and ( value == "en" or value == "fr" ))

    elif datafield == "100__":
        if subfield == "a":
            if CFG_NO_EMPTY_FIELDS:
                # This field can't be empty
                result = len(value) > 0

    elif datafield == "245__":
        if subfield == "a":
            if CFG_NO_EMPTY_FIELDS:
                # This field can't be empty
                result = len(value) > 0

    elif datafield == "246__":
        if subfield == "a":
            if CFG_NO_EMPTY_FIELDS:
                # This field can't be empty
                result = len(value) > 0

    elif datafield == "246_1":
        if subfield == "a":
            if CFG_NO_EMPTY_FIELDS and is_bulletin:
                # This field can't be empty
                result = len(value) > 0

    elif datafield == "260__":
        if subfield == "c":
            if current_year == "1959-60":
                result = value == "1959" or value == "1960"
            else:
                result = value == current_year and len(current_year) == 4

    elif datafield == "269__":
        if subfield == "a":
            result = ( current_language.lower() == "e" and value == "Geneva" ) or ( current_language.lower() == "f" and value == "Genève" )
        elif subfield == "b":
            result = value == "CERN"
        elif subfield == "c":
            # TODO: Should we check the date format here? What is the correct format?
            result = len(value) > 0

    elif datafield == "520__":
        if subfield == "b":
            if CFG_NO_EMPTY_FIELDS:
                # This field can't be empty
                result = len(value) > 0

    elif datafield == "590__":
        if subfield == "b":
            if CFG_NO_EMPTY_FIELDS:
                # This field can't be empty
                result = len(value) > 0

    elif datafield == "690__":
        if subfield == "a":
            result = value == "CERN"

    elif datafield == "773__":
        if subfield == "c":
            page_match = PATTERN_PAGINATION.match(value)
            result = page_match is not None
            # In case there is a page range match (example: "25-26"), make sure that the
            # starting page is lower than the ending page. Don't check for Roman numbers.
            if result:
                page_start, page_end = page_match.groups()
                if ( page_start is not None and page_end is not None ) and \
                   ( page_start.isdigit() and page_end.isdigit() ) and \
                   ( int(page_start) >= int(page_end) ):
                    result = False
        elif subfield == "n":
            # Issue numbers should not have leading "0"
            result = value == current_issue.lstrip("0")
        elif subfield == "p":
            result = ( is_courier  and ( ( current_language.lower() == "e" and value == "CERN Courier"  ) or \
                                         ( current_language.lower() == "f" and value == "Courrier CERN" ) ) ) or \
                     ( is_bulletin and value == "CERN Bulletin" )
        elif subfield == "t":
            result = ( is_courier  and ( ( current_language.lower() == "e" and value == "CERN Courier"  ) or \
                                         ( current_language.lower() == "f" and value == "Courrier CERN" ) ) ) or \
                     ( is_bulletin and value == "CERN Bulletin" )
        elif subfield == "v":
            result = value == current_volume
        elif subfield == "y":
            if current_year == "1959-60":
                result = value == "1959" or value == "1960"
            else:
                result = value == current_year and len(current_year) == 4

    elif datafield == "980__":
        if subfield == "a":
            result = ( is_courier  and value == "COURIERARCHIVE"  ) or \
                     ( is_bulletin and value == "BULLETINARCHIVE" )

    elif datafield == "FFT__":
        if subfield == "a":
            result = os.path.isfile(os.path.sep.join((directory, value)))
        elif subfield == "t":
            result = value == "Figures"
        elif subfield == "d":
            if CFG_NO_EMPTY_FIELDS:
                # This field can't be empty
                result = len(value) > 0

    # NOTE: Accept FTT for now to avoid the huge amount of errors
    elif datafield == "FTT__":
        if subfield == "a":
            result = os.path.isfile(os.path.sep.join((directory, value)))
        elif subfield == "t":
            result = value == "Figures"
        elif subfield == "d":
            if CFG_NO_EMPTY_FIELDS:
                # This field can't be empty
                result = len(value) > 0

    else:
        (result, error) = (True, "")

    if not result:
        error = "Incorrect value (%s) in %s%s" % (value, datafield, subfield)

    return (result, error)


def _report(message, exit=False, warn=False, info=False):
    """
    """
    if message in CORNER_CASE_WARNINGS_TO_IGNORE:
        return
    if exit:
        sys.exit("%s: %s" % ("ERROR", message))
    elif warn:
        print "%s: %s" % ("WARNING", message)
    elif info:
        print "%s: %s" % ("INFORMATION", message)
    else:
        print message

def test_assertion(assertion, message):
    """
    We are using this function to report all errors (it replaced the assert
    statement, which was catching just the first error in try/except clause)
    """
    if not assertion:
        _report(message, warn = True)

def run():
    """
    """

    parser = OptionParser()

#    parser.add_option("-d",
#                      "--directory",
#                      dest="directory",
#                      type="str",
#                      action="store",
#                      default=".",
#                      help="The base directory to check")

    parser.add_option("-c",
                      "--courier",
                      dest="is_courier",
                      action="store_true",
                      default=False,
                      help="Specify that we are checking the CERN Courier")

    parser.add_option("-b",
                      "--bulletin",
                      dest="is_bulletin",
                      action="store_true",
                      default=False,
                      help="Specify that we are checking the CERN Bulletin")

    (options, args) = parser.parse_args()

    # Try and get the target directory from the first positional argument
    # passed to the script. If no arguments were passed, then get the current
    # working directory.

    try:
        directory = args[0].rstrip("/")
    except IndexError:
        directory = os.getcwd()

    if os.path.exists(directory):
        if not os.path.isdir(directory):
            _report("Error: The given directory is not valid.", exit = True)
    else:
        _report("Error: The given directory does not exist.", exit = True)

    if options.is_courier and options.is_bulletin:
        _report("Error: You can't specify both the CERN Courier and the CERN Bulletin options.", exit = True)
    elif options.is_courier or options.is_bulletin:
        is_courier, is_bulletin = options.is_courier, options.is_bulletin
    else:
        # The user has not specified whether we are checking the CERN Courier or the CERN Bulleting.
        # Let's try and detect it ourselves.
        current_dir = directory.split(os.path.sep)[-1]
        if current_dir == CFG_CCCBD_PUBLICATIONS_CERN_BULLETIN:
            is_courier, is_bulletin = False, True
        elif current_dir == CFG_CCCBD_PUBLICATIONS_CERN_COURRIER:
            is_courier, is_bulletin = True, False
        else:
            _report("Autodection failed. You may need specify either the CERN Courier or the CERN Bulletin option.", exit = True)

    directory_walk = os.walk(directory)

    try:

        if is_courier:

            first_iteration_p = True

            current_language, current_volume, current_issue, current_year = (None, ) * 4

            pattern_volume_issue_dir = re.compile('vol(\d+)-issue(\d+|\d+-\d+)$')

            pattern_tiff_file_page   = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-(?:p\d+[a-z]?|[IVX]{1,4})-(\w)\.tiff$')
            #pattern_tiff_file_covers = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-covers\.tiff$')
            # NOTE: accept both "cover" and "covers"
            pattern_tiff_file_covers = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-covers?\.tiff$')
            pattern_tiff_file_toc    = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-toc\.tiff$')

            pattern_pdf_file_page   = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+[a-z]?-(\w)\.pdf$')
            pattern_pdf_file_issue  = re.compile('vol(\d+)-issue(\d+|\d+-\d+)\.pdf$')
            # NOTE: accept both "cover" and "covers"
            #pattern_pdf_file_covers = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-covers\.pdf$')
            pattern_pdf_file_covers = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-covers?\.pdf$')
            pattern_pdf_file_toc    = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-toc\.pdf$')

            pattern_ocr_file_page = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+[a-z]?-(\w)\.ocr$')

            pattern_xml_file_page = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+[a-z]?-(\w)\.xml$')

            # Strict
            #pattern_png_file_fig        = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+fig[a-z]?\.png$')
            #pattern_png_file_figcaption = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+fig[a-z]?caption\.txt$')
            #pattern_png_file_captions   = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+captions\.xml$')
            # NOTE: note so strict, extra letters are allowed either before or after the fig/captions
            # NOTE: allow for the -<language> after the figure name
            #pattern_png_file_fig        = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+[a-z]?fig[a-z]?\.png$')
            pattern_png_file_fig        = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+[a-z]?fig[a-z]?(?:-\w)?\.png$')
            pattern_png_file_figcaption = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+[a-z]?fig[a-z]?caption\.txt$')
            pattern_png_file_captions   = re.compile('vol(\d+)-issue(\d+|\d+-\d+)-p\d+[a-z]?captions\.xml$')

            while True:

                dirpath, dirnames, filenames = directory_walk.next()

                current_dir = dirpath.split(os.path.sep)[-1]

                # For the first iteration over the directory make sure we are in the CERN Courier or exit
                if first_iteration_p:
                    if current_dir in CFG_CCCBD_PUBLICATIONS:
                        for dirname in dirnames:
                            if dirname in CFG_CCCBD_LANGUAGES:
                                continue
                            _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                        first_iteration_p = False
                    elif current_dir == ".":
                        for dirname in dirnames:
                            if dirname not in CFG_CCCBD_LANGUAGES:
                                _report("This does not seem to be a valid starting directory : %s" % (dirpath,), exit = True)
                        first_iteration_p = False
                    else:
                        _report("This is not a valid starting directory : %s" % (dirpath,), exit = True)

                if current_dir in CFG_CCCBD_LANGUAGES:
                    for dirname in dirnames:
                        if dirname.isdigit() or dirname == "1959-60":
                            # Hackish solution for this one specific directory
                            continue
                        _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                    current_language = current_dir

                elif current_dir.isdigit() or current_dir == "1959-60":
                    for dirname in dirnames:
                        if pattern_volume_issue_dir.match(dirname) is not None:
                            continue
                        _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                    current_volume, current_issue = (None, ) * 2
                    current_year = current_dir

                elif pattern_volume_issue_dir.match(current_dir) is not None:
                    for dirname in dirnames:
                        if dirname in CFG_CCCBD_FORMATS:
                            continue
                        _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)

                    current_month = None
                    current_volume, current_issue = pattern_volume_issue_dir.match(current_dir).groups()

                elif current_dir == CFG_CCCBD_FORMATS_TIFF:
                    pass

                elif current_dir == CFG_CCCBD_FORMATS_PDF:
                    pass

                elif current_dir == CFG_CCCBD_FORMATS_OCR:
                    pass

                elif current_dir == CFG_CCCBD_FORMATS_XML:
                    current_month_candidates = []
                    for filename in filenames:
                        xml_file_page_match = pattern_xml_file_page.match(filename)
                        if xml_file_page_match is not None:
                            tmp_file = os.path.sep.join((dirpath, filename))
                            try:
                                xml = etree.parse(tmp_file)
                                current_month_candidates_elements = xml.xpath("datafield[@tag='269']/subfield[@code='c']")
                                if len(current_month_candidates_elements) != 1:
                                    _report("Not exactly one 269__c defined for %s" % (os.path.sep.join((dirpath, filename)),), exit = True)
                                # Dates in 269__c should look something like 'October 1959'
                                current_month_candidates_months_and_years = [e.text for e in current_month_candidates_elements]
                                current_month_candidates_months = []
                                # Let's extract the months
                                for month in current_month_candidates_months_and_years:
                                    # Strip digits from month
                                    month = "".join([b for b in month if not b.isdigit()]).strip()
                                    if len(month.split()) > 1:
                                        current_month_candidates_months.append('-'.join(month.split()[:-1]))
                                    else:
                                        current_month_candidates_months.append(month)
                                # current_month_candidates_months = ['/'.join(d.split()[:-1]) for d in current_month_candidates_months_and_years]
                                current_month_candidates.extend(current_month_candidates_months)
                            except etree.XMLSyntaxError:
                                pass
                        else:
                            pass
                    if current_month_candidates:
                        print current_month_candidates

                        current_month_candidates_unique = list(set(current_month_candidates))
                        current_month_candidates_unique_lowest_score = sorted(zip([current_month_candidates.count(u) for u in current_month_candidates_unique], current_month_candidates_unique), key = lambda x:x[0])[0][1]
                        if len(current_month_candidates_unique) > 1:
                            print "===> CHECK ME: More than one unique value in the current month candidates (%s)" % (current_month_candidates_unique_lowest_score.encode("UTF-8"),)

                        current_month_candidates_score = map(sum, zip(*[[Levenshtein.distance(proper_month.decode("UTF-8").lower(), unicode(current_month_candidate).lower()) for proper_month in ((current_language == CFG_CCCBD_LANGUAGES_ENG and CFG_CCCBD_MONTHS_ENG) or (current_language == CFG_CCCBD_LANGUAGES_FRE and CFG_CCCBD_MONTHS_FRE) or [])] for current_month_candidate in current_month_candidates]))
                        if current_month_candidates_score:
                            current_month_candidates_score_min = min(current_month_candidates_score)
                            current_month_candidates_score_min_avg = float(current_month_candidates_score_min) / float(len(current_month_candidates))
                            if current_month_candidates_score_min_avg > 2:
                                print "===> CHECK ME: Too high average minimum score for the best candidate (%s)" % (str(current_month_candidates_score_min_avg),)
                            current_month = ((current_language == CFG_CCCBD_LANGUAGES_ENG and CFG_CCCBD_MONTHS_ENG) or (current_language == CFG_CCCBD_LANGUAGES_FRE and CFG_CCCBD_MONTHS_FRE) or [])[current_month_candidates_score.index(current_month_candidates_score_min)]
                    current_date = current_month + " " + current_year
                    print "Now I will replace old date in file %s with %s" % (filename, current_date)
                    # Replace month with correct value in every file
                    for filename in filenames:
                        xml_file_page_match = pattern_xml_file_page.match(filename)
                        if xml_file_page_match is not None:
                            tmp_file = os.path.sep.join((dirpath, filename))
                            # One special case without month and year (special issue: /dfs/cern.ch/COURRIER_CERN/F/1960/vol1-issue6-7/PDF)
                            if current_language == "F" and current_volume == "1" and current_issue == "6-7":
                                print "Special case. Not changing anything."
                                continue
                            try:
                                xml = etree.parse(tmp_file)
                                current_month_candidates_elements = xml.xpath("datafield[@tag='269']/subfield[@code='c']")
                                if len(current_month_candidates_elements) != 1:
                                    _report("Not exactly one 269__c defined for %s" % (os.path.sep.join((dirpath, filename)),), exit = True)
                                current_month_to_fix = [e.text for e in current_month_candidates_elements][0]
                                # There are encoding issues with French letters so we need to encode the month properly
                                # Otherwise we get UnicodeEncodeError: 'ascii' codec can't encode character...
                                current_month_to_fix = current_month_to_fix.encode('utf8')
                                with open(tmp_file) as f:
                                    newfile = f.read().replace(current_month_to_fix, current_date)
                                open(tmp_file, "w").write(newfile)
                                print "Replaced %s with %s in %s" % (current_month_to_fix, current_date, tmp_file)
                            except etree.XMLSyntaxError:
                                pass
                    print "l:", current_language, "/v:", current_volume, "/i:", current_issue, "/y:", current_year, "/m:", current_month
                    print

                elif current_dir == CFG_CCCBD_FORMATS_PNG:
                    pass

        if is_bulletin:
            # Don't do anything fo the CERN Bulletin yet.
            raise StopIteration

            first_iteration_p = True

            current_language, current_volume, current_issue, current_year = (None, ) * 4

            pattern_volume_issue_dir = re.compile('(\d{2}(?:-\d{2})?(?:bis)?)-(\d{4})$') # 03-1996 or 51-52-1996

            pattern_tiff_file_page   = re.compile('(\d{2}(?:-\d{2})?(?:bis)?)-(\d{4})-(?:p\d+[a-z]?|[IVX]{1,4})\.tiff$')

            pattern_pdf_file_page   = re.compile('(\d{2}(?:-\d{2})?(?:bis)?)-(\d{4})-(?:p\d+[a-z]?|[IVX]{1,4})\.pdf$')
            pattern_pdf_file_issue  = re.compile('(\d{2}(?:-\d{2})?(?:bis)?)-(\d{4})\.pdf$')

            pattern_ocr_file_page = re.compile('(\d{2}(?:-\d{2})?(?:bis)?)-(\d{4})-(?:p\d+[a-z]?|[IVX]{1,4})\.ocr$')

            pattern_xml_file_page = re.compile('(\d{2}(?:-\d{2})?(?:bis)?)-(\d{4})-(?:p\d+[a-z]?|[IVX]{1,4})\.xml$')

            while True:

                dirpath, dirnames, filenames = directory_walk.next()

                current_dir = dirpath.split(os.path.sep)[-1]

                # For the first iteration over the directory make sure we are in the CERN Bulletin or exit
                if first_iteration_p:
                    if current_dir in CFG_CCCBD_PUBLICATIONS:
                        for dirname in dirnames:
                            if dirname.isdigit():
                                continue
                            _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                        first_iteration_p = False
                    elif current_dir == ".":
                        for dirname in dirnames:
                            if not dirname.isdigit():
                                _report("This does not seem to be a valid starting directory : %s" % (dirpath,), exit = True)
                        first_iteration_p = False
                    else:
                        _report("This is not a valid starting directory : %s" % (dirpath,), exit = True)

                if current_dir.isdigit():
                    for dirname in dirnames:
                        if pattern_volume_issue_dir.match(dirname) is not None:
                            continue
                        _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                    current_volume, current_issue = (None, ) * 2
                    current_year = current_dir

                elif pattern_volume_issue_dir.match(current_dir) is not None:
                    for dirname in dirnames:
                        if dirname in CFG_CCCBD_FORMATS:
                            continue
                        _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                        # TODO: Check if we can correct the problem
                        # If we fix the problem here, we might introduce another problem in the FFT tags of the XML files!
                        # Either make sure to fix the problem in both places or loosen the checks.
                        #if dirname.upper() in CFG_CCCBD_FORMATS:
                        #    tmp_name_before = os.path.sep.join((dirpath, dirname))
                        #    tmp_name_after  = os.path.sep.join((dirpath, dirname.upper()))
                        #    os.rename(tmp_name_before, tmp_name_after)
                        #    _report("Renamed %s to %s " % (tmp_name_before, tmp_name_after), info = True)

                    current_issue, current_volume = pattern_volume_issue_dir.match(current_dir).groups()

                elif current_dir == CFG_CCCBD_FORMATS_TIFF:
                    _execute_on_each_directory(current_dir, dirpath)
                    if dirnames:
                        for dirname in dirnames:
                            _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                    for filename in filenames:
                        _execute_on_each_file(filename, current_dir, dirpath)
                        tiff_file_page_match = pattern_tiff_file_page.match(filename)
                        if tiff_file_page_match is not None:
                            try:
                                assert (current_issue, current_volume) == tiff_file_page_match.groups()
                            except AssertionError:
                                _report("There is an unexpected file in %s : %s" % (dirpath, filename), warn = True)
                        else:
                            _report("There is an unexpected file in %s : %s" % (dirpath, filename), warn = True)

                elif current_dir == CFG_CCCBD_FORMATS_PDF:
                    _execute_on_each_directory(current_dir, dirpath)
                    if dirnames:
                        for dirname in dirnames:
                            _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                    pdf_issue_p = False
                    for filename in filenames:
                        _execute_on_each_file(filename, current_dir, dirpath)
                        pdf_file_page_match = pattern_pdf_file_page.match(filename)
                        if pdf_file_page_match is not None:
                            try:
                                assert (current_issue, current_volume) == pdf_file_page_match.groups()
                            except AssertionError:
                                _report("There is an unexpected file in %s : %s" % (dirpath, filename), warn = True)
                        else:
                            pdf_file_issue_match = pattern_pdf_file_issue.match(filename)
                            if pdf_file_issue_match is not None:
                                try:
                                    assert (current_issue, current_volume) == pdf_file_issue_match.groups()
                                    pdf_issue_p = True
                                except AssertionError:
                                    _report("There is an unexpected file in %s : %s" % (dirpath, filename), warn = True)
                            else:
                                _report("There is an unexpected file in %s : %s" % (dirpath, filename), warn = True)
                    if not pdf_issue_p:
                        _report("The PDF issue file is missing in %s" % (dirpath,), warn = True)

                elif current_dir == CFG_CCCBD_FORMATS_OCR:
                    _execute_on_each_directory(current_dir, dirpath)
                    if dirnames:
                        for dirname in dirnames:
                            _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                    for filename in filenames:
                        _execute_on_each_file(filename, current_dir, dirpath)
                        ocr_file_page_match = pattern_ocr_file_page.match(filename)
                        if ocr_file_page_match is not None:
                            try:
                                assert (current_issue, current_volume) == ocr_file_page_match.groups()
                            except AssertionError:
                                _report("There is an unexpected file in %s : %s" % (dirpath, filename), warn = True)
                        else:
                            _report("There is an unexpected file in %s : %s" % (dirpath, filename), warn = True)

                elif current_dir == CFG_CCCBD_FORMATS_XML:
                    _execute_on_each_directory(current_dir, dirpath)
                    if dirnames:
                        for dirname in dirnames:
                            _report("There is an unexpected directory in %s : %s" % (dirpath, dirname), warn = True)
                    for filename in filenames:
                        _execute_on_each_file(filename, current_dir, dirpath)
                        xml_file_page_match = pattern_xml_file_page.match(filename)
                        if xml_file_page_match is not None:
                            try:
                                assert (current_issue, current_volume) == xml_file_page_match.groups()

                                tmp_file = os.path.sep.join((dirpath, filename))
                                try:
                                    xml = etree.parse(tmp_file)
                                    # keep all the marc tags (datafields & subfields) found in this file in this dictionary for later checks
                                    tmp_file_marc_tags = {}

                                    # Check if the file encoding is correct
                                    test_assertion(xml.docinfo.encoding == "UTF-8" , "[XML] Wrong encoding (%s) in %s" % (xml.docinfo.encoding, os.path.sep.join((dirpath, filename))))

                                    # Check if the root element:
                                    xml_root = xml.getroot()
                                    # is correct
                                    test_assertion(xml_root.tag == "record" , "[XML] Wrong root element (%s) in %s" % (xml_root.tag, os.path.sep.join((dirpath, filename))))
                                    # has no overflowing text anywhere
                                    test_assertion(xml_root.text.strip() == "" , "[XML] Extra text (%s) in the root element in %s" % (xml_root.text.strip(), os.path.sep.join((dirpath, filename))))
                                    # has no attributes
                                    test_assertion(xml_root.attrib == {} , "[XML] Extra attributes (%s) in the root element in %s" % (str(xml_root.attrib), os.path.sep.join((dirpath, filename))))

                                    # Go through all the root's children and check:
                                    xml_datafields = xml_root.iterchildren()
                                    for xml_datafield in xml_datafields:
                                        # if they are all datafields
                                        test_assertion(xml_datafield.tag == "datafield" , "[XML] Wrong datafield element (%s) in %s" % (xml_datafield.tag, os.path.sep.join((dirpath, filename))))
                                        # if they have any overflowing text anywhere
                                        if xml_datafield.text:
                                            test_assertion(xml_datafield.text.strip() == "" , "[XML] Extra text (%s) in a datafield element in %s" % (xml_datafield.text.strip(), os.path.sep.join((dirpath, filename))))
                                        if xml_datafield.tail:
                                            test_assertion(xml_datafield.tail.strip() == "" , "[XML] Extra text (%s) in a datafield element in %s" % (xml_datafield.tail.strip(), os.path.sep.join((dirpath, filename))))
                                        # if they have the expected attributes
                                        assert ( sorted(xml_datafield.keys()) == ['ind1', 'ind2', 'tag'] ), "[XML] Extra attributes (%s) in a datafield element in %s" % (str(xml_datafield.attrib), os.path.sep.join((dirpath, filename)))
                                        # if they are valid datafields
                                        tmp_file_datafield = ''.join([xml_datafield.attrib[key] for key in ('tag', 'ind1', 'ind2')]).replace(' ', '_')
                                        test_assertion(tmp_file_datafield in CFG_CCCBD_MARC_FIELDS_ALLOWED , "[XML] Unexpected datafield element tag (%s) in %s" % (tmp_file_datafield, os.path.sep.join((dirpath, filename))))

                                        # this is now a valid datafield, so add it to the dictionary of marc tags found in this file
                                        tmp_file_marc_tags[tmp_file_datafield] = []

                                        # Go through all of each datafield's children and check:
                                        xml_subfields = xml_datafield.iterchildren()
                                        tmp_file_datafield_allowed_subfields = CFG_CCCBD_MARC_FIELDS_ALLOWED.get(tmp_file_datafield, "")
                                        for xml_subfield in xml_subfields:
                                            # if they are all subfields
                                            test_assertion(xml_subfield.tag == "subfield" , "[XML] Wrong subfield element (%s) in %s" % (xml_subfield.tag, os.path.sep.join((dirpath, filename))))
                                            # if they have any overflowing text anywhere
                                            test_assertion(xml_subfield.tail.strip() == "" , "[XML] Extra text (%s) in a subfield element in %s" % (xml_subfield.tail.strip(), os.path.sep.join((dirpath, filename))))
                                            # if they have the expected attributes
                                            test_assertion(xml_subfield.keys() == ['code'] , "[XML] Extra attributes (%s) in a subfield element in %s" % (str(xml_subfield.attrib), os.path.sep.join((dirpath, filename))))
                                            # if they are valid subfields
                                            tmp_file_subfield = xml_subfield.attrib['code']
                                            test_assertion(tmp_file_subfield in tmp_file_datafield_allowed_subfields , "[XML] Unexpected subfield element code (%s) in datafield %s in %s" % (str(tmp_file_subfield), tmp_file_datafield, os.path.sep.join((dirpath, filename))))
                                            # if their content is valid
                                            (result, error) = _check_marc_content(tmp_file_datafield, tmp_file_subfield, xml_subfield.text,
                                                                                  current_language, current_volume, current_issue,
                                                                                  current_year, directory, is_courier, is_bulletin)
                                            test_assertion(result is True , "[XML] %s in %s" % (error, os.path.sep.join((dirpath, filename))))

                                            # this is now a valid subfield, so add it to the dictionary of marc tags found in this file
                                            tmp_file_marc_tags[tmp_file_datafield].append(tmp_file_subfield)

                                        # if the datafield has children (subfields)
                                        test_assertion(len(tmp_file_marc_tags[tmp_file_datafield]) > 0 , "[XML] No subfields defined for datafield element tag (%s) in %s" % (tmp_file_datafield, os.path.sep.join((dirpath, filename))))

                                    # Check that all the marc tags (datafields & subfields) found in this file respect the CFG_CCCBD_MARC_FIELDS_MINIMUM
                                    for datafield in CFG_CCCBD_MARC_FIELDS_MINIMUM:
                                        subfields = tmp_file_marc_tags.pop(datafield, None)
                                        test_assertion(subfields is not None , "[XML] Mandatory datafield (%s) missing in %s" % (datafield, os.path.sep.join((dirpath, filename))))
                                        for subfield in CFG_CCCBD_MARC_FIELDS_MINIMUM[datafield]:
                                            test_assertion(subfield in subfields , "[XML] Mandatory subfield (%s) for datafield (%s) missing in %s" % (subfield, datafield, os.path.sep.join((dirpath, filename))))

                                except etree.XMLSyntaxError:
                                    _report("[XML] Invalid syntax in %s" % (os.path.sep.join((dirpath, filename)),), warn = True)

                            except AssertionError:
                                _report("There is an unexpected file in %s : %s" % (dirpath, filename), warn = True)
                        else:
                            _report("There is an unexpected file in %s : %s" % (dirpath, filename), warn = True)

    except StopIteration:
        #_report("We are all done!")
        pass

if __name__ == "__main__":
    run()
