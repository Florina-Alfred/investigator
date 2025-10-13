# Summary (gpt-oss:latest)

- **Ryan Carson’s background & career**
  - Computer Science graduate from Colorado State University.
  - First job as a web developer; built Dropsend (a Dropbox‑like file transfer service) which was acquired after two years.
  - Co‑founded Treehouse, an online coding school that taught ~1 million people and grew to a 100+ employee team.
  - Currently builds Untangle, a divorce‑support platform, using AI to code at night.
  - Uses AI assistants extensively to accelerate development.

- **Three‑part system for coding with AI**
  1. **Create PRD prompt** – Generates a detailed product requirements document in Markdown, asking clarifying questions about problem, goal, target user, and success metrics.
  2. **Generate tasks prompt** – Produces a high‑level task list from the PRD, limiting to ~5 parent tasks before expanding to atomic subtasks; allows editing before sub‑task creation.
  3. **Process task list prompt** – Configures the agent to run one sub‑task at a time, request user approval, run tests after each sub‑task, and commit only when tests pass.

- **GitHub repository (≈4 000 stars)**
  - Contains three markdown prompt files: `create PRD`, `generate tasks`, and `process task list`.
  - Provides a reproducible, structured workflow that improves AI‑generated code quality.

- **Create PRD prompt details**
  - Guides the AI to ask for clarifications on:
    - The problem being solved.
    - The overall goal.
    - Target user personas.
    - Success metrics.
  - Outputs a comprehensive markdown PRD with sections like goals, user stories, success criteria, and open questions.

- **Generate tasks prompt details**
  - Reads the PRD and produces parent tasks such as:
    1. Database schema & data layer
    2. Assessment questionnaire UI
    3. Scoring logic
    4. Results display & interpretation
    5. AI recommendation integration
  - Offers the option to create a new branch before coding.

- **Process task list prompt details**
  - Executes tasks sequentially with user confirmation.
  - After each sub‑task, runs the test suite; if all tests pass, commits changes.
  - Supports acceptance or rejection of diffs and uses “get” commands for code retrieval.

- **Demo walkthrough (Untangle partner assessment feature)**
  - **PRD generation**: AI produces a markdown PRD for relationship assessment.
  - **Task list creation**: AI generates five parent tasks and asks for branch creation.
  - **Sub‑task generation**: AI expands each parent into detailed atomic subtasks and includes test creation.
  - **Execution**: Using Ghosty terminal + NeoVim, the AMP agent runs the process, creates a feature branch, writes code, runs GEST tests, and commits only on success.
  - **Static UI preview**: Agent builds a mockup of the questionnaire, displayed locally at `http://localhost:3000/partner/assessment`.

- **AI agent specifics**
  - Powered by AMP with Sonnet 4 as the default model; can switch to Oracle for deeper reasoning.
  - Uses “tagging” to provide context to the agent.
  - Supports approval workflow, diff inspection, and get commands.
  - Emulates conventional software engineering practices (branching, PRs, tests).

- **Test‑driven development with GEST**
  - Tests are added after each sub‑task to verify functionality.
  - GEST is a lightweight testing framework for TypeScript/Next.js projects.
  - Ensures code quality and reduces manual debugging loops.

- **Ryan’s solo‑founder insights**
  - Prioritize high‑pain‑point problems for niche audiences (pain‑pill vs vitamin analogy).
  - Solo founding enables control over time, quick iteration, and bootstrapping without VC.
  - AI accelerates solo development and learning, allowing you to ship without large teams.
  - Advocates for asking AI first before consulting human experts to maximize efficiency.

- **Contact & resources**
  - Twitter: **@RyanCarson** (active on X).
  - AMP: <https://amp.code.com> (free trial with $10 credit).
  - Untangle: <https://untangle-us.com> (divorce‑support platform for Connecticut).

- **Key takeaways**
  - Structured prompts (PRD → tasks → execution) produce higher quality AI‑generated code than ad‑hoc “vibe coding.”
  - Branching, testing, and incremental approvals replicate professional software development.
  - AI assistants can replace many developer tasks, but human oversight (reviews, testing, architectural decisions) remains essential.