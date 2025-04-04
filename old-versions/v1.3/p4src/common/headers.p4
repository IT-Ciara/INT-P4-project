/* -*- P4_16 -*- */

/**************** V1.2 ****************/

/*************************************************************************
 ***********************  H E A D E R S  *********************************
 *************************************************************************/

/*  Define all the headers the program will recognize             */
/*  The actual sets of headers processed by each gress can differ */

/* Standard ethernet header */
header ethernet_h {
mac_addr_t   dst_addr;
mac_addr_t   src_addr;
bit<16> ether_type;
}

header vlan_tag_h {
    bit<3>       pri;
    bit<1>       dei;
    bit<12>      vid;
    bit<16> ether_type;
}

header ipv4_h {
bit<4>       version;
bit<4>       ihl;
bit<8>       diffserv;
bit<16>      total_len;
bit<16>      identification;
bit<3>       flags;
bit<13>      frag_offset;
bit<8>       ttl;
bit<8>       protocol;
bit<16>      hdr_checksum;
ipv4_addr_t  src_addr;
ipv4_addr_t  dst_addr;
}

header ipv6_h{
    bit<4>    version;
    bit<8>    trafficClass;
    bit<20>   flowLabel;
    bit<16>   payloadLen;
    bit<8>    nextHdr;
    bit<8>    hopLimit;
    ipv6_addr_t srcAddr;
    ipv6_addr_t dstAddr;
}

header udp_h {
    bit<16> src_port;
    bit<16> dst_port;
    bit<16> length;
    bit<16> checksum;
}

header tcp_h {
    bit<16> src_port;
    bit<16> dst_port;
    bit<32> seq_no;
    bit<32> ack_no;
    bit<4>  data_offset;
    bit<4>  res;
    bit<8>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgent_ptr;
}

header payload_h{
    bit<104> data;
}

header custom_int_shim_h{
    bit<1> full_int_stack;
    bit<1> full_mtu;
    bit<6> reserved;
    bit<8> int_count;
    bit<16> next_hdr;
}

header custom_int_h{
    bit<32> data;
}
