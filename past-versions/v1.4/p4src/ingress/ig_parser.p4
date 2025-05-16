parser IngressParser(packet_in        pkt,
    /* User */
    out ig_hdrs_t          hdr,
    out ig_metadata_t         meta,
    /* Intrinsic */
    out ingress_intrinsic_metadata_t  ig_intr_md)
{
    /* This is a mandatory state, required by Tofino Architecture */
    state start {
        //Initialize metadata
        meta.user_port = 0;
        meta.sdn_trace = 0;
        meta.dropped = 0;
        meta.port_loop = 0;
        meta.vlan_loop = 0;
        meta.l4_dst_port = 0;
        meta.do_ing_mirroring = 0;
        meta.do_egr_mirroring = 0;
        meta.ing_mir_ses = 0;
        meta.egr_mir_ses = 0;
        meta.pkt_type = 0;
        meta.copy = 0;
        meta.normal = 0;
        meta.has_polka = 0;
        pkt.extract(ig_intr_md);
        pkt.advance(PORT_METADATA_SIZE);
        transition parse_ethernet;
    }
    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type) {
            0x8100 : parse_vlan;
            0x0800 : parse_ipv4;
            default : accept;
        }
    }
    state parse_vlan {
        pkt.extract(hdr.outer_vlan);
        transition select(hdr.outer_vlan.ether_type) {
            0x0800 : parse_ipv4;
            default : accept;
        }
    }
    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            6 : parse_tcp;
            17 : parse_udp;
            default : accept;
        }
    }
    state parse_tcp {
        pkt.extract(hdr.tcp);
        meta.l4_dst_port = hdr.tcp.dst_port;
        transition accept;
    }
    state parse_udp {
        pkt.extract(hdr.udp);
        meta.l4_dst_port = hdr.udp.dst_port;
        transition accept;
    }
}