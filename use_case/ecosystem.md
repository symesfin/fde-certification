# The ecosystem you deploy into

Where your application would actually run, inside your actual firm.

> **Week 1 starts this file. Week 9 finishes it.**
> TC1 Step 10 asks eight questions. The full Week 9 checklist has around thirty,
> and the eight are a strict subset — so nothing here gets thrown away.

Describe patterns, not specifics. "On-prem OpenShift, images from an internal
registry, no public egress" is useful to everyone and identifies nobody. Never
put real hostnames, IPs, or architecture diagrams in this file.

---

## Week 1 — the first eight questions

<!-- Answered in TC1 Step 10. Bring these back from a real conversation. -->

**Who did you ask?** (role, not name)

Myself: I am the client's only engineer and own its deployment. Approval is the client's (row 7).

| # | Question | Answer |
| :---: | --- | --- |
| 1 | Where do internal apps run? (k8s, ECS, App Service, a VM someone maintains) | Serverless functions run by a workflow orchestrator, object storage for files, a managed database for the vendor master. Deploys are a manual CI run with a production confirmation step. |
| 2 | Which cloud? AWS, Azure, GCP, on-prem, several? | AWS, in the client's account; the model runs on GCP (Vertex AI). |
| 3 | Is there an internal container registry? | Yes: the client's AWS account routinely uses ECR. |
| 4 | How do users log in? (Okta, Entra ID, Ping, SAML, homegrown) | Accountants don't: they drop files in their usual network folders and a sync agent pushes them over a private VPN. Engineers use AWS SSO. A web UI would need an auth decision that hasn't been made; the existing private network is the cheapest option. |
| 5 | Can the app reach the internet? Egress proxy? Allowlist? | Yes, at least to GCP: the pipeline already calls the model there from AWS. |
| 6 | Where do secrets come from? (Vault, Secrets Manager, Key Vault) | AWS Secrets Manager (the model's service-account credentials). |
| 7 | Who approves a deployment, and what review does it need? | Cutover: the AP systems lead and the COO sponsor agree based on shadow-mode reports, plus a formal SOW. The sponsor can't approve it alone under the current SOW, so it also needs whoever signs SOWs above him; that role isn't recorded yet. |
| 8 | Is there an approved internal LLM endpoint already? | No client gateway recorded: production calls Gemini on Vertex AI directly. The course app uses my employer's LLM gateway, which the client allows its invoice data through. |

**What surprised you?**

How well the overall solution works. My client has used many classical SaaS tools and products to improve this process, but adapting LLMs will turn out to be a major cost and time advantage.

**What would you have to change about your app to deploy there?**

The model string becomes Vertex Gemini (or Bedrock, to stay in one cloud). `vendors.csv` is replaced by the vendor-master database query. The input becomes a storage key instead of base64: the workflow service caps a payload at 256 KB, so a PDF can't travel in the request. The handler runs as a serverless function, not a Gradio server.

---

## Week 1 — what your machine told you

<!--
  Paste the egress probe output from Session 1 here. It is evidence, and it
  frequently disagrees with what people believe about their own network.
-->

<!-- probe output here -->

**Does this match what you were told in the table above?** Where it doesn't, that
gap is worth chasing — it usually means a proxy nobody documented.

---

## Week 9 — the full checklist

<!--
  TC9 extends this same file. Do not start a new one: the point is that the git
  history shows one continuous piece of work from Week 1 to Week 9.
-->

<!-- Week 9 -->
