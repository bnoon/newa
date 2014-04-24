kill `cat newaVegModel_run.pid`
rm newaVegModel_err.log
rm newaVegModel_run.log
python run_newaVegModel.py -p 4016 -l newaVegModel_run.log -P newaVegModel_run.pid -m 3
ls -l newaVegModel*.log
