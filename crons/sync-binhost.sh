#!/bin/bash
BH_ARCH=i686

if [ "$(which lftp)" = "" ]; then
	echo "You must have lftp installed."
	exit
else
	cat >/tmp/lftp.scr <<EOF
open ftp://${BH_ARCH}:binhost@192.168.10.201
mirror -R ./ ./
EOF
fi
cd /usr/portage/packages/
$(which lftp) -f /tmp/lftp.scr || echo "Error while syncing packages."
rm /tmp/lftp.scr

