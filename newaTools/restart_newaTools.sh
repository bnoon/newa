kill `cat newaTools_run.pid`
rm newaTools_err.log
rm newaTools_run.log
python run_newaTools.py -p 4017 -l newaTools_run.log -P newaTools_run.pid -m 3
ls -l newaTools*.log
