const TRANSLATIONS = {
  en: {
    "workspace_back_btn": "Return to Governance Dashboard",
    "Low": "Low",
    "Medium": "Medium",
    "High": "High",
    "Critical": "Critical",
    "Safe": "Safe",
    "Not Safe": "Not Safe",
    // Brand & Sidebar
    "sidebar_title": "DevFlow Guard",
    "sidebar_subtitle": "Release Risk OS",
    "sidebar_workspace_context": "Workspace Context",
    "sidebar_project": "Project",
    "sidebar_release": "Release",
    "sidebar_create_workspace": "Create Workspace",
    "sidebar_create_project_btn": "Create project",
    "sidebar_create_release_btn": "Create release",
    "sidebar_local_data": "Local Data",
    "local_data_loading": "Loading data stats…",
    "local_data_backup": "Download backup (.db)",
    "local_data_reset": "Reset all data",
    "guide_badge": "Guide",
    "guide_summary": "How to use DevFlow Guard",
    "guide_step1_desc": "<strong>Create data:</strong> click <em>Initialize Local Sample Workspace</em> above to generate demo projects, releases, and requirements.",
    "guide_step2_desc": "<strong>Pick context:</strong> choose a <em>Project</em> and <em>Release</em> in the left sidebar (Workspace Context).",
    "guide_step3_desc": "<strong>Follow the rail:</strong> walk the six steps below — Start → Artifacts → Traceability → Impact → Gate → Report.",
    "guide_step4_desc": "<strong>Scan artifacts:</strong> in Step 2, upload SQL / log / test / OpenAPI files to run the risk guards.",
    "guide_step5_desc": "<strong>Review history:</strong> open the <em>Operations Workspace</em> (sidebar) for browser-local notes and the audit timeline.",
    "guide_note_desc": "Everything runs locally on SQLite — no internet or login required. Close this panel with the arrow; it stays collapsed for the session.",
    "topbar_desc": "One focused surface for release risk, traceability, evidence, and operator history.",
    "cmd_kicker": "Today command",
    "cmd_title": "Start with the release gate, then move evidence forward.",
    "cmd_desc": "Use the primary action to initialize or refresh the workspace, then follow the six-step rail only when the previous checkpoint is clear.",
    "sidebar_flow_label": "Recommended flow",
    "sidebar_workspace_link": "Open Operations Workspace",
    "sidebar_why_title": "Why it matters",
    "sidebar_why_desc": "Jira tracks work. This checks release risk, gaps, evidence and safety.",
    
    // Topbar & Auth
    "topbar_eyebrow": "DevFlow Governance OS",
    "topbar_title": "Release Compliance Control Center",
    "topbar_logout": "Logout",
    
    // Login overlay
    "login_title": "Sign in to DevFlow",
    "login_email": "Email address",
    "login_password": "Password",
    "login_submit": "Sign In",
    "login_toggle_register": "Don't have an account? <span class=\"link-highlight\">Register</span>",
    "register_title": "Create a new account",
    "register_submit": "Register Account",
    "register_toggle_login": "Already have an account? <span class=\"link-highlight\">Sign In</span>",
    
    // Stepper
    "step_1": "Start",
    "step_2": "Artifacts",
    "step_3": "Traceability",
    "step_4": "Impact",
    "step_5": "Gate",
    "step_6": "Report",
    
    // Metrics Grid
    "metric_step": "Current step",
    "metric_blockers": "Blockers",
    "metric_traceability": "Traceability",
    "metric_mode": "Mode",
    "metric_mode_val": "Offline",
    
    // Step Panels
    "step1_title": "Workspace Initialization & Governance Control",
    "step1_desc": "Prepare controlled workspace data, then move into artifact upload.",
    "step1_btn_init": "Initialize Local Sample Workspace",
    "step1_btn_refresh": "Refresh Workspace Dashboard",
    "step1_btn_today": "View Today's Focus",
    "step1_btn_verify": "Verify Audit Integrity",
    "step1_btn_next": "Next Step Guide",
    
    "step2_title": "Upload and Scan Release Artifacts",
    "step2_desc": "Use examples/ or real project files.",
    "step2_btn_sql": "Scan SQL",
    "step2_btn_logs": "Scan Logs",
    "step2_btn_tests": "Scan Tests",
    "step2_btn_api": "Scan API Diff",
    "step2_btn_review": "Review Guard Findings",
    
    "step3_title": "Traceability Matrix & Release Governance",
    "step3_desc": "Check links, analyze risk profiles, and audit recovery policies.",
    "step3_btn_trace": "Run Traceability",
    "step3_btn_risk": "Risk Scan",
    
    "step4_title": "Requirement Change Impact",
    "step4_desc": "Record a requirement change and see affected items.",
    "step4_btn_record": "Record Change",
    "step4_btn_impact": "Run Impact",
    
    "step5_title": "Advanced Release Gate",
    "step5_desc": "Analyze code paths, environment config and final readiness.",
    "step5_btn_code": "Code Risk",
    "step5_btn_env": "Env Guard",
    "step5_btn_ready": "Readiness",
    "step5_btn_fix": "Fix Demo Blockers",
    
    "step6_title": "Evidence Report & Production Release",
    "step6_desc": "Export evidence package, verify audit signatures, and deploy release.",
    "step6_btn_prev": "Preview Evidence",
    "step6_btn_download": "Download Evidence",
    "step6_btn_notes": "Release Notes",
    
    // Dynamic alerts
    "toast_session_checking": "Checking session...",
    "toast_logged_out": "Logged out",
    "toast_logged_in": "Logged in as",
    
    // Dynamic Renderers
    "no_traceability_rows_yet": "No traceability rows yet.",
    "tasks": "Tasks",
    "apis": "APIs",
    "tests": "Tests",
    "bugs": "Bugs",
    "commits": "Commits",
    "no_readiness_result_yet": "No readiness result yet.",
    "readiness_score": "Readiness score",
    "blockers_title": "Blockers",
    "warnings_title": "Warnings",
    "recommendations_title": "Recommendations",
    "no_guard_findings_yet": "No guard findings yet.",
    "finding": "Finding",
    "blocking": "Blocking",
    "non_blocking": "Non-blocking",
    "no_active_requirements": "No active requirements to review.",
    "score": "Score",
    "risks": "Risks",
    "priority": "Priority",
    "Fix hints": "Fix hints",
    "release_risk_by_requirement": "Release risk by Requirement",
    "risks_plural": "risk(s)",
    "top_actions": "Top actions",
    "no_drilldown_data": "No drilldown data available.",
    "next_actions": "Next actions",
    "placeholder_actions": "Placeholder actions",
    "no_missing_placeholder": "No missing task/test placeholder.",
    "risk_details": "Risk details",
    "no_active_risks": "No active risks.",
    "linked_work_items": "Linked work items",
    "no_linked_work_items": "No linked work items yet.",
    "empty_state": "Empty state",
    "no_traceability_warnings": "No traceability warnings.",
    "PASS": "PASS",
    "FAIL": "FAIL",
    "drilldown": "Drilldown",
    "Create task placeholder": "Create task placeholder",
    "Create test placeholder": "Create test placeholder",
    "Convert placeholder": "Convert placeholder",
    "Raw JSON debug": "Raw JSON debug",
    "None.": "None.",
    "None": "None",
    "task": "Task",
    "test": "Test",
    "Open": "Open",
    "Done": "Done"
  },
  vi: {
    "workspace_back_btn": "Quay lại Dashboard chính",
    "Low": "Thấp",
    "Medium": "Trung bình",
    "High": "Cao",
    "Critical": "Nghiêm trọng",
    "Safe": "An toàn",
    "Not Safe": "Không an toàn",
    "PASS": "ĐẠT",
    "FAIL": "KHÔNG ĐẠT",
    "drilldown": "Xem chi tiết",
    "Create task placeholder": "Tạo nhiệm vụ giữ chỗ",
    "Create test placeholder": "Tạo kiểm thử giữ chỗ",
    "Convert placeholder": "Chuyển đổi giữ chỗ",
    "Raw JSON debug": "Dữ liệu JSON thô (Debug)",
    "None.": "Không có.",
    "None": "Không có",
    "task": "Nhiệm vụ",
    "test": "Kiểm thử",
    "Open": "Mở",
    "Done": "Hoàn thành",
    // Brand & Sidebar
    "sidebar_title": "DevFlow Guard",
    "sidebar_subtitle": "Hệ điều hành Quản lý rủi ro",
    "sidebar_workspace_context": "Bối cảnh Không gian làm việc",
    "sidebar_project": "Dự án",
    "sidebar_release": "Bản phát hành",
    "sidebar_create_workspace": "Tạo Không gian làm việc",
    "sidebar_create_project_btn": "Tạo dự án",
    "sidebar_create_release_btn": "Tạo bản phát hành",
    "sidebar_local_data": "Dữ liệu cục bộ",
    "local_data_loading": "Đang tải thống kê dữ liệu…",
    "local_data_backup": "Tải bản sao lưu (.db)",
    "local_data_reset": "Xoá toàn bộ dữ liệu",
    "guide_badge": "Hướng dẫn",
    "guide_summary": "Cách sử dụng DevFlow Guard",
    "guide_step1_desc": "<strong>Tạo dữ liệu:</strong> nhấn <em>Initialize Local Sample Workspace</em> ở trên để tạo dự án, phiên bản và yêu cầu mẫu.",
    "guide_step2_desc": "<strong>Chọn ngữ cảnh:</strong> chọn <em>Dự án</em> và <em>Phiên bản</em> ở thanh bên trái (Workspace Context).",
    "guide_step3_desc": "<strong>Đi theo lộ trình:</strong> thực hiện sáu bước bên dưới — Bắt đầu → Tài liệu → Truy vết → Tác động → Cổng duyệt → Báo cáo.",
    "guide_step4_desc": "<strong>Quét tài liệu:</strong> ở Bước 2, tải lên file SQL / log / test / OpenAPI để chạy kiểm tra rủi ro.",
    "guide_step5_desc": "<strong>Xem lịch sử:</strong> mở <em>Operations Workspace</em> (thanh bên) để xem ghi chú cục bộ và dòng thời gian kiểm toán.",
    "guide_note_desc": "Mọi thứ chạy cục bộ trên SQLite — không cần internet hay đăng nhập. Đóng bảng này bằng mũi tên; nó sẽ thu gọn trong phiên làm việc.",
    "topbar_desc": "Một màn hình tập trung cho rủi ro phát hành, truy vết, bằng chứng và lịch sử vận hành.",
    "cmd_kicker": "Lệnh hôm nay",
    "cmd_title": "Bắt đầu với cổng phát hành, rồi đẩy bằng chứng tiến lên.",
    "cmd_desc": "Dùng thao tác chính để khởi tạo hoặc làm mới workspace, rồi đi theo lộ trình sáu bước khi checkpoint trước đã rõ ràng.",
    "sidebar_flow_label": "Quy trình đề xuất",
    "sidebar_workspace_link": "Mở Không gian vận hành",
    "sidebar_why_title": "Tại sao điều này quan trọng",
    "sidebar_why_desc": "Jira theo dõi công việc. Hệ thống này kiểm tra rủi ro phát hành, lỗ hổng bảo mật và độ an toàn.",
    
    // Topbar & Auth
    "topbar_eyebrow": "Hệ điều hành Quản trị DevFlow",
    "topbar_title": "Trung tâm Kiểm soát Tuân thủ Phát hành",
    "topbar_logout": "Đăng xuất",
    
    // Login overlay
    "login_title": "Đăng nhập vào DevFlow",
    "login_email": "Địa chỉ email",
    "login_password": "Mật khẩu",
    "login_submit": "Đăng nhập",
    "login_toggle_register": "Chưa có tài khoản? <span class=\"link-highlight\">Đăng ký</span>",
    "register_title": "Tạo tài khoản mới",
    "register_submit": "Đăng ký tài khoản",
    "register_toggle_login": "Đã có tài khoản? <span class=\"link-highlight\">Đăng nhập</span>",
    
    // Stepper
    "step_1": "Bắt đầu",
    "step_2": "Tải hiện vật",
    "step_3": "Truy vết",
    "step_4": "Tác động",
    "step_5": "Cổng duyệt",
    "step_6": "Báo cáo",
    
    // Metrics Grid
    "metric_step": "Bước hiện tại",
    "metric_blockers": "Trở ngại chặn",
    "metric_traceability": "Độ truy vết",
    "metric_mode": "Chế độ",
    "metric_mode_val": "Ngoại tuyến",
    
    // Step Panels
    "step1_title": "Khởi tạo Không gian làm việc & Kiểm soát Quản trị",
    "step1_desc": "Chuẩn bị dữ liệu workspace có kiểm soát, sau đó chuyển sang upload artifact.",
    "step1_btn_init": "Khởi tạo workspace mẫu local",
    "step1_btn_refresh": "Làm mới Dashboard",
    "step1_btn_today": "Xem trọng tâm hôm nay",
    "step1_btn_verify": "Xác thực tính toàn vẹn Audit",
    "step1_btn_next": "Hướng dẫn bước tiếp theo",
    
    "step2_title": "Tải lên và Quét các hiện vật phát hành",
    "step2_desc": "Sử dụng các file mẫu trong ví dụ hoặc file dự án thực tế.",
    "step2_btn_sql": "Quét SQL",
    "step2_btn_logs": "Quét Logs",
    "step2_btn_tests": "Quét Tests",
    "step2_btn_api": "Quét API Diff",
    "step2_btn_review": "Xem kết quả rà soát",
    
    "step3_title": "Ma trận Truy vết & Quản trị phát hành",
    "step3_desc": "Kiểm tra liên kết, phân tích hồ sơ rủi ro và rà soát chính sách phục hồi dữ liệu.",
    "step3_btn_trace": "Chạy Truy vết",
    "step3_btn_risk": "Quét rủi ro",
    
    "step4_title": "Tác động thay đổi yêu cầu",
    "step4_desc": "Ghi nhận thay đổi yêu cầu và phân tích các hạng mục bị ảnh hưởng.",
    "step4_btn_record": "Ghi nhận thay đổi",
    "step4_btn_impact": "Chạy phân tích tác động",
    
    "step5_title": "Cổng duyệt phát hành nâng cao",
    "step5_desc": "Phân tích đường dẫn mã nguồn, cấu hình môi trường và mức độ sẵn sàng cuối cùng.",
    "step5_btn_code": "Rủi ro Code",
    "step5_btn_env": "Quét môi trường",
    "step5_btn_ready": "Độ sẵn sàng",
    "step5_btn_fix": "Sửa lỗi chặn Demo",
    
    "step6_title": "Báo cáo bằng chứng & Phát hành Production",
    "step6_desc": "Xuất gói bằng chứng tuân thủ, kiểm tra chữ ký số và phân phối phát hành.",
    "step6_btn_prev": "Xem trước bằng chứng",
    "step6_btn_download": "Tải xuống bằng chứng",
    "step6_btn_notes": "Ghi chú phát hành",
    
    // Dynamic alerts
    "toast_session_checking": "Đang kiểm tra phiên làm việc...",
    "toast_logged_out": "Đã đăng xuất",
    "toast_logged_in": "Đăng nhập với vai trò",
    
    // Dynamic Renderers
    "no_traceability_rows_yet": "Chưa có ma trận truy vết nào.",
    "tasks": "Nhiệm vụ",
    "apis": "Giao diện API",
    "tests": "Kiểm thử",
    "bugs": "Lỗi phần mềm",
    "commits": "Lần Commit",
    "no_readiness_result_yet": "Chưa có kết quả sẵn sàng.",
    "readiness_score": "Điểm sẵn sàng phát hành",
    "blockers_title": "Yếu tố chặn",
    "warnings_title": "Cảnh báo",
    "recommendations_title": "Đề xuất khắc phục",
    "no_guard_findings_yet": "Chưa có phát hiện rà soát nào.",
    "finding": "Phát hiện",
    "blocking": "Đang chặn",
    "non_blocking": "Không chặn",
    "no_active_requirements": "Không có yêu cầu nghiệp vụ hoạt động để xem xét.",
    "score": "Điểm số",
    "risks": "Rủi ro",
    "priority": "Độ ưu tiên",
    "Fix hints": "Gợi ý khắc phục",
    "release_risk_by_requirement": "Rủi ro phát hành theo Yêu cầu nghiệp vụ",
    "risks_plural": "rủi ro",
    "top_actions": "Hành động ưu tiên",
    "no_drilldown_data": "Không có dữ liệu chi tiết.",
    "next_actions": "Hành động tiếp theo",
    "placeholder_actions": "Hành động giữ chỗ (Placeholder)",
    "no_missing_placeholder": "Không thiếu nhiệm vụ/kiểm thử giữ chỗ nào.",
    "risk_details": "Chi tiết rủi ro",
    "no_active_risks": "Không có rủi ro hoạt động.",
    "linked_work_items": "Các mục công việc liên kết",
    "no_linked_work_items": "Chưa có mục công việc liên kết nào.",
    "empty_state": "Trạng thái trống",
    "no_traceability_warnings": "Không có cảnh báo truy vết nào."
  }
};

let currentLang = localStorage.getItem("devflow_lang") || "vi";

function t(key) {
  return TRANSLATIONS[currentLang][key] || key;
}

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("devflow_lang", lang);
  applyTranslations();
}

function toggleLanguage() {
  const nextLang = currentLang === "en" ? "vi" : "en";
  setLanguage(nextLang);
}

// Auto-translated phrase dictionaries for text without data-i18n attributes.
const PHRASE_MAP = {
  "Production control room": "Phòng điều khiển vận hành",
  "Run release governance, evidence checks, traceability review, and audit history from one operator workspace.": "Chạy quản trị phát hành, kiểm tra bằng chứng, rà soát truy vết và lịch sử kiểm toán từ một không gian vận hành.",
  "governance steps": "bước quản trị",
  "Live": "Trực tiếp",
  "risk and evidence gates": "cổng rủi ro và bằng chứng",
  "Audit": "Kiểm toán",
  "history ledger visible": "hiển thị sổ lịch sử",
  "Protected API session required before operational actions.": "Cần phiên API được bảo vệ trước khi thao tác vận hành.",
  "Sign in with a real account. Local sample credentials are available only for isolated QA mode.": "Đăng nhập bằng tài khoản thật. Thông tin mẫu cục bộ chỉ dùng cho chế độ QA riêng biệt.",
  "Use local sample admin": "Dùng admin mẫu cục bộ",
  "Sample credentials only seed the isolated local QA account.": "Thông tin mẫu chỉ tạo tài khoản QA cục bộ riêng biệt.",
  "Local QA auth": "Xác thực QA cục bộ",
  "Not logged in": "Chưa đăng nhập",
  "Initialize sample": "Khởi tạo mẫu",
  "Upload artifacts": "Tải tài liệu lên",
  "Traceability": "Truy vết",
  "Impact": "Tác động",
  "Release gate": "Cổng phát hành",
  "Evidence": "Bằng chứng",
  "View history timeline": "Xem dòng thời gian lịch sử",
  "Local database": "Cơ sở dữ liệu cục bộ",
  "Review history": "Xem lịch sử",
  "Dashboard": "Bảng điều khiển",
  "Today focus": "Trọng tâm hôm nay",
  "Audit integrity": "Kiểm tra toàn vẹn",
  "Workspace": "Không gian làm việc",
  "Start": "Bắt đầu",
  "Artifacts": "Tài liệu",
  "Gate": "Cổng duyệt",
  "Report": "Báo cáo",
  "From guards/readiness": "Từ guard/sẵn sàng",
  "Not run": "Chưa chạy",
  "Requirement links": "Liên kết yêu cầu",
  "Runs locally": "Chạy cục bộ",
  "Step 1": "Bước 1",
  "Step 2": "Bước 2",
  "Step 3": "Bước 3",
  "Step 4": "Bước 4",
  "Step 5": "Bước 5",
  "Step 6": "Bước 6",
  "SQL Migration": "Di trú SQL",
  "Find destructive database changes.": "Tìm thay đổi CSDL mang tính phá hủy.",
  "Logs": "Nhật ký",
  "Find errors, exceptions, timeouts.": "Tìm lỗi, ngoại lệ, hết thời gian.",
  "Tests": "Kiểm thử",
  "Find failed tests and errors.": "Tìm test thất bại và lỗi.",
  "API Diff": "So sánh API",
  "Find removed OpenAPI paths.": "Tìm các đường dẫn OpenAPI bị xóa.",
  "🔬 Core Analysis & Risk Audit": "🔬 Phân tích cốt lõi & Kiểm toán rủi ro",
  "Analyze traceability matrix, scan for bugs, and view requirements risk.": "Phân tích ma trận truy vết, quét lỗi và xem rủi ro yêu cầu.",
  "Bug Patterns": "Mẫu lỗi",
  "Risk Dashboard by Requirement": "Bảng rủi ro theo yêu cầu",
  "📈 Planning & Analytics Control": "📈 Điều khiển Lập kế hoạch & Phân tích",
  "View historical metrics, burndown rates, prevention logs, and timelines.": "Xem chỉ số lịch sử, tốc độ burndown, nhật ký phòng ngừa và dòng thời gian.",
  "Snapshot Analytics": "Phân tích ảnh chụp",
  "Risk Delta": "Chênh lệch rủi ro",
  "Recurring Risk Trends": "Xu hướng rủi ro lặp lại",
  "Risk Prevention Backlog": "Tồn đọng phòng ngừa rủi ro",
  "Next Release Readiness": "Sẵn sàng phát hành kế tiếp",
  "Prevention Execution Board": "Bảng thực thi phòng ngừa",
  "Overdue Escalations": "Leo thang quá hạn",
  "Prevention Burndown": "Burndown phòng ngừa",
  "Owner Workload Balance": "Cân bằng khối lượng chủ sở hữu",
  "Prevention Calendar": "Lịch phòng ngừa",
  "Readiness Timeline": "Dòng thời gian sẵn sàng",
  "Scenario Planning": "Lập kế hoạch kịch bản",
  "Plan Recommendation": "Đề xuất kế hoạch",
  "Scope Audit": "Kiểm toán phạm vi",
  "🗄️ Database & Migration Governance": "🗄️ Quản trị CSDL & Di trú",
  "Verify local schema health, review checklist protocols, and check migrations.": "Kiểm tra sức khỏe schema cục bộ, rà soát quy trình và kiểm tra di trú.",
  "Migration Notes": "Ghi chú di trú",
  "Migration Check": "Kiểm tra di trú",
  "Upgrade Safety": "An toàn nâng cấp",
  "Dry-run SQL": "Chạy thử SQL",
  "Backup Checklist": "Danh mục sao lưu",
  "🔐 Signature & Cryptography Gates": "🔐 Cổng Chữ ký & Mật mã",
  "Verify package integrity adapters and run local public key dry-run decode.": "Kiểm tra adapter toàn vẹn gói và chạy thử giải mã khóa công khai cục bộ.",
  "Verification Policy": "Chính sách xác minh",
  "Signature Adapters": "Adapter chữ ký",
  "Adapter Contracts": "Hợp đồng adapter",
  "Sample Fixtures": "Fixture mẫu",
  "Public-key Verifier": "Bộ xác minh khóa công khai",
  "Real Verify Dry-run": "Chạy thử xác minh thật",
  "Verifier Evidence": "Bằng chứng bộ xác minh",
  "Verified Gate": "Cổng đã xác minh",
  "Hardened Evidence Gate": "Cổng bằng chứng gia cố",
  "Verifier Profiles": "Hồ sơ bộ xác minh",
  "Policy Presets": "Cấu hình chính sách sẵn",
  "Final Signed Evidence": "Bằng chứng ký cuối cùng",
  "E2E Governance Rehearsal": "Diễn tập quản trị E2E",
  "Adapter Dry-run": "Chạy thử adapter",
  "📋 Releases & Approval History": "📋 Phát hành & Lịch sử phê duyệt",
  "Inspect final approval signatures, review retrospectives, and track audit history.": "Kiểm tra chữ ký phê duyệt cuối, xem hồi cứu và theo dõi lịch sử kiểm toán.",
  "Export Release Review Checklist": "Xuất danh mục rà soát phát hành",
  "Release Review Completion": "Hoàn tất rà soát phát hành",
  "Final Sign-off Snapshot": "Ảnh chụp phê duyệt cuối",
  "Approval Records": "Hồ sơ phê duyệt",
  "Compare Approvals": "So sánh phê duyệt",
  "Retrospectives": "Hồi cứu",
  "Learning Loop": "Vòng học hỏi",
  "Governance Readiness": "Sẵn sàng quản trị",
  "🛠️ Developer Rehearsals & Milestone Verification (v10 - v12)": "🛠️ Diễn tập Lập trình viên & Xác minh Cột mốc (v10 - v12)",
  "Inspect runbooks and build package assets for milestone versions (v10.0 to v12.0).": "Kiểm tra runbook và tạo tài nguyên gói cho các phiên bản cột mốc (v10.0 đến v12.0).",
  "Stable Milestone": "Cột mốc ổn định",
  "Installer Checklist": "Danh mục cài đặt",
  "Quick Requirements": "Yêu cầu nhanh",
  "Requirement Management": "Quản lý yêu cầu",
  "Create and review requirements for the selected project.": "Tạo và xem yêu cầu cho dự án đã chọn.",
  "Key": "Khóa",
  "Title": "Tiêu đề",
  "Priority": "Ưu tiên",
  "Status": "Trạng thái",
  "Create": "Tạo",
  "Refresh Requirements": "Làm mới yêu cầu",
  "Refresh Traceability": "Làm mới truy vết",
  "Requirement key": "Khóa yêu cầu",
  "Old requirement": "Yêu cầu cũ",
  "New requirement": "Yêu cầu mới",
  "Changed files": "Tệp thay đổi",
  "Environment config": "Cấu hình môi trường",
  "Quick Work Items": "Hạng mục công việc nhanh",
  "Task / Test / Bug Management": "Quản lý Task / Test / Bug",
  "Create and update work items for the selected project.": "Tạo và cập nhật hạng mục công việc cho dự án đã chọn.",
  "Kind": "Loại",
  "Severity": "Mức độ",
  "Requirement": "Yêu cầu",
  "Filter by requirement": "Lọc theo yêu cầu",
  "Refresh Work Items": "Làm mới hạng mục",
  "Goal Completion": "Hoàn thành mục tiêu",
  "Git, Requirement Diff, Deep API, Workload": "Git, So sánh yêu cầu, API sâu, Khối lượng",
  "Extra deterministic project-risk checks.": "Kiểm tra rủi ro dự án bổ sung, xác định.",
  "Git/PR CSV": "CSV Git/PR",
  "Old requirement CSV": "CSV yêu cầu cũ",
  "New requirement CSV": "CSV yêu cầu mới",
  "OpenAPI before/after JSON": "JSON OpenAPI trước/sau",
  "Import Git": "Nhập Git",
  "Compare Req": "So sánh yêu cầu",
  "Deep API": "API sâu",
  "Workload": "Khối lượng",
  "📋 Core Evidence Preview & Export": "📋 Xem trước & Xuất bằng chứng cốt lõi",
  "Preview release evidence report, compile notes, and review operators sign-off.": "Xem trước báo cáo bằng chứng phát hành, biên soạn ghi chú và rà soát phê duyệt.",
  "Final Sign-off": "Phê duyệt cuối",
  "Operator Sign-off": "Phê duyệt vận hành",
  "Evidence Manifest": "Bảng kê bằng chứng",
  "Bundle Integrity": "Toàn vẹn gói",
  "API Docs": "Tài liệu API",
  "🗄️ Database & Migration Handoff": "🗄️ Bàn giao CSDL & Di trú",
  "Audit SQL migration plans, dry-run transactions, and run deployment upgrades.": "Kiểm toán kế hoạch di trú SQL, chạy thử giao dịch và nâng cấp triển khai.",
  "Apply Assistant": "Trợ lý áp dụng",
  "Post-migration Verify": "Xác minh sau di trú",
  "Safe Copy Apply": "Áp dụng sao chép an toàn",
  "Rollback Drill": "Diễn tập hoàn tác",
  "Real Migration Gate": "Cổng di trú thật",
  "Production Checklist": "Danh mục sản xuất",
  "Upgrade Runbook": "Sổ tay nâng cấp",
  "Rehearsal Report": "Báo cáo diễn tập",
  "Operator Handoff": "Bàn giao vận hành",
  "🔐 Cryptographic Signing Handoff": "🔐 Bàn giao Ký mật mã",
  "Digitally sign evidence bundles, verify cryptographic checksums, and confirm handoffs.": "Ký số các gói bằng chứng, xác minh checksum mật mã và xác nhận bàn giao.",
  "Signing Readiness": "Sẵn sàng ký",
  "Timestamp Handoff": "Bàn giao dấu thời gian",
  "Timestamp Integrity": "Toàn vẹn dấu thời gian",
  "Signed Payload Import": "Nhập payload đã ký",
  "Timestamp Token Evidence": "Bằng chứng token thời gian",
  "Signed+Timestamp Verify": "Xác minh ký+thời gian",
  "Verifier Evidence Records": "Hồ sơ bằng chứng xác minh",
  "Signed Artifact Package": "Gói tài liệu đã ký",
  "Signed Artifacts": "Tài liệu đã ký",
  "Final Operator Approval": "Phê duyệt vận hành cuối",
  "📈 Prevention & Risk Analytics": "📈 Phân tích Phòng ngừa & Rủi ro",
  "Track remaining backlog items, recurring trends, escalations, calendar.": "Theo dõi tồn đọng còn lại, xu hướng lặp, leo thang, lịch.",
  "New Retrospective": "Hồi cứu mới",
  "Prevention Checklist": "Danh mục phòng ngừa",
  "Inspect runbooks and release packages for historical versions (v10.0 to v12.0).": "Kiểm tra runbook và gói phát hành cho các phiên bản lịch sử (v10.0 đến v12.0).",
  "Context": "Ngữ cảnh",
  "OS Panel": "Bảng OS",
  "Dashboard and today focus.": "Bảng điều khiển và trọng tâm hôm nay.",
  "Initialize a local sample workspace or load existing release data to begin.": "Khởi tạo không gian mẫu cục bộ hoặc tải dữ liệu phát hành hiện có để bắt đầu.",
  "Risk": "Rủi ro",
  "Risk / Trace / Activity": "Rủi ro / Truy vết / Hoạt động",
  "Findings appear here.": "Kết quả hiển thị ở đây.",
  "No findings yet.": "Chưa có kết quả.",
  "Release": "Phát hành",
  "Readiness / Evidence": "Sẵn sàng / Bằng chứng",
  "Gate and evidence report.": "Báo cáo cổng và bằng chứng.",
  "No readiness yet.": "Chưa sẵn sàng.",
  "History": "Lịch sử",
  "Operational Timeline": "Dòng thời gian vận hành",
  "Activity, signoff, and retrospective trail.": "Nhật ký hoạt động, phê duyệt và hồi cứu.",
  "Refresh": "Làm mới",
  "Return to Governance Dashboard": "Quay lại Bảng quản trị",
  "Browser-local state": "Trạng thái cục bộ trình duyệt"
};
const VNN_SUFFIX = {
  "Walkthrough": "Hướng dẫn",
  "Demo Script": "Kịch bản demo",
  "Deployment Guide": "Hướng dẫn triển khai",
  "Quickstart": "Bắt đầu nhanh",
  "First-run Wizard": "Trình hướng dẫn lần đầu",
  "Reset Safety": "An toàn đặt lại",
  "Reset Plan": "Kế hoạch đặt lại",
  "First-run Package": "Gói chạy lần đầu",
  "Demo Profiles": "Hồ sơ demo",
  "Profile Plan": "Kế hoạch hồ sơ",
  "Tutorial Progress": "Tiến độ hướng dẫn",
  "Mark Profile Done": "Đánh dấu hồ sơ xong",
  "Tutorial Package": "Gói hướng dẫn",
  "Sample Builder": "Trình tạo mẫu",
  "Build Sample": "Tạo mẫu",
  "Completion Badge": "Huy hiệu hoàn thành",
  "Builder Package": "Gói trình tạo",
  "Execute Reset": "Thực thi đặt lại",
  "Reset Package": "Gói đặt lại",
  "Rollback Snapshot": "Ảnh chụp hoàn tác",
  "Reset With Audit": "Đặt lại kèm kiểm toán",
  "Audit Trail": "Nhật ký kiểm toán",
  "Rollback Package": "Gói hoàn tác",
  "Import Rehearsal": "Diễn tập nhập",
  "Restore Checklist": "Danh mục khôi phục",
  "Restore Package": "Gói khôi phục",
  "Restore Plan": "Kế hoạch khôi phục",
  "Execute Restore": "Thực thi khôi phục",
  "Restore Audit": "Kiểm toán khôi phục",
  "Conflict Report": "Báo cáo xung đột",
  "Digest Plan": "Kế hoạch digest",
  "Digest Audit": "Kiểm toán digest",
  "Recovery Stability": "Ổn định phục hồi",
  "Recovery Runbook": "Sổ tay phục hồi",
  "Recovery Package": "Gói phục hồi",
  "Recovery UX": "Trải nghiệm phục hồi",
  "Export Fixture": "Xuất fixture",
  "Import Fixture": "Nhập fixture",
  "Fixture Package": "Gói fixture",
  "Fixture Validation": "Kiểm định fixture",
  "Walkthrough Package": "Gói hướng dẫn",
  "Smoke Test": "Kiểm tra khói",
  "Post-Restore Verify": "Xác minh sau khôi phục",
  "Smoke Package": "Gói kiểm tra khói",
  "Evidence Bundle": "Gói bằng chứng",
  "Demo Handoff": "Bàn giao demo",
  "Handoff Package": "Gói bàn giao",
  "RC Freeze": "Đóng băng RC",
  "Acceptance": "Nghiệm thu",
  "RC Package": "Gói RC",
  "Packaging Cleanup": "Dọn đóng gói",
  "Install Verify": "Xác minh cài đặt",
  "Final Package": "Gói cuối",
  "Archive Manifest": "Bảng kê lưu trữ",
  "Release Notes": "Ghi chú phát hành",
  "Release Package": "Gói phát hành",
  "Checksum Handoff": "Bàn giao checksum",
  "Checksum Package": "Gói checksum",
  "Release Tag": "Thẻ phát hành",
  "Portfolio Script": "Kịch bản portfolio",
  "Baseline Freeze": "Đóng băng nền",
  "Deploy Checklist": "Danh mục triển khai",
  "Deploy Package": "Gói triển khai"
};


const _origTextStore = new WeakMap();
const _SKIP_TAGS = new Set(["SCRIPT", "STYLE", "TEXTAREA", "CODE", "PRE", "OPTION", "SELECT"]);

function _translatePhrase(en) {
  if (Object.prototype.hasOwnProperty.call(PHRASE_MAP, en)) return PHRASE_MAP[en];
  const m = en.match(/^(v\d+\.\d+)\s+(.+)$/);
  if (m && Object.prototype.hasOwnProperty.call(VNN_SUFFIX, m[2])) return m[1] + " " + VNN_SUFFIX[m[2]];
  return null;
}

// Translate visible text that is not wrapped in a [data-i18n] element.
// Original English is captured per text node so switching back to EN restores it.
function translateTextNodes() {
  const toVi = currentLang === "vi";
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    const parent = node.parentElement;
    if (!parent || _SKIP_TAGS.has(parent.tagName) || parent.closest("[data-i18n]")) continue;
    if (!_origTextStore.has(node)) {
      const trimmed = node.textContent.trim();
      if (!trimmed || !/[A-Za-z]/.test(trimmed) || _translatePhrase(trimmed) === null) continue;
      _origTextStore.set(node, node.textContent);
    }
    const original = _origTextStore.get(node);
    const trimmed = original.trim();
    if (toVi) {
      const vi = _translatePhrase(trimmed);
      node.textContent = vi !== null ? original.replace(trimmed, vi) : original;
    } else {
      node.textContent = original;
    }
  }
}

function applyTranslations() {
  // Update language switcher text
  const langBtn = document.getElementById("langBtn");
  if (langBtn) {
    langBtn.textContent = currentLang === "en" ? "🌐 EN" : "🌐 VI";
  }
  
  // Translate all elements with data-i18n attribute
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    const translation = TRANSLATIONS[currentLang][key];
    if (translation) {
      if (key.includes("toggle") || key.includes("desc") || key.includes("why")) {
        el.innerHTML = translation; // Allow HTML link elements to parse
      } else {
        el.textContent = translation;
      }
    }
  });

  // Translate placeholders if any
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    const translation = TRANSLATIONS[currentLang][key];
    if (translation) {
      el.placeholder = translation;
    }
  });

  // Stepper labels update dynamically
  for (let i = 1; i <= 6; i++) {
    const span = document.querySelector(`#stepBtn${i} span`);
    if (span) {
      const translation = TRANSLATIONS[currentLang][`step_${i}`];
      if (translation) span.textContent = translation;
    }
  }

  // Set default dynamic UI labels if stepper is updated
  if (typeof goStep === "function" && typeof currentStep !== "undefined") {
    const textEl = document.getElementById("metricStepText");
    if (textEl) {
      const descriptions = [
        "",
        t("step1_desc"),
        t("step2_desc"),
        t("step3_desc"),
        t("step4_desc"),
        t("step5_desc"),
        t("step6_desc")
      ];
      textEl.textContent = descriptions[currentStep];
    }
  }
  translateTextNodes();
}

// Auto apply on load
window.addEventListener("DOMContentLoaded", () => {
  applyTranslations();
});
