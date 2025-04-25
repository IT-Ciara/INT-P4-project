#include <core.p4>


#if __TARGET_TOFINO__ == 2
#include <t2na.p4>
#define CPU_PORT_VALUE 2
#define MIRROR_TYPE_WIDTH 4
#else
#include <tna.p4>
#define CPU_PORT_VALUE 64 
#define MIRROR_TYPE_WIDTH 3
#endif


typedef bit<MIRROR_TYPE_WIDTH> mirror_type_t;

// ====== Stage 1: User Port? ======
// ====== Stage 2: Has Polka ID? ======
// ====== Stage 3: Topology Discovery? ======
// ====== Stage 3: Link Continuity Test? ======
// ====== Stage 4: Partner-Provided Link? ======
// ====== Stage 5: SDN Trace? ======
// ====== Stage 6: Contention Flow? ======
// ====== Stage 7: Port Loop? ======
// ====== Stage 7: VLAN Loop? ======
// ====== Stage 8: Flow Mirror? ======
// ====== Stage 9: Port Mirror? ======
// ====== Stage 10: No Polka - Destination Endpoint? ======
// ====== Stage 11: Polka - Destination Endpoint? ======

//=============================================================================
//             C O N S T A N T S  &  T Y P E S
//=============================================================================
#include "include/1_cst_types.p4"
//=============================================================================
//             H E A D E R S
//=============================================================================
#include "include/2_hdrs.p4"
//=============================================================================
//                     I N G R E S S   P I P E L I N E
//=============================================================================
#include "include/3_ig_md.p4"
//================ I N G R E S S   H E A D E R S ==============================
#include "include/4_ig_hdrs.p4"
//================ I N G R E S S   P A R S E R ================================
#include "include/5_ig_prs.p4"
//================ I N G R E S S   C O N T R O L ==============================
#include "include/6_ig_ctl.p4"
//================ I N G R E S S  D E P A R S E R =============================
#include "include/7_ig_dprs.p4"
//=============================================================================
//                     E G R E S S   P I P E L I N E
//=============================================================================
//================ E G R E S S   M E T A D A T A ==============================
#include "include/8_eg_md.p4"
//================ E G R E S S   H E A D E R S ================================
#include "include/9_eg_hdrs.p4"
//================ E G R E S S   P A R S E R ================================
#include "include/10_eg_prs.p4"
//================ E G R E S S   C O N T R O L ==============================
#include "include/11_eg_ctl.p4"
//================ E G R E S S  D E P A R S E R =============================
#include "include/12_eg_dprs.p4"

//=============================================================================
//                F I N A L   P A C K A G E 
//=============================================================================

Pipeline(
    IngressParser(),
    Ingress(),
    IngressDeparser(),
    EgressParser(),
    Egress(),
    EgressDeparser()
) pipe;

Switch(pipe) main;

