"""AI Orchestrator: coordinates the 4 agents, enforces security, keeps the audit log."""
import uuid

import pandas as pd

from .agents import analysis_agent, data_agent, planner, web_agent
from .config import OUTPUT_DIR
from .security import AuditLog, is_allowed


def _records(df: pd.DataFrame, n=50):
    return df.head(n).astype(object).where(df.head(n).notna(), None).to_dict(orient="records")


def run_workflow(request: str, approved: bool = False) -> dict:
    run_id = uuid.uuid4().hex[:8]
    log = AuditLog(run_id)
    result = {"run_id": run_id, "status": "ok", "logs": log.entries}

    try:
        # ---- Module 1: Planner
        log.add("Planner", "Received request, building plan")
        plan = planner.plan(request)
        result["plan"] = plan
        if plan["error"]:
            log.add("Planner", plan["error"], "error")
            result["status"] = "error"
            result["message"] = plan["error"]
            return result
        log.add("Planner", f"Plan ready: {len(plan['steps'])} steps, target {plan['url']}")

        # ---- Security & human approval
        if not is_allowed(plan["url"]) and not approved:
            log.add("Security", f"Domain not in allow-list: {plan['url']} -> human approval required", "warn")
            result["status"] = "needs_approval"
            result["message"] = "This website is not on the approved list. Approve to continue."
            return result
        log.add("Security", "Domain approved" + (" (by human)" if approved else " (allow-list)"))

        # ---- Module 2: Web extraction
        log.add("WebAgent", "Fetching page and extracting data")
        ext = web_agent.extract(plan["url"], plan["table_index"])
        raw = ext["df"]
        log.add("WebAgent", f"{ext['note']} Extracted {raw.shape[0]} rows x {raw.shape[1]} cols ({ext['mode']} mode)")
        result["source_title"] = ext["title"]
        result["raw_preview"] = _records(raw.astype(object), 10)
        result["raw_columns"] = [str(c) for c in raw.columns]

        # ---- Module 3: Cleaning & transformation
        log.add("DataAgent", "Cleaning and transforming")
        cl = data_agent.clean_and_transform(
            raw, plan["options"]["deduplicate"], plan["options"]["fill_missing"]
        )
        df = cl["df"]
        for op in cl["operations"]:
            log.add("DataAgent", op)
        result["cleaning"] = cl["operations"]
        result["stats"] = cl["stats"]
        result["columns"] = list(df.columns)
        result["clean_preview"] = _records(df, 50)

        # ---- Module 4: Analysis & validation
        log.add("AnalysisAgent", "Running analysis and validation")
        s = cl["stats"]
        val = analysis_agent.validate((s["raw_rows"], s["raw_cols"]), s["raw_missing"], df, s["duplicates_removed"])
        ana = analysis_agent.analyze(df)
        log.add("AnalysisAgent", f"Data quality score: {val['quality_score']}/100")
        result["validation"] = val
        result["analysis"] = ana

        # ---- Export
        path = OUTPUT_DIR / f"{run_id}.csv"
        df.to_csv(path, index=False)
        log.add("Orchestrator", f"Saved dataset to outputs/{run_id}.csv")
        result["download"] = f"/api/download/{run_id}"
        result["message"] = "Workflow completed."

    except Exception as e:  # tool/source failures are reported, not crashed
        log.add("Orchestrator", f"Workflow failed: {e}", "error")
        result["status"] = "error"
        result["message"] = str(e)

    return result
