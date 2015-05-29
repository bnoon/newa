kill `cat newaModel_run.pid`
rm newaModel_err.log
rm newaModel_run.log
python run_newaModel.py -p 4012 -l newaModel_run.log -P newaModel_run.pid -m 3
ls -l newaModel*.log
