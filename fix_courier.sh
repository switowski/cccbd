#!/bin/bash
# Script for fixing CERN Courier files, run in top courier directory

# Find all files inside current directory
for f in $(find ./ -type f)
do
    # Get the directory name
    d=$(basename $(dirname $f))
    # Get the language
    if echo $f | grep -q "/E/"; then
        lang="E"
    else
        if echo $f | grep -q "/F/"; then
            lang="F"
        else
            echo "Error, can't figure out the language, exiting."
            exit
        fi
    fi
    # if it's XML:
    if [ "$d" == "XML" ]; then
    # Remove lines with empty subfields
        sed -i "/<subfield code=\".\"><\/subfield>/d" $f
    # Remove empty fields that we might have just created
    # I have no idea what kind of magic is happening here but it took me 2 hours to make this pattern and it's working
        sed -i "N;/<datafield tag=\".\{3\}\" ind2=\" \" ind1=\" \">\n <\/datafield>/d;P;D;" $f
    # Fix predefined fields:
        # 041__a Language
        if [ "$lang" == "E" ]; then
            sed -i "N;s/<datafield tag=\"041\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"041\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">en<\/subfield>/;P;D;" $f
        else
            sed -i "N;s/<datafield tag=\"041\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"041\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">fr<\/subfield>/;P;D;" $f
        fi
        # 269__a and 269__b Publication place and publisher name
        if [ "$lang" == "E" ]; then
            sed -i "N;s/<datafield tag=\"269\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"269\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">Geneva<\/subfield>/;P;D;" $f
        else
            sed -i "N;s/<datafield tag=\"269\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"269\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">Genève<\/subfield>/;P;D;" $f
        fi
        # 690__a Subject indicator
            sed -i "N;s/<datafield tag=\"690\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"690\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">CERN<\/subfield>/;P;D;" $f
        # 773__p Title
        if [ "$lang" == "E" ]; then
            sed -i "s/<subfield code=\"p\">.*<\/subfield>/<subfield code=\"p\">CERN Courier<\/subfield>/" $f
        else
            sed -i "s/<subfield code=\"p\">.*<\/subfield>/<subfield code=\"p\">Courrier CERN<\/subfield>/" $f
        fi
        # 980__a Primary collection indicator
            sed -i "N;s/<datafield tag=\"980\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"980\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">COURIERARCHIVE<\/subfield>/;P;D;" $f
    # More complicated fixes
        # Issue number
        issue=$(echo $f | grep -Po "(?<=issue)[0-9]*(?=\/)")
        sed -i "s/<subfield code=\"n\">.*<\/subfield>/<subfield code=\"n\">$issue<\/subfield>/" $f
        # Volume number
        volume=$(echo $f | grep -Po "(?<=vol)[0-9]*(?=-issue[0-9]*/)")
        sed -i "s/<subfield code=\"v\">.*<\/subfield>/<subfield code=\"v\">$volume<\/subfield>/" $f
    fi


done