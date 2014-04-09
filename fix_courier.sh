#!/bin/bash
# Script for fixing CERN Courier files, run in top courier directory

# Find all files inside current directory
for f in $(find ./ -type f)
do
    # Get the directory name
    d=$(basename $(dirname $f))
    # Get the language
    if echo $f | grep -q "/E/"; then
        lang="e"
    else
        if echo $f | grep -q "/F/"; then
            lang="f"
        else
            echo "Error, can't figure out the language in file "$f", exiting."
            exit
        fi
    fi
    # Rename .tif to .tiff
    if echo $f | grep -Po 'tif$'; then
        new_filename=$(echo $f | grep -Po '.*(?=.tif)').tiff
        mv $f $new_filename
        f=$new_filename
    fi
    # Get basename of a file (so only vol32-issue10-V-f.tiff from COURRIER_CERN/F/1992/vol32-issue10/TIFF/vol32-issue10-V-f.tiff)
    b=$(basename $f)
    # Fix missing "e" or "f" in tiff filenames
    if echo $b | grep -Po '[IV].tiff$'; then
        new_filename=$(echo $f | grep -Po '.*[IVX]*(?=\.tiff$)')"-"$lang".tiff"
        mv $f $new_filename
        f=$new_filename
    fi
    # Rename ...captions.txt to captions.txt
    if [ "$d" == "PNG" ]; then
        rename 's/captions\.txt/caption\.txt/' $f
    fi
    # Rename ...figcaptions.xml to captions.xml
    if [ "$d" == "PNG" ]; then
        rename 's/figcaptions\.xml$/captions\.xml/' $f
    fi

    # if it's XML:
    if [ "$d" == "XML" ]; then
    # Remove lines with empty subfields
        sed -i "/<subfield code=\".\"><\/subfield>/d" $f
    # Also a different pattern for empty lines
        sed -i 'N;/<subfield code=\".\">\n    <\/subfield>/d;P;D;' $f
    # And another one
        sed -i "/    <subfield code=\".\" \/>/d" $f
    # Remove empty fields that we might have just created
    # I have no idea what kind of magic is happening here with this ;P;D but it took me 2 hours to make this pattern and it's working
        sed -i "N;/<datafield tag=\".\{3\}\" ind2=\" \" ind1=\" \">\n <\/datafield>/d;P;D;" $f
    # Again, different pattern for empty fields
        sed -i "N;/<datafield tag=\".\{3\}\" ind2=\" \" ind1=\" \">\n  <\/datafield>/d;P;D;" $f
    # Replace 41__ with 041__:
        sed -i "s/<datafield tag=\"41\" ind2=\" \" ind1=\" \">/<datafield tag=\"041\" ind2=\" \" ind1=\" \">/" $f
    # Fix predefined fields:
        # 041__a Language
        if [ "$lang" == "e" ]; then
            sed -i "N;s/<datafield tag=\"041\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"041\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">en<\/subfield>/;P;D;" $f
        else
            sed -i "N;s/<datafield tag=\"041\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"041\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">fr<\/subfield>/;P;D;" $f
        fi
        # 269__a and 269__b Publication place and publisher name
        if [ "$lang" == "e" ]; then
            sed -i "N;s/<datafield tag=\"269\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"269\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">Geneva<\/subfield>/;P;D;" $f
        else
            sed -i "N;s/<datafield tag=\"269\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"269\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">Genève<\/subfield>/;P;D;" $f
        fi
        # 690__a Subject indicator
            sed -i "N;s/<datafield tag=\"690\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"690\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">CERN<\/subfield>/;P;D;" $f
        # 773__p Title
        if [ "$lang" == "e" ]; then
            sed -i "s/<subfield code=\"p\">.*<\/subfield>/<subfield code=\"p\">CERN Courier<\/subfield>/" $f
        else
            sed -i "s/<subfield code=\"p\">.*<\/subfield>/<subfield code=\"p\">Courrier CERN<\/subfield>/" $f
        fi
        # 980__a Primary collection indicator
            sed -i "N;s/<datafield tag=\"980\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">.*<\/subfield>/<datafield tag=\"980\" ind2=\" \" ind1=\" \">\n<subfield code=\"a\">COURIERARCHIVE<\/subfield>/;P;D;" $f

        # Issue number
        issue=$(echo $f | grep -Po "(?<=issue)[0-9]*(?=\/)")
        sed -i "s/<subfield code=\"n\">.*<\/subfield>/<subfield code=\"n\">$issue<\/subfield>/" $f
        # Volume number
        volume=$(echo $f | grep -Po "(?<=vol)[0-9]*(?=-issue[0-9]*/)")
        sed -i "s/<subfield code=\"v\">.*<\/subfield>/<subfield code=\"v\">$volume<\/subfield>/" $f
    fi
done
echo "Done!"