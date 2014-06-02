#!/bin/bash
#proto-index 1.0.0 - 2013
#credits:
#   r3boot (http://r3blog.nl)
#
#put this in your crontab:
#3 4 * * * (cd /path/yo/want/to/index ; /path/for/scripts/00index.sh) > /var/log/00index.log 2>&1
(echo "# proto-index v=1.0.0 created=`date +%s`"; find . ! -name "lost+found" -printf "%y %T@ %s %m %P\n"; echo "# end proto-index") | gzip -9c > 00INDEX.gz.tmp
mv 00INDEX.gz.tmp 00INDEX.gz
