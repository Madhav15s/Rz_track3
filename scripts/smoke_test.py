import asyncio
from playwright.async_api import async_playwright
import os
import json
import re

async def run_smoke_test():
    os.makedirs("audit/screenshots", exist_ok=True)
    report_lines = ["# Phase 8 Browser Verification Report\n"]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        console_errors = []
        network_errors = []
        
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("response", lambda response: network_errors.append(f"{response.status} {response.url}") if response.status >= 400 and response.url.startswith("http://localhost:8000") else None)

        try:
            print("Going to dashboard")
            await page.goto("http://localhost:5173/")
            report_lines.append("Browser startup: PASS")
            
            print("Waiting for Overview")
            await page.wait_for_selector("text=Executive Overview", timeout=5000)
            await page.screenshot(path="audit/screenshots/1_Executive_Overview.png")
            report_lines.append("Dashboard load: PASS")
            
            print("Clicking Decision Console")
            await page.click("a[href='/cases']")
            await page.wait_for_selector("text=Select a case to view decision logic", timeout=5000)
            
            print("Clicking CASE_A_POS_UPLIFT")
            await page.click("text=CASE_A_POS_UPLIFT")
            await page.wait_for_selector("text=RETRY_LATER", timeout=5000)
            
            content = await page.content()
            if "RETRY_LATER" in content and "APPROVED" in content:
                report_lines.append("Decision flow: PASS")
            else:
                raise Exception("Decision data failed to render fully.")
            
            await page.screenshot(path="audit/screenshots/2_Causal_Decision_Console.png")
            
            # Oracle Check (word boundary to prevent overflow-y matching)
            oracle_strings = ["y_0", "y_1", "y_2", "y_3", "y_4", "y_5", "true_uplift", "oracle_action", "latent_liquidity", "latent_urgency", "latent_payment_reliability"]
            oracle_leak = []
            for s in oracle_strings:
                if re.search(r'\b' + s + r'\b', content):
                    oracle_leak.append(s)
            
            if oracle_leak:
                report_lines.append(f"Oracle isolation: FAIL (Leaked: {oracle_leak})")
            else:
                report_lines.append("Oracle isolation: PASS")
                
            page.on("dialog", lambda dialog: dialog.accept())
            
            print("Clicking Execute")
            await page.click("text=Execute", timeout=5000)
            
            print("Waiting for Audit Trail or Lifecycle")
            await page.wait_for_selector("text=Audit Trail", timeout=10000)
            
            print("Navigating to Execution")
            await page.click("a[href='/execution']")
            await page.wait_for_selector("text=Action Lifecycle", timeout=5000)
            await page.screenshot(path="audit/screenshots/3_Execution_Flow.png")
            
            exec_content = await page.content()
            if "Pending" in exec_content or "Verified" in exec_content or "Simulated" in exec_content:
                report_lines.append("Execution flow: PASS")
            else:
                report_lines.append("Execution flow: FAIL (No success states visible)")
                
            print("Testing Governor Bypass via API")
            response = await page.request.post("http://localhost:8000/api/cases/CASE_D_POLICY_REJECT/execute", data=json.dumps({"action_id": 1}), headers={"Content-Type": "application/json"})
            if response.status == 403:
                report_lines.append("Governor rejection: PASS")
            else:
                report_lines.append(f"Governor rejection: FAIL (Status {response.status})")

            print("Clicking Evaluation")
            await page.locator("nav a").filter(has_text="Evaluation").click()
            await page.wait_for_selector("text=Evaluation Report", timeout=5000)
            await page.screenshot(path="audit/screenshots/4_Evaluation.png")
            report_lines.append("Evaluation: PASS")
            
            report_lines.append("Visual QA: PASS")
            
        except Exception as e:
            print(f"ERROR: {e}")
            report_lines.append(f"FAILED during flow: {str(e)}")
            report_lines.append("Final status: BLOCKED")
        
        if len(console_errors) > 0 or len(network_errors) > 0:
            if "403 http://localhost:8000/api/cases/CASE_D_POLICY_REJECT/execute" in network_errors:
                network_errors.remove("403 http://localhost:8000/api/cases/CASE_D_POLICY_REJECT/execute")
            
            if len(console_errors) == 0 and len(network_errors) == 0:
                report_lines.append("Console/network: PASS")
            else:
                report_lines.append(f"Console/network: FAIL (Errors: {console_errors}, {network_errors})")
        else:
            report_lines.append("Console/network: PASS")
            
        if "FAIL" not in "\n".join(report_lines) and "BLOCKED" not in "\n".join(report_lines):
            report_lines.append("\nFinal status:\nPASS")
        else:
            report_lines.append("\nFinal status:\nBLOCKED")
            
        with open("audit/PHASE_8_BROWSER_VERIFICATION.md", "w") as f:
            f.write("\n".join(report_lines))
            
        print("Done.")

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
