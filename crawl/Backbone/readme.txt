===========------------------ How Panacea Crawling tool works ----------------------===============

If a team name is there in the "team_data.pbf" file then a new thread will be created for that team. This thread will run endless and will search for batches.
If a team name is there in the "team_data_to_stop.pbf" file then all the process will be stopped for that team. This can not be un done. (Not working now)
If a batch name is there is the "batches_to_run.pbf" file then a new thread will be created for that batch. This thread will get completed after all the server threads initiated by it gets completed.
If a batch name is there is the "batches_to_stop.pbf" file then that batch will be stopped and the data will be processed for it.
If a batch name is removed from the "batches_to_stop.pbf" file then that batch will be restarted from the point where it was stopped.
If a batch name is removed from the "batches_to_run.pbf" file after putting it in "batches_to_stop.pbf" file then that batch will be stopped completely and cannot be resumed.
If a batch name is removed from the "batches_to_run.pbf" file before putting it in "batches_to_stop.pbf" file then the system will throw an error. (DO NOT DO THIS)