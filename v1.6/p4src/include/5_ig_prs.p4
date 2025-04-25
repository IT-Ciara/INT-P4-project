parser IngressParser(packet_in        pkt,
    /* User */
    out ig_hdrs_t          hdr,
    out ig_metadata_t         meta,
    /* Intrinsic */
    out ingress_intrinsic_metadata_t  ig_intr_md)
{
    state start{
        pkt.extract(ig_intr_md);
        pkt.advance(PORT_METADATA_SIZE);
        //Initialize the metadata
        meta.do_ing_mirroring = 0;
        meta.do_egr_mirroring = 0;
        meta.pkt_type = PKT_TYPE_NORMAL;
        meta.ing_mir_ses = 0;
        meta.egr_mir_ses = 0;
        //Ing Metadata 
        hdr.ig_metadata.setValid();
        hdr.ig_metadata.md_type = 0x7E;
        hdr.ig_metadata.ig_tstamp = ig_intr_md.ingress_mac_tstamp; 
        hdr.ig_metadata.ig_port = ig_intr_md.ingress_port;

        //==== Input Test ====
        meta.user_port = 0;

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
            // ETHER_TYPE_POLKA : parse_polka;
            ETHER_TYPE_IPV4 : parse_ipv4;
            ETHER_TYPE_VLAN : parse_u_vlan;           
            default : accept;
        }
    }

    state parse_polka{
        pkt.extract(hdr.polka);
        meta.polka_routeid = hdr.polka.routeid;
        transition select(hdr.polka.proto) {
            ETHER_TYPE_IPV4 : parse_ipv4;
            ETHER_TYPE_VLAN : parse_u_vlan;
            default : accept;
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