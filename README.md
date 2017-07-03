#Ip re-routing with sdn and nfv: based on the below paper

http://ieeexplore.ieee.org/document/7417318/

#description

Created a topology with multiple servers and I was able to detect server down(h2 down). And traffic
towards the server(h2) that is down is redirected towards NFV-IP rewriter where destination
ip was re-rwitten to a working server's ip-address(either h3 or h4). Through this method end user can
access server even if server is down.

#Requirements: 

    ● ubuntu
    ● pox controller installed
    ● python installed 
    ● mininet installed
    ● Click installed 
        
#Code
        
    .final2.py (it contains the topology,place inside mininet/examples and execute it by sudo python final2.py)

    .host_tracker.py (it is the modified file,place it inside pox/pox/host_tracker after keeping the orginal file safely , and this file will be executed while starting the controller)

    .kj_global.py (for storing ip,mac of hosts that goes down, place it inside pox/pox/host_tracker)

    .kj_host.py (place this file inside pox/pox/misc, and this file will be executed while starting the controller)
       
    .kj_learning.py (place this inside pox/pox/forwarding,it is the modified version of l2_learning.py, this file will be executed while starting the controller)
    
    .www.click (this performis re-routing) place this inside click/conf 

#Execution
	
	.1) starting the controller,inside pox folder type

       ./pox.py openflow.discovery forwarding.kj_learning misc.kj_host
    
    .2) running topology

       place inside mininet/examples and execute it by sudo python final2.py 
       now topology is created .....type following commands(before and after starting click for checking ip-rerouting )
       
       		nodes (shows nodes list)
       		links (shows links)
       		pingall (to ping all)
       		link h2 s1 down (to make server down)
       		link h2 s1 up (to make link up)
       		h1 wget h2 (trying to access server)
   			dpctl-dump-flows (to view switch table info)
            h2 wireshark& (to start wireshark in server (h2))
       .2.1) create server 

             inside mininet type h2 xterm&(for opening xterm of a host inside mininet)
             inside xterm type python -m SimpleHTTPServer 80
             now the host h2 acts as a server

    .3) running click(nfv)
        
        inside click folder type

            sudo ~/bin/click conf/www.click  

#sdn Referances (i refered these projects.....thanks for those awesome guys)

   .https://github.com/tssurya/Software-Defined-Networking-and-Network-Functions-Virtualization

   .https://github.com/rakeshgn31/SDN_Project

   .https://github.com/syafiq/IK-2220-SDN-and-NFV

   .https://github.com/gauravpuri334/SDN-NFV

   .https://github.com/pandan0315/SDN

   .https://github.com/noxrepo/pox/issues/180

   .https://stackoverflow.com/questions/43121566/how-to-make-controller-detect-link-down-or-host-down-in-the-following-topology