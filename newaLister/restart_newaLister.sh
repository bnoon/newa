kill `cat newaLister_run.pid`
rm newaLister_err.log
rm newaLister_run.log
python run_newaLister.py -p 4010 -l newaLister_run.log -P newaLister_run.pid -m 3
ls -l newaLister*.log
