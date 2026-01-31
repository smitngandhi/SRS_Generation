document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("srsForm");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        // ---------- helpers ----------
        const getCheckedValues = (name) =>
            Array.from(document.querySelectorAll(`input[name="${name}"]:checked`))
                .map(el => el.value);

        const splitToArray = (value) =>
            value
                ? value.split(/[\n,]/).map(v => v.trim()).filter(Boolean)
                : [];

        // ---------- Target Users ----------
        let targetUsers = getCheckedValues("target_users");
        if (targetUsers.includes("Other")) {
            const customUser = document.getElementById("target_users_custom")?.value;
            if (customUser) targetUsers.push(customUser);
        }

        // ---------- Domain ----------
        let domain = formData.get("domain");
        if (domain === "Other") {
            domain = document.getElementById("domain_custom")?.value;
        }

        // ---------- Compliance ----------
        let compliance = getCheckedValues("compliance_requirements");
        if (compliance.includes("Other")) {
            const customCompliance =
                document.getElementById("compliance_custom")?.value;
            if (customCompliance) compliance.push(customCompliance);
        }

        // ---------- Core Features ----------
        const coreFeatures = splitToArray(formData.get("core_features"));

        // ---------- Booleans ----------
        const authenticationRequired =
            formData.get("authentication_required") === "true";
        const sensitiveDataHandling =
            formData.get("sensitive_data_handling") === "true";

        // ---------- FINAL PAYLOAD (MATCHES PYDANTIC) ----------
        const payload = {
            project_identity: {
                project_name: formData.get("project_name"),
                problem_statement: formData.get("problem_statement"),
                target_users: targetUsers
            },

            system_context: {
                application_type: formData.get("application_type"),
                domain: domain
            },

            functional_scope: {
                core_features: coreFeatures,
                primary_user_flow:
                    formData.get("primary_user_flow")?.trim() || null
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
                preferred_backend:
                    formData.get("preferred_backend")?.trim() || null,
                database_preference:
                    formData.get("database_preference")?.trim() || null,
                deployment_preference:
                    formData.get("deployment_preference")?.trim() || null
            },

            output_control: {
                srs_detail_level: formData.get("srs_detail_level")
            }
        };

        console.log("SRS Payload:", payload);

        // ---------- SEND TO BACKEND ----------
        try {
            const response = await fetch("/generate_introduction", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const err = await response.text();
                throw new Error(err);
            }

            const result = await response.json();
            console.log("Server response:", result);
            alert("SRS generated successfully!");

        } catch (error) {
            console.error("Submission error:", error);
            alert("Failed to generate SRS");
        }
    });
});
