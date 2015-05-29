kill `cat newaUtil_run.pid`
rm newaUtil_err.log
rm newaUtil_run.log
python run_newaUtil.py -p 4014 -l newaUtil_run.log -P newaUtil_run.pid -m 3
ls -l newaUtil*.log
