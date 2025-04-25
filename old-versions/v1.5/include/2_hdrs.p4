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
header polka_h{
    bit<8>          version;
    bit<8>          ttl;
    bit<16>         proto;
    polka_route_t   routeid;  
}
header custom_int_shim_h{
    bit<48> ig_tstamp;
    bit<1> full_int_stack;
    bit<1> full_mtu;
    bit<6> _padding;
    bit<8> int_count;
    bit<16> next_hdr;
    bit<16> reserved;
}
header custom_int_h{
    bit<32> data;
}
//========= MIRRORING ==========//
header mirror_bridged_metadata_h {
    pkt_type_t pkt_type;
    @flexible bit<1> do_egr_mirroring;  //  Enable egress mirroring
    @flexible MirrorId_t egr_mir_ses;   // Egress mirror session ID
}
header mirror_h {
    pkt_type_t  pkt_type;
}
//=========Ingress Metadata=========//
header ig_md_h {
    bit<8> md_type;
    bit<48> ig_tstamp;
    bit<1> endpoint;
    // ==== Stage 4: Partner-provided link? ====
    bit<1> rm_s_vlan_add_int;
    bit<6> padding;
}