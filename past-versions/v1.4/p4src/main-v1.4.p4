#include <core.p4>
#include <tna.p4>

#ifndef TOFINO
    #define CPU_PORT_VALUE 64
#endif

#ifdef TOFINO2
    #include <tofino2.p4>
    #define CPU_PORT_VALUE 2
#endif

const PortId_t CPU_PORT = CPU_PORT_VALUE;

/*----------------------------------------------------------------------------*
 *                   C O N S T A N T S   &   T Y P E S                        *
 *----------------------------------------------------------------------------*/
#include "constants/types.p4"

/*----------------------------------------------------------------------------*
*                           H E A D E R S                                     *
*----------------------------------------------------------------------------*/
#include "headers/hdrs-main.p4"

/*----------------------------------------------------------------------------*
*                   I N G R E S S   P R O C E S S I N G                      *
*----------------------------------------------------------------------------*/

/*------------------ I N G R E S S  G L O B A L  M E T A D A T A ------------ */
#include "ingress/ig_metadata.p4"

/*------------------ I N G R E S S  H E A D E R S --------------------------- */
#include "ingress/ig_hdrs.p4"

/*------------------ I N G R E S S   P A R S E R -----------------------------*/
#include "ingress/ig_parser.p4"

/*------------------ I N G R E S S - M A T C H - A C T I O N ---------------- */
#include "ingress/ig_ctrl.p4"
// #include "ingress/ig_ctrl_modules/ig_save_tstamp.p4"


/*------------------ I N G R E S S  D E P A R S E R ------------------------- */
#include "ingress/ig_deparser.p4"

/*----------------------------------------------------------------------------*
*                   E G R E S S   P R O C E S S I N G                        *
*----------------------------------------------------------------------------*/

/*------------------ E G R E S S  H E A D E R S ----------------------------- */
#include "egress/eg_metadata.p4"

/*------------------ E G R E S S  G L O B A L  M E T A D A T A -------------- */
#include "egress/eg_hdrs.p4"

/*------------------ E G R E S S  P A R S E R ------------------------------- */
#include "egress/eg_parser.p4"

/*------------------ E G R E S S  M A T C H - A C T I O N ------------------- */
#include "egress/eg_ctrl.p4"

/*------------------ E G R E S S  D E P A R S E R --------------------------- */
#include "egress/eg_deparser.p4"

/*------------------ F I N A L  P A C K A G E ------------------------------- */

Pipeline(
    IngressParser(),
    Ingress(),
    IngressDeparser(),
    EgressParser(),
    Egress(),
    EgressDeparser()
) pipe;

Switch(pipe) main;