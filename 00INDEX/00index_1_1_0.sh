#!/bin/bash -e
#proto-index 1.1.0 - 2-6-2014
#credits:
#   trbs (trbs.net)
#   r3boot (r3blog.nl)
#   maze (maze.io)

#put this in your crontab:
#3 4 * * * (cd /path/yo/want/to/index ; /path/for/scripts/00index.sh) > /var/log/00index.log 2>&1
(
    echo "# proto-index v=1.1.0 created=`date +%s`"
    find . ! -name "lost+found" -printf "%y %T@ %s %m %P " -exec file -b --mime-type "{}" \;
    echo "# end proto-index"
) | gzip -9c > 00INDEX.gz.tmp && mv 00INDEX.gz.tmp 00INDEX.gz