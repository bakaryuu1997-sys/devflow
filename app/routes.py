from fastapi import APIRouter

from app.routes_auth import router as auth_router
from app.routes_core import router as core_router
from app.routes_guards import router as guards_router
from app.routes_security import router as security_router
from app.routes_os import router as os_router
from app.routes_v4 import router as v4_router
from app.routes_v42 import router as v42_router
from app.routes_v64 import router as v64_router
from app.routes_v65 import router as v65_router
from app.routes_v66 import router as v66_router
from app.routes_v67 import router as v67_router
from app.routes_v68 import router as v68_router
from app.routes_v69 import router as v69_router
from app.routes_v70 import router as v70_router
from app.routes_v71 import router as v71_router
from app.routes_v72 import router as v72_router
from app.routes_v73 import router as v73_router
from app.routes_v74 import router as v74_router
from app.routes_v75 import router as v75_router
from app.routes_v76 import router as v76_router
from app.routes_v77 import router as v77_router
from app.routes_v78 import router as v78_router
from app.routes_v79 import router as v79_router
from app.routes_v80 import router as v80_router
from app.routes_v81 import router as v81_router
from app.routes_v82 import router as v82_router
from app.routes_v83 import router as v83_router
from app.routes_v84 import router as v84_router
from app.routes_v85 import router as v85_router
from app.routes_v86 import router as v86_router
from app.routes_v87 import router as v87_router
from app.routes_v88 import router as v88_router
from app.routes_v89 import router as v89_router
from app.routes_v90 import router as v90_router
from app.routes_v91 import router as v91_router
from app.routes_v92 import router as v92_router
from app.routes_v93 import router as v93_router
from app.routes_v94 import router as v94_router
from app.routes_v95 import router as v95_router
from app.routes_v96 import router as v96_router
from app.routes_v97 import router as v97_router
from app.routes_v98 import router as v98_router
from app.routes_v99 import router as v99_router
from app.routes_v100 import router as v100_router
from app.routes_v101 import router as v101_router
from app.routes_v102 import router as v102_router
from app.routes_v103 import router as v103_router
from app.routes_v104 import router as v104_router
from app.routes_v105 import router as v105_router
from app.routes_v106 import router as v106_router
from app.routes_v107 import router as v107_router
from app.routes_v108 import router as v108_router
from app.routes_v109 import router as v109_router
from app.routes_v110 import router as v110_router
from app.routes_v111 import router as v111_router
from app.routes_v112 import router as v112_router
from app.routes_v113 import router as v113_router
from app.routes_v114 import router as v114_router
from app.routes_v115 import router as v115_router
from app.routes_v116 import router as v116_router
from app.routes_v117 import router as v117_router
from app.routes_v118 import router as v118_router
from app.routes_v119 import router as v119_router
from app.routes_v120 import router as v120_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(core_router)
router.include_router(os_router)
router.include_router(guards_router)
router.include_router(security_router)
router.include_router(v4_router)
router.include_router(v42_router)
router.include_router(v64_router)
router.include_router(v65_router)
router.include_router(v66_router)
router.include_router(v67_router)
router.include_router(v68_router)
router.include_router(v69_router)
router.include_router(v70_router)
router.include_router(v71_router)
router.include_router(v72_router)
router.include_router(v73_router)
router.include_router(v74_router)
router.include_router(v75_router)
router.include_router(v76_router)
router.include_router(v77_router)
router.include_router(v78_router)
router.include_router(v79_router)
router.include_router(v80_router)
router.include_router(v81_router)
router.include_router(v82_router)
router.include_router(v83_router)
router.include_router(v84_router)
router.include_router(v85_router)
router.include_router(v86_router)
router.include_router(v87_router)
router.include_router(v88_router)
router.include_router(v89_router)
router.include_router(v90_router)
router.include_router(v91_router)
router.include_router(v92_router)
router.include_router(v93_router)
router.include_router(v94_router)
router.include_router(v95_router)
router.include_router(v96_router)
router.include_router(v97_router)
router.include_router(v98_router)
router.include_router(v99_router)
router.include_router(v100_router)
router.include_router(v101_router)
router.include_router(v102_router)
router.include_router(v103_router)
router.include_router(v104_router)
router.include_router(v105_router)
router.include_router(v106_router)
router.include_router(v107_router)
router.include_router(v108_router)
router.include_router(v109_router)
router.include_router(v110_router)
router.include_router(v111_router)
router.include_router(v112_router)
router.include_router(v113_router)
router.include_router(v114_router)
router.include_router(v115_router)
router.include_router(v116_router)
router.include_router(v117_router)
router.include_router(v118_router)
router.include_router(v119_router)
router.include_router(v120_router)
