"""
Service packages configuration for the recruiting agency
"""

SERVICE_PACKAGES = [
    {
        "package_id": "tech_startup_pack",
        "name": "Tech Startup Hiring Pack",
        "description": "Comprehensive hiring solution for tech startups and fast-growing companies",
        "target_industries": ["technology", "fintech", "edtech", "healthtech", "startup"],
        "target_roles": ["software engineer", "backend engineer", "frontend engineer", "full stack developer", 
                        "data scientist", "product manager", "ui/ux designer", "devops engineer"],
        "price_range": "$5,000 - $15,000 per role",
        "features": [
            "Technical screening and coding assessments",
            "Cultural fit evaluation",
            "30-day replacement guarantee",
            "Dedicated account manager",
            "Fast turnaround (2-3 weeks average)"
        ],
        "typical_timeline": "2-4 weeks",
        "success_rate": "92%"
    },
    {
        "package_id": "enterprise_pack",
        "name": "Enterprise Hiring Solution",
        "description": "Scalable hiring solution for large enterprises and established companies",
        "target_industries": ["finance", "healthcare", "manufacturing", "consulting", "enterprise"],
        "target_roles": ["senior manager", "director", "vp", "executive", "specialist", "analyst"],
        "price_range": "$10,000 - $25,000 per role",
        "features": [
            "Executive search and headhunting",
            "Comprehensive background checks",
            "90-day replacement guarantee",
            "Dedicated search consultant",
            "Market intelligence reports"
        ],
        "typical_timeline": "4-8 weeks",
        "success_rate": "89%"
    },
    {
        "package_id": "bulk_hiring_pack",
        "name": "Volume Hiring Package",
        "description": "Cost-effective solution for high-volume recruitment needs",
        "target_industries": ["retail", "logistics", "customer service", "sales", "operations"],
        "target_roles": ["sales representative", "customer service", "operations", "coordinator", 
                        "associate", "specialist"],
        "price_range": "$2,000 - $8,000 per role",
        "features": [
            "Streamlined screening process",
            "Group interviews and assessments",
            "Bulk pricing discounts",
            "Rapid deployment",
            "14-day replacement guarantee"
        ],
        "typical_timeline": "1-3 weeks",
        "success_rate": "85%"
    },
    {
        "package_id": "specialized_roles_pack",
        "name": "Specialized Roles Package",
        "description": "Expert recruitment for niche and highly specialized positions",
        "target_industries": ["healthcare", "legal", "engineering", "research", "academia"],
        "target_roles": ["doctor", "lawyer", "engineer", "researcher", "scientist", "architect"],
        "price_range": "$8,000 - $20,000 per role",
        "features": [
            "Industry-specific expertise",
            "Professional network access",
            "Credential verification",
            "60-day replacement guarantee",
            "Consultation on role requirements"
        ],
        "typical_timeline": "3-6 weeks",
        "success_rate": "87%"
    },
    {
        "package_id": "remote_hiring_pack",
        "name": "Remote Talent Acquisition",
        "description": "Global talent acquisition for remote and distributed teams",
        "target_industries": ["technology", "marketing", "design", "content", "consulting"],
        "target_roles": ["remote developer", "digital marketer", "content writer", "designer", 
                        "virtual assistant", "consultant"],
        "price_range": "$3,000 - $12,000 per role",
        "features": [
            "Global talent pool access",
            "Timezone compatibility matching",
            "Remote work assessment",
            "Cultural integration support",
            "45-day replacement guarantee"
        ],
        "typical_timeline": "2-5 weeks",
        "success_rate": "90%"
    }
]

# Common role synonyms for better matching
ROLE_SYNONYMS = {
    "software engineer": ["developer", "programmer", "software developer", "backend engineer", "frontend engineer"],
    "ui/ux designer": ["designer", "ux designer", "ui designer", "product designer"],
    "data scientist": ["data analyst", "ml engineer", "ai engineer", "data engineer"],
    "product manager": ["pm", "product owner", "product lead"],
    "sales representative": ["sales rep", "salesperson", "sales executive", "account executive"],
    "customer service": ["customer support", "support agent", "help desk"],
    "devops engineer": ["devops", "infrastructure engineer", "site reliability engineer", "sre"]
}

# Industry synonyms for better matching
INDUSTRY_SYNONYMS = {
    "technology": ["tech", "software", "it", "saas"],
    "finance": ["financial services", "banking", "fintech"],
    "healthcare": ["medical", "health", "pharma", "healthtech"],
    "education": ["edtech", "learning", "academic"],
    "retail": ["e-commerce", "ecommerce", "consumer"]
}
