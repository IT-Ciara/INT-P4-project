parser EgressParser(packet_in        pkt,
    /* User */
    out eg_hdrs_t          hdr,
    out eg_metadata_t         meta,
    /* Intrinsic */
    out egress_intrinsic_metadata_t  eg_intr_md)
{
    state start{
        pkt.extract(eg_intr_md);

        //==== Output Test ====
        meta.user_port = 0;
        meta.p4_sw_port = 0;
        meta.transit_port = 0;

        transition parse_metadata;
    }
    state parse_metadata {
        mirror_h mirror_md = pkt.lookahead<mirror_h>();
        transition select(mirror_md.pkt_type) {
            PKT_TYPE_MIRROR : parse_mirror_md;
            PKT_TYPE_NORMAL : parse_bridged_md;
            default : accept;
        }
    }    
    state parse_bridged_md {
        pkt.extract(hdr.bridged_md);
        transition parse_ig_metadata;
    }
    state parse_mirror_md {
        mirror_h mirror_md;
        // pkt.extract(mirror_md);
        pkt.extract(hdr.mirror_md);
        transition parse_ethernet;
    }
    state parse_ig_metadata {
        pkt.extract(hdr.ig_metadata);
        meta.md_type = hdr.ig_metadata.md_type;
        meta.ig_tstamp = hdr.ig_metadata.ig_tstamp;
        transition parse_ethernet;
    }
    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type) {
            ETHER_TYPE_POLKA : parse_polka;
            ETHER_TYPE_IPV4 : parse_ipv4;
            ETHER_TYPE_VLAN : parse_u_vlan;
            ETHER_TYPE_QINQ : parse_s_vlan;            
            default : accept;
        }
    }     
    state parse_s_vlan{
        pkt.extract(hdr.s_vlan);
        transition select(hdr.s_vlan.ether_type) {
            ETHER_TYPE_IPV4 : parse_ipv4;
            ETHER_TYPE_VLAN : parse_u_vlan;           
            default : accept;
        }
    }
    state parse_polka{
        pkt.extract(hdr.polka);
        transition select(hdr.polka.proto) {
            ETHER_TYPE_IPV4 : parse_ipv4;
            ETHER_TYPE_VLAN : parse_u_vlan;
            ETHER_TYPE_INT : parse_int_shim;
            default : accept;
        }
    }
    state parse_int_shim{
        pkt.extract(hdr.custom_int_shim);
        transition select(hdr.custom_int_shim.int_count, hdr.custom_int_shim.next_hdr){
            (1, 0x8100): parse_0_int;
            (1,_): parse_0_int;
            (2, 0x8100): parse_1_int;
            (2,_): parse_1_int;
            (3, 0x8100): parse_2_int;
            (3,_): parse_2_int;
            (4, 0x8100): parse_3_int;
            (4,_): parse_3_int;
            (5, 0x8100): parse_4_int;
            (5,_): parse_4_int;
            (6, 0x8100): parse_5_int;
            (6,_): parse_5_int;
            (_,0x8100): parse_u_vlan;
            (_,0x0800): parse_ipv4;
            default: accept;
        }
    }    
    state parse_5_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        pkt.extract(hdr.custom_int_stack[2]);
        pkt.extract(hdr.custom_int_stack[3]);
        pkt.extract(hdr.custom_int_stack[4]);
        pkt.extract(hdr.custom_int_stack[5]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_u_vlan;
            default: accept;
        }
    }
    state parse_4_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        pkt.extract(hdr.custom_int_stack[2]);
        pkt.extract(hdr.custom_int_stack[3]);
        pkt.extract(hdr.custom_int_stack[4]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_u_vlan;
            default: accept;
        }
    }
    state parse_3_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        pkt.extract(hdr.custom_int_stack[2]);
        pkt.extract(hdr.custom_int_stack[3]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_u_vlan;
            default: accept;
        }
    }
    state parse_2_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        pkt.extract(hdr.custom_int_stack[2]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_u_vlan;
            default: accept;
        }
    }

    state parse_1_int{
        pkt.extract(hdr.custom_int_stack[0]);
        pkt.extract(hdr.custom_int_stack[1]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_u_vlan;
            default: accept;
        }
    }
    state parse_0_int{
        pkt.extract(hdr.custom_int_stack[0]);
        transition select(hdr.custom_int_shim.next_hdr){
            0x8100: parse_u_vlan;
            default: accept;
        }
    }

    state parse_u_vlan{
        pkt.extract(hdr.u_vlan);
        transition select(hdr.u_vlan.ether_type) {
            ETHER_TYPE_IPV4 : parse_ipv4;
            default : accept;
        }
    }
    state parse_ipv4{
        pkt.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            IP_PROTO_UDP : parse_udp;
            IP_PROTO_TCP : parse_tcp;
            default : accept;
        }
    }
    state parse_udp{
        pkt.extract(hdr.udp);
        transition accept;
    }
    state parse_tcp{
        pkt.extract(hdr.tcp);
        transition accept;
    }


}