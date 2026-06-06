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
    "step1_desc": "Deploy compliance parameters, register workspace tracks, and seed admin parameters.",
    "step1_btn_init": "Initialize Workspace (Seed Data)",
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
    "step1_desc": "Thiết lập các tham số tuân thủ, đăng ký luồng làm việc và thiết lập cấu hình quản trị.",
    "step1_btn_init": "Khởi tạo Workspace (Dữ liệu Seed)",
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

let currentLang = localStorage.getItem("devflow_lang") || "en";

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
}

// Auto apply on load
window.addEventListener("DOMContentLoaded", () => {
  applyTranslations();
});
