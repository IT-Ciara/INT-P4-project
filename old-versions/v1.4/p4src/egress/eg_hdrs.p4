struct eg_hdrs_t {
    mirror_bridged_metadata_h bridged_md;
    ethernet_h   ethernet;
    vlan_tag_h outer_vlan;
    custom_int_shim_h custom_int_shim;
    custom_int_h[6] custom_int_stack;
    vlan_tag_h inner_vlan;
    ipv4_h ipv4;
    udp_h udp;
    tcp_h tcp;
}