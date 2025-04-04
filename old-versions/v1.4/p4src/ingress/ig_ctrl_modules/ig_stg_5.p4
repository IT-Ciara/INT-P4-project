typedef bit<2> ig_loop_stats_index_t;

control ig_stg_5(
    inout ig_hdrs_t hdr,
    inout ig_metadata_t meta,
    in ingress_intrinsic_metadata_t ig_intr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md
) {
    ig_loop_stats_index_t ig_loop_stats_index = 0;
    // Counters
    //Direct counter
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_port_loop_tbl_counter;
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) ig_vlan_loop_tbl_counter;
    
    //Indirect counter
    Counter<bit<64>, ig_loop_stats_index_t>(1<<2, CounterType_t.PACKETS_AND_BYTES) ig_loop_counter;

    //Actions
    action send_back(ig_loop_stats_index_t stats_idx){
        ig_tm_md.ucast_egress_port = ig_intr_md.ingress_port;
        ig_loop_stats_index = stats_idx;
        ig_port_loop_tbl_counter.count();  
        meta.port_loop = 1;
    }

    //Tables
    table ig_port_loop_tbl {
        key = {
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            send_back;
        }
        size = 100;
        counters = ig_port_loop_tbl_counter;
    }


    action send_back_vlan(ig_loop_stats_index_t stats_idx){
        ig_tm_md.ucast_egress_port = ig_intr_md.ingress_port;
        ig_loop_stats_index = stats_idx;
        ig_vlan_loop_tbl_counter.count();
        meta.vlan_loop = 1;
    }  

    table  ig_vlan_loop_tbl {
        key = {
            hdr.outer_vlan.vid: exact;
            ig_intr_md.ingress_port: exact;
        }
        actions = {
            send_back_vlan;
        }
        size = 100;
        counters = ig_vlan_loop_tbl_counter;
    }

    apply{
        if(ig_port_loop_tbl.apply().miss){
            ig_vlan_loop_tbl.apply();
        }
        ig_loop_counter.count(ig_loop_stats_index);
    }

}