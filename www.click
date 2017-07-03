// AverageCounter
out_eth1 :: AverageCounter;
out_eth2 :: AverageCounter;
in_eth1 :: AverageCounter;
in_eth2 :: AverageCounter;

// Counter for classifier

// packets
pack_req_ex :: Counter;
pack_res_ex :: Counter;
pack_req_in :: Counter;
pack_res_in :: Counter;

// arp
arp_req_ex :: Counter;
arp_res_ex :: Counter;
arp_req_in :: Counter;
arp_res_in :: Counter;

// Service
service_count :: Counter;

// ICMP
icmp_count :: Counter;

// Dropped
drop_ex :: Counter;
drop_in :: Counter;

// Device declaration
fr_ext :: FromDevice(s2-eth1, SNIFFER false);
to_ext :: Queue(200) -> out_eth1 -> pack_res_ex -> ToDevice(s2-eth1);
fr_int :: FromDevice(s2-eth2, SNIFFER false);
to_int :: Queue(200) -> out_eth2 -> pack_res_in -> ToDevice(s2-eth2);

// ARP Responder
arpr_ext :: ARPResponder(10.0.0.2 fe:24:e2:fa:39:56);
arpr_int :: ARPResponder(10.0.0.2 a2:fe:e8:7d:25:46);

// ARP Querier

arpq_ext :: ARPQuerier(10.0.0.2, fe:24:e2:fa:39:56);
arpq_int :: ARPQuerier(10.0.0.2, a2:fe:e8:7d:25:46);

// Classifier internal and external
c_in,c_ex :: Classifier(12/0806 20/0001,	// ARP Request
			12/0806 20/0002,	// ARP Response
			12/0800, 		// IP Packet
			-); 			// the rest
c_ip_in :: IPClassifier(
			dst 10.0.0.2 tcp port 80, 	// http req
			dst 10.0.0.2 and icmp,	// icmp echo req
			- );

rewr :: IPRewriter(weblb);
weblb :: RoundRobinIPMapper(
			10.0.0.2 - 10.0.0.3 - 1 0,	// 1st webserver
			10.0.0.2 10.0.0.4 - 1 0);	// 2nd webserver
				// 3rd webserver

fr_ext -> in_eth1 -> pack_req_ex -> c_in;
c_in[0] -> Print(www_ci_0) -> arp_req_ex -> arpr_ext[0] -> to_ext;
c_in[1] -> Print(www_ci_1) -> arp_res_ex -> [1]arpq_ext;
c_in[2] -> Print(www_ci_2) -> Strip(14) -> CheckIPHeader ->IPPrint(***ini)-> c_ip_in;
c_in[3] -> Print(www_ci_3) -> Discard;

c_ip_in[0] -> Print(www_c_ip_in0) -> service_count -> rewr[1] ->IPPrint(***) -> [0]arpq_int->to_int;
c_ip_in[1] -> Print(www_c_ip_in1) -> icmp_count -> ICMPPingResponder -> [0]arpq_ext -> to_ext;
c_ip_in[2] -> Print(www_c_ip_in2) -> drop_ex -> Discard;

fr_int -> in_eth2 -> pack_req_in -> c_ex;
c_ex[0] -> Print(www_ce_0) -> arp_req_in -> arpr_int[0] -> to_int; 
c_ex[1] -> Print(www_ce_1) -> arp_res_in -> [1]arpq_int;
c_ex[2] -> Print(www_ce_2) -> Strip(14) -> CheckIPHeader -> rewr[0]->IPPrint(***) -> [0]arpq_ext -> to_ext;
c_ex[3] -> Print(www_ce_3) -> drop_in -> Discard;
