struct ig_hdrs_t{
    mirror_bridged_metadata_h bridged_md;
    ig_md_h ig_metadata;
    ethernet_h   ethernet;
    vlan_tag_h s_vlan;
    polka_h polka;
    custom_int_shim_h custom_int_shim; 
    custom_int_h[6] custom_int_stack; 
    vlan_tag_h u_vlan; 
    ipv4_h ipv4;
    udp_h udp;
    tcp_h tcp;
}