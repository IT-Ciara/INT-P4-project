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
        meta.user_flag = 0;
        meta.dropped = 0;
        meta.polka = 0;
        meta.port_loop = 0;
        meta.vlan_loop = 0;
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
        transition accept;
    }
    state parse_udp {
        pkt.extract(hdr.udp);
        transition accept;
    }
}