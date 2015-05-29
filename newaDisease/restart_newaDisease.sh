kill `cat newaDisease_run.pid`
rm newaDisease_err.log
rm newaDisease_run.log
python run_newaDisease.py -p 4011 -l newaDisease_run.log -P newaDisease_run.pid -m 3
ls -l newaDisease*.log
