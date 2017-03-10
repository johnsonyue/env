##usage:
 * manual part:
   * args:
		
			<share_dir>: where the downloaded data is located
			<source>: data source (caida, iplane, etc)
			<nfs_server_ip>: downloader host ip #not container ip
			<nfs_client_ip>: analyzer host ip
   * nfs:
		
			#on nfs-server
			root# apt-get install nfs-kernel-server
			root# echo "<share_dir>	<nfs_client_ip>(ro,sync,no_subtree_check)"
			
			#on nfs-client
			root# apt-get install nfs-common
			root# mkdir -p <mount_point>
			root# mount <nfs_server_ip>:<share_dir> <mount_point>
   * run:

			#on nfs-server
			#generate state file
			root# ./scan.py <share_dir>
			#start httpd
			root# nohup python httpd.py >httpd_log 2>&1 &
			
			#on nfs-client
			root# nohup python run.py <source> <mount_point> >analyze_log 2>&1 &
		
##design notes:
 * trace defines **one unified** data format used to store raw trace data.
   * design: put hard-coded content in one file,
   * advantages:
     * better readability
     * easier to swap,add,rm fields
 * to add new data sources (e.g. CAIDA, iPlane, RIPE Atlas ..),
   * implement decoding method in decode.sh
   * implement uniform method in uniform.py
 * to add new data fields to trace:
   * add field index to trace.py
   * modify uniform methods in uniform.py
   * modify analyze methods in analyze.py
