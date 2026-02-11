// Domain-specific data for SRS generation
const domainData = {
    "Healthcare": {
        title: "Healthcare & Medical Devices",
        standards: ["IEC 62304", "FDA 21 CFR Part 820", "ISO 13485", "ISO 14971", "HIPAA", "HL7", "FHIR", "DICOM"],
        sections: [
            "Introduction & Medical Device Classification",
            "Software Development Plan",
            "Software Requirements Specification",
            "Software Architecture",
            "Software Hazard Analysis (Risk Management)",
            "Verification & Validation Plan",
            "Cybersecurity Requirements (IEC 81001-5)",
            "Off-the-Shelf (OTS) Software Management",
            "Traceability Matrix",
            "Clinical Validation Requirements"
        ],
        note: "Your SRS will include medical device-specific requirements following IEC 62304 standards with proper risk classification and safety requirements."
    },
    "Finance": {
        title: "Financial Services & Fintech",
        standards: ["PCI DSS", "SOX", "GDPR", "CCPA", "GLBA", "BSA", "Dodd-Frank", "KYC", "AML", "OFAC"],
        sections: [
            "Introduction & Regulatory Jurisdiction",
            "Regulatory Compliance Requirements (AML/KYC/CTF)",
            "Security & Data Protection (PCI DSS)",
            "Transaction Processing Requirements",
            "Reporting & Audit Requirements",
            "Risk Management Requirements",
            "Business Continuity & Disaster Recovery",
            "Third-Party Risk Management",
            "Fraud Detection & Prevention"
        ],
        note: "Your SRS will include financial regulatory compliance requirements for payment processing, data security, and audit trails."
    },
    "Aerospace": {
        title: "Aerospace & Aviation",
        standards: ["DO-178C/ED-12C", "DO-330", "ARP4754A", "DO-254", "ASIL/DAL Classification"],
        sections: [
            "Introduction & Certification Basis",
            "Plan for Software Aspects of Certification (PSAC)",
            "Software Development Plan",
            "Software Verification Plan",
            "Software Configuration Management Plan",
            "Software Quality Assurance Plan",
            "Software Requirements (High-Level & Low-Level)",
            "Software Architecture & Partitioning",
            "Tool Qualification (DO-330)",
            "Bidirectional Traceability"
        ],
        note: "Your SRS will follow DO-178C standards with appropriate Design Assurance Level (DAL) classification and certification requirements."
    },
    "Automotive": {
        title: "Automotive",
        standards: ["ISO 26262", "ASPICE", "ISO 21434", "MISRA", "AUTOSAR", "ASIL Classification"],
        sections: [
            "Introduction & Scope",
            "Functional Safety Concept (ISO 26262)",
            "System Requirements",
            "Software Safety Requirements (ASIL)",
            "Software Architecture Design (AUTOSAR)",
            "Cybersecurity Requirements (ISO 21434)",
            "ASPICE Process Requirements",
            "Verification & Validation (Code Coverage)",
            "Coding Standards Compliance (MISRA)",
            "Freedom from Interference"
        ],
        note: "Your SRS will include automotive functional safety requirements with ASIL classification and AUTOSAR compliance."
    },
    "Telecom": {
        title: "Telecommunications",
        standards: ["3GPP", "ETSI", "ITU-T", "IETF RFCs", "5G NR", "IMS"],
        sections: [
            "Introduction & Network Context (3GPP Release)",
            "3GPP Specification Compliance (Stage 1/2/3)",
            "Network Functions Requirements",
            "Protocol Stack Requirements",
            "Interface Requirements (N1, N2, N3, etc.)",
            "Network Management Requirements",
            "Quality of Service (QoS) Requirements",
            "Security Requirements (5G-AKA)",
            "Interoperability Requirements"
        ],
        note: "Your SRS will follow 3GPP standards with proper network function specifications and protocol compliance."
    },
    "Energy": {
        title: "Energy & Utilities",
        standards: ["NERC CIP", "FERC", "IEC 61850", "IEEE 1547", "DNP3", "Modbus"],
        sections: [
            "Introduction & System Overview",
            "Regulatory Compliance (NERC CIP)",
            "SCADA & Control Requirements",
            "Smart Metering Requirements (AMI)",
            "Grid Management Requirements",
            "Cybersecurity Requirements (ICS Security)",
            "Integration Requirements (GIS/CIS)",
            "Real-time Monitoring & Control",
            "Disaster Recovery & Business Continuity"
        ],
        note: "Your SRS will include critical infrastructure protection requirements and SCADA system specifications."
    },
    "E-commerce": {
        title: "E-commerce & Retail",
        standards: ["PCI DSS", "GDPR", "CCPA", "SOC 2", "ISO 27001"],
        sections: [
            "Introduction & Business Model",
            "User Management Requirements",
            "Product Catalog Requirements",
            "Shopping Cart & Checkout",
            "Order Management",
            "Payment Processing (PCI DSS)",
            "Inventory Management",
            "Analytics & Reporting",
            "Security & Privacy Compliance"
        ],
        note: "Your SRS will include e-commerce best practices with payment security and customer data protection requirements."
    },
    "Education": {
        title: "Education",
        standards: ["FERPA", "COPPA", "GDPR", "Section 508", "WCAG 2.1"],
        sections: [
            "Introduction & Educational Context",
            "Student Data Privacy (FERPA/COPPA)",
            "Learning Management System Requirements",
            "Content Management & Delivery",
            "Assessment & Grading System",
            "Accessibility Requirements (WCAG/Section 508)",
            "Integration Requirements (LTI/SIS)",
            "Analytics & Reporting",
            "Security & Compliance"
        ],
        note: "Your SRS will include educational data privacy requirements and accessibility compliance for learning systems."
    },
    "Other": {
        title: "General Software Requirements Specification",
        standards: ["IEEE 830", "ISO/IEC/IEEE 29148"],
        sections: [
            "Introduction (Purpose, Scope, Definitions, References)",
            "Overall Description (Product Perspective, User Characteristics, Operating Environment)",
            "System Features / Functional Requirements",
            "External Interface Requirements (User, Hardware, Software, Communication)",
            "Non-Functional Requirements (Performance, Security, Reliability, Scalability)",
            "Assumptions and Dependencies",
            "Glossary"
        ],
        note: "Your SRS will follow standard IEEE 830 format with general software engineering best practices suitable for various domains."
    }
};

