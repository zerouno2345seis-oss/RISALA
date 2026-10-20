import zipfile,re,sys
src,dst=sys.argv[1:3]
zi=zipfile.ZipFile(src);zo=zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED)
sup=lambda c:'<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/><w:rtl/></w:rPr><w:t>%s</w:t></w:r>'%c
for it in zi.infolist():
    d=zi.read(it.filename)
    for fn,tag in (('word/document.xml','footnoteReference w:id="\\d+"'),('word/footnotes.xml','footnoteRef')):
        if it.filename==fn:
            pat=r'(<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:%s/></w:r>)'%tag
            d=re.sub(pat,lambda m:sup('(')+m.group(1)+sup(')'),d.decode('utf8')).encode('utf8')
    zo.writestr(it,d)
zo.close()
