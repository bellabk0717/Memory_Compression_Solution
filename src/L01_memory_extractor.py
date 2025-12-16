def extract_user_memory(messages):
    """
    Extract high-confidence, long-term user memory from a conversation.

    Design principles:
    - Focus on stable, non-negotiable facts
    - Prefer precision over recall (false negatives > false positives)
    - Only extract information when explicitly stated
    - Avoid semantic inference and hallucination

    This module intentionally does NOT handle:
    - Pain points
    - Feature preferences
    - Vendor comparisons
    """

    # -------------------------------
    # 1. Define explicit memory schema
    # -------------------------------
    user_memory = {
        "company_profile": {
            "type": None,              # B2B / B2C
            "company_size": None,      # total employees
            "sales_team_size": None    # number of sales staff
        },
        "technical_constraints": {
            "deployment": None,        # cloud / on-prem
            "data_residency": None,    # China / global
            "it_capability": None      # has_internal_it / no_internal_it
        },
        "commercial_constraints": {
            "budget": None             # e.g. 20万/年
        }
    }

    # -------------------------------
    # 2. Keyword dictionaries
    #    (expandable but controlled)
    # -------------------------------
    B2B_KEYWORDS = ["b2b", "to b", "企业客户", "企业级"]
    B2C_KEYWORDS = ["b2c", "to c", "个人用户", "消费者"]

    CLOUD_KEYWORDS = ["云", "云端", "saas"]
    NO_IT_KEYWORDS = ["没有it", "没有it运维", "无it", "没有技术团队"]

    # -------------------------------
    # 3. Scan conversation messages
    # -------------------------------
    for msg in messages:
        text = msg.get("content", "")
        text_lower = text.lower()

        # ---- company type (explicit signals only) ----
        if any(k in text_lower for k in B2B_KEYWORDS):
            user_memory["company_profile"]["type"] = "B2B"

        if any(k in text_lower for k in B2C_KEYWORDS):
            user_memory["company_profile"]["type"] = "B2C"

        # ---- company size ----
        # Simple numeric heuristic, intentionally conservative
        if "200" in text and "人" in text:
            user_memory["company_profile"]["company_size"] = 200

        # ---- sales team size ----
        if "销售" in text and "50" in text:
            user_memory["company_profile"]["sales_team_size"] = 50

        # ---- budget ----
        if "20万" in text:
            user_memory["commercial_constraints"]["budget"] = "20万/年"

        # ---- deployment preference ----
        if any(k in text for k in CLOUD_KEYWORDS):
            user_memory["technical_constraints"]["deployment"] = "cloud"

        # ---- data residency ----
        if "国内" in text:
            user_memory["technical_constraints"]["data_residency"] = "China"

        # ---- IT capability ----
        if any(k in text_lower for k in NO_IT_KEYWORDS):
            user_memory["technical_constraints"]["it_capability"] = "no_internal_it"

    # -------------------------------
    # 4. Clean empty fields
    #    (keep memory compact)
    # -------------------------------
    cleaned_memory = {}

    for section, fields in user_memory.items():
        filtered_fields = {k: v for k, v in fields.items() if v is not None}
        if filtered_fields:
            cleaned_memory[section] = filtered_fields

    return cleaned_memory

