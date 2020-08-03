set -eu

function run() {
    echo -e "> $1"
    eval $1
}

## MIGRATION ##

echo '[*] Database Migration'
run 'cd ./konoha/models'
run 'PYTHONPATH="." alembic upgrade head'
run 'PYTHONPATH="." alembic revision --autogenerate -m \"$(date +%Y_%m_%d_%H_%M_%S)\"'
run 'PYTHONPATH="." alembic upgrade head'
run 'cd ../..'

###############

if [ $1 = '--dev' ]; then
run 'pwd'
run 'nodemon -e py,ini --ignore konoha/models/versions --exec python -m konoha config.ini'
else
run 'python -m konoha config.ini'
fi