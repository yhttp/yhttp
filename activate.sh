# Pick first word of directory as venv name
HERE=`dirname "$(readlink -f "$BASH_SOURCE")"`

DIRNAME=$(basename ${HERE})
VENVNAME=$(echo ${DIRNAME} | cut -d'-' -f1)

VENV=${HOME}/.virtualenvs/${VENVNAME}


source ${VENV}/bin/activate