// Initialize domain selector functionality
document.addEventListener('DOMContentLoaded', function() {
    const domainSelect = document.getElementById('domain');
    
    if (domainSelect) {
        domainSelect.addEventListener('change', function() {
            const selectedDomain = this.value;
            const domainInfoSection = document.getElementById('domainInfoSection');
            const domainCustomInput = document.getElementById('domain_custom');

            // For "Other", show the custom input field (optional) but still display domain info
            if (selectedDomain === 'Other') {
                domainCustomInput.style.display = 'block';
                // Show domain info for "Other" as well
                if (domainData[selectedDomain]) {
                    const data = domainData[selectedDomain];
                    
                    document.getElementById('domainTitle').textContent = data.title;
                    
                    const standardsList = document.getElementById('standardsList');
                    standardsList.innerHTML = data.standards.map(std => 
                        `<span class="standard-badge">${std}</span>`
                    ).join('');
                    
                    const sectionsList = document.getElementById('sectionsList');
                    sectionsList.innerHTML = data.sections.map(section => 
                        `<div class="section-item">${section}</div>`
                    ).join('');
                    
                    document.getElementById('infoNote').textContent = data.note;
                    
                    domainInfoSection.classList.add('active');
                }
            } else {
                domainCustomInput.style.display = 'none';
                
                // Display domain-specific information
                if (selectedDomain && domainData[selectedDomain]) {
                    const data = domainData[selectedDomain];
                    
                    // Update title
                    document.getElementById('domainTitle').textContent = data.title;
                    
                    // Update standards
                    const standardsList = document.getElementById('standardsList');
                    standardsList.innerHTML = data.standards.map(std => 
                        `<span class="standard-badge">${std}</span>`
                    ).join('');
                    
                    // Update sections
                    const sectionsList = document.getElementById('sectionsList');
                    sectionsList.innerHTML = data.sections.map(section => 
                        `<div class="section-item">${section}</div>`
                    ).join('');
                    
                    // Update info note
                    document.getElementById('infoNote').textContent = data.note;
                    
                    // Show the section
                    domainInfoSection.classList.add('active');
                } else {
                    domainInfoSection.classList.remove('active');
                }
            }
        });
    }
});