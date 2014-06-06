Workflow to upload files:
1. Generate issue files
2. Concatenate all files into one big XML:
    echo "<collection>" >> ../year1960.xml ; find ./ -regex ".*\(-e\|[0-9]\)\.xml" | xargs cat >> ../year1960.xml ; echo "</collection>" >> ../year1960.xml
3. Replace the original paths to files (E/19xx/ or ./E/19xx) with something that bibupload can access, e.g.
    sed "s/E\/19/\/afs\/cern.ch\/project\/cds\/other\/CCCBD\/COURIER\/E\/19/" year1960.xml
4. Add the path to CFG_BIBUPLOAD_FFT_ALLOWED_LOCAL_PATHS (in config.py)
5. Run bibupload -i
6. Create collections isung Websearch interface
7. Assign newly created collection to parent collections
8. Run webcoll on collections and on parent collection
9. Run bibindex on files, e.g. bibindex -i 1690374-1690448