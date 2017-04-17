##usage:
 * manual part:
   * args:
		
			<share_dir>: where the downloaded data is located
			<source>: data source (caida, iplane, etc)
			<nfs_server_ip>: downloader host ip #not container ip
			<nfs_client_ip>: analyzer host ip
   * run:

			#on nfs-server
			#generate state file
			root# ./scan.py <share_dir>
			#start httpd
			root# nohup python httpd.py >httpd_log 2>&1 &
			
			#on nfs-client
			root# nohup python run.py <source> <mount_point> >analyze_log 2>&1 &

 * download:
			
			#generate state file
			root# python cron.py <source>
			#start httpd
			root# nohup python httpd.py >httpd_log 2>&1 &
			#start downloading.
			root# nohup python download.py caida >download_log 2>&1 &
