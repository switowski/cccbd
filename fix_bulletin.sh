#!/bin/bash
# Script for fixing CERN Bulletin files, run in top Bulletin directory

# Find all files inside current directory
for f in $(find ./ -type f)
do
    # Get the directory name
    d=$(basename $(dirname $f))

    # if it's XML:
    if [ "$d" == "XML" ]; then
    # Replace 41__ with 041__:
        sed -i "s/<datafield tag=\"41\" ind2=\" \" ind1=\" \">/<datafield tag=\"041\" ind2=\" \" ind1=\" \">/" $f
    # Fix predefined fields:
        # 041__a Language
        sed -i "s/<subfield code=\"a\">en<\/subfield>/<subfield code=\"a\">eng<\/subfield>/" $f
        sed -i "s/<subfield code=\"a\">fr<\/subfield>/<subfield code=\"a\">fre<\/subfield>/" $f

        # 260__c Year
        year=$(echo $f | grep -Po "(?<=/)[0-9]*(?=/)")
        sed -i "N;s/<datafield tag=\"260\" ind2=\" \" ind1=\" \">\n<subfield code=\"c\">.*<\/subfield>/<datafield tag=\"260\" ind2=\" \" ind1=\" \">\n<subfield code=\"c\">$year<\/subfield>/;P;D;" $f

        # 690__a Subject indicator
            sed -i "N;s/<datafield tag=\"690\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"690\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">CERN<\/subfield>/;P;D;" $f

        # 773__n Issue number
        issue=$(echo $f | grep -Po "(?<=/)([0-9]*)(?=-[0-9]{4}\/)")
        # If first character is 0, remove it
        if [[ ${issue:0:1} == "0" ]]; then
            issue=${issue:1}
        fi
        # Remove the second trailing zero from numbers like 01-02
        if [[ ${issue:2:1} == "0" ]]; then
            issue=${issue:0:2}${issue:3}
        fi
        sed -i "s/<subfield code=\"n\">.*<\/subfield>/<subfield code=\"n\">$issue<\/subfield>/" $f

        # 773_t Talk given at, replace "CERN Bullettin" with "CERN Bulletin"
        sed -i "s/<subfield code=\"t\">CERN Bullettin<\/subfield>/<subfield code=\"t\">CERN Bulletin<\/subfield>/" $f

        # 980__a Primary collection indicator
        sed -i "N;s/<datafield tag=\"980\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"980\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">BULLETINARCHIVE<\/subfield>/;P;D;" $f

        # 980__a Primary collection indicator, replace "BULLETTINARCHIVE" with "BULLETINARCHIVE"
        sed -i "s/<subfield code=\"a\">BULLETTINARCHIVE<\/subfield>/<subfield code=\"a\">BULLETINARCHIVE<\/subfield>/" $f

    # We remove empty fields AFTER all replacements. Otherwise we might remove important fields that are empty (like volume) and we won't be able to fill them with correct values
    # Remove lines with empty subfields
        sed -i "/<subfield code=\".\"><\/subfield>/d" $f
    # Also a different pattern for empty lines
        sed -i 'N;/<subfield code=\".\">\n    <\/subfield>/d;P;D;' $f
    # And another one
        sed -i "/    <subfield code=\".\" \/>/d" $f

    # Remove empty fields that we might have just created
    # I have no idea what kind of magic is happening here with this ;P;D but it took me 2 hours to make this pattern and it's working
        sed -i "N;/<datafield tag=\".\{3\}\" ind2=\".\" ind1=\".\">\n<\/datafield>/d;P;D;" $f
    # Again, different pattern for empty fields
        sed -i "N;/<datafield tag=\".\{3\}\" ind2=\".\" ind1=\".\">\n <\/datafield>/d;P;D;" $f
    # And one more different pattern for empty fields
        sed -i "N;/<datafield tag=\".\{3\}\" ind2=\".\" ind1=\".\">\n  <\/datafield>/d;P;D;" $f
    fi
done
echo "Done!"