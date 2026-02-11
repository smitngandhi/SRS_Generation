document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("srsForm");

    // Show/hide custom input for Target Users
    const targetUsersOtherCheck = document.getElementById("target_users_other_check");
    const targetUsersCustomInput = document.getElementById("target_users_custom");

    if (targetUsersOtherCheck) {
        targetUsersOtherCheck.addEventListener("change", (e) => {
            if (e.target.checked) {
                targetUsersCustomInput.style.display = "block";
            } else {
                targetUsersCustomInput.style.display = "none";
                targetUsersCustomInput.value = "";
            }
        });
    }

    // Show/hide custom input for Domain
    const domainSelect = document.getElementById("domain");
    const domainCustomInput = document.getElementById("domain_custom");

    if (domainSelect) {
        domainSelect.addEventListener("change", (e) => {
            // Domain info display is now handled by domain-data.js
            // Only show/hide custom input here
            if (e.target.value === "Other") {
                domainCustomInput.style.display = "block";
            } else {
                domainCustomInput.style.display = "none";
                domainCustomInput.value = "";
            }
        });
    }

    // Show/hide custom input for Compliance
    const complianceOtherCheck = document.getElementById("compliance_other_check");
    const complianceCustomInput = document.getElementById("compliance_custom");

    if (complianceOtherCheck) {
        complianceOtherCheck.addEventListener("change", (e) => {
            if (e.target.checked) {
                complianceCustomInput.style.display = "block";
            } else {
                complianceCustomInput.style.display = "none";
                complianceCustomInput.value = "";
            }
        });
    }

    // Form submission handler
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        // ---------- Helper Functions ----------
        const getCheckedValues = (name) =>
            Array.from(document.querySelectorAll(`input[name="${name}"]:checked`))
                .map(el => el.value)
                .filter(val => val !== "Other"); // Exclude "Other" from the array

        const splitToArray = (value) =>
            value
                ? value.split(/[\n,]/).map(v => v.trim()).filter(Boolean)
                : [];

        // ---------- Target Users ----------
        let targetUsers = getCheckedValues("target_users");
        const customUser = document.getElementById("target_users_custom")?.value.trim();
        if (customUser) {
            targetUsers.push(customUser);
        }

        // Validate at least one target user
        if (targetUsers.length === 0) {
            alert("Please select at least one target user");
            return;
        }

        // ---------- Domain ----------
        let domain = formData.get("domain");
        
        // If "Other" is selected, check if custom domain is provided
        // If no custom domain, use "Other" as the domain value
        if (domain === "Other") {
            const customDomain = document.getElementById("domain_custom")?.value.trim();
            if (customDomain) {
                domain = customDomain; // Use custom domain name if provided
            }
            // Otherwise keep domain as "Other" - it's valid
        }

        // ---------- Compliance ----------
        let compliance = getCheckedValues("compliance_requirements");
        const customCompliance = document.getElementById("compliance_custom")?.value.trim();
        if (customCompliance) {
            compliance.push(customCompliance);
        }

        // If no compliance requirements selected, use empty array
        if (compliance.length === 0) {
            compliance = [];
        }

        // ---------- Authors ----------
        const author = splitToArray(formData.get("author"));
        if (author.length === 0) {
            alert("Please provide at least one author name");
            return;
        }

        // ---------- Core Features ----------
        const coreFeatures = splitToArray(formData.get("core_features"));
        if (coreFeatures.length === 0) {
            alert("Please provide at least one core feature");
            return;
        }

        // ---------- Booleans ----------
        const authenticationRequired = formData.get("authentication_required") === "true";
        const sensitiveDataHandling = formData.get("sensitive_data_handling") === "true";

        // ---------- FINAL PAYLOAD ----------
        const payload = {
            project_identity: {
                project_name: formData.get("project_name").trim(),
                author: author,
                organization: formData.get("organization").trim(),
                problem_statement: formData.get("problem_statement").trim(),
                target_users: targetUsers
            },

            system_context: {
                application_type: formData.get("application_type"),
                domain: domain
            },

            functional_scope: {
                core_features: coreFeatures,
                primary_user_flow: formData.get("primary_user_flow")?.trim() || null
            },

            non_functional_requirements: {
                expected_user_scale: formData.get("expected_user_scale"),
                performance_expectation: formData.get("performance_expectation")
            },

            security_and_compliance: {
                authentication_required: authenticationRequired,
                sensitive_data_handling: sensitiveDataHandling,
                compliance_requirements: compliance
            },

            technical_preferences: {
                preferred_backend: formData.get("preferred_backend")?.trim() || null,
                database_preference: formData.get("database_preference")?.trim() || null,
                deployment_preference: formData.get("deployment_preference")?.trim() || null
            },

            output_control: {
                srs_detail_level: formData.get("srs_detail_level")
            }
        };

        console.log("SRS Payload:", JSON.stringify(payload, null, 2));

        // ---------- SEND TO BACKEND ----------
        try {
            const response = await fetch("/generate_srs", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Server error:", errorText);
                throw new Error(`Server returned ${response.status}: ${errorText}`);
            }

            const result = await response.json();
            console.log("Server response:", result);
            alert("SRS generated successfully!");

        } catch (error) {
            console.error("Submission error:", error);
            alert(`Failed to generate SRS: ${error.message}`);
        }
    });
});