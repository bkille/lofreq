echoerror() {
    echo "ERROR: $@" 1>&2
}
echook() {
    echo "OK: $@" 1>&2
}
echowarn() {
    echo "WARN: $@" 1>&2
}
echoinfo() {
    echo "INFO: $@" 1>&2
}
echodebug() {
    echo "DEBUG: $@" 1>&2
}

# md5sum is md5 on mac
md5=$(which md5sum 2>/dev/null || which md5)

seq=$(which seq 2>/dev/null || which gseq)

LOFREQ=../src/lofreq/lofreq
#LOFREQ=../lofreq_star-2.0.0-beta/lofreq/lofreq


