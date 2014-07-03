#!/bin/bash
#proto-index 1.2.0 - 2/7/2014
#credits:
#   trbs (trbs.net)
#   r3boot (r3blog.nl)
#   dsc (own3d.be)

#put this in your crontab:
#3 4 * * * (cd /path/yo/want/to/index ; /path/for/scripts/00index.sh) > /var/log/00index.log 2>&1
(echo "# proto-index v=1.2.0 created=`date +%s`"; find . ! -name "lost+found" -follow -printf "%y %T@ %s %m %P\n"; echo "# end proto-index") | gzip -9c > 00INDEX.gz.tmp
mv 00INDEX.gz.tmp 00INDEX.gz