# Project Dublin — Phase Plan

This is the build plan, taken one phase at a time. Each phase delivers working software and
teaches a specific set of ideas. For the full design and the reasoning behind it, see
Project_dublin.md.

## Phase 0 — Foundations (done)

Set up a safe, reproducible project: the repository layout, a Python environment, secret
handling, and the database.

- [x] Repository structure, a Python 3.12 virtual environment, a `.gitignore` file, and a `.env.example` file
- [x] A Postgres database running in Docker, with a jobs table managed by a migration runner

This phase is complete: the project installs cleanly and the jobs table exists locally.

## Phase 1 — Official job APIs (in progress)

Pull real Dublin jobs from job-search APIs that cover Ireland, starting with Jooble and then
Careerjet, and save each job into the database in one consistent format.

- [x] Get a Jooble API key and make the first authenticated request
- [x] Page through the results and respect the API's rate limits
- [ ] Describe the API response as typed models, so bad data is caught early
- [ ] Convert each job into our standard format and save it without creating duplicates
- [ ] Add Careerjet as a second source behind the same interface

What you learn: how REST APIs work, authentication, paging, rate limits, data validation,
and the step that turns many different formats into one. That conversion step is the core of
the whole project.

This phase is complete when one command fetches Dublin jobs and saves them, and running it
again adds no duplicates.

## Phase 2 — Company hiring systems and duplicate removal (not started)

This phase pulls job openings from the systems companies use to manage hiring, called
applicant tracking systems. We begin with the platforms that publish clean, consistent
data: Greenhouse, Lever, Ashby, and SmartRecruiters. We then add the harder enterprise
platforms such as Workday, SuccessFactors, and Taleo, which differ from one company to the
next and need more maintenance.

We also read company directories such as Techireland and Scale Ireland. These do not list
jobs themselves. They tell us which Dublin companies exist, so we know whose systems to
check and which employers are known to sponsor visa applicants.

The same job often appears on more than one source, so this phase also combines repeated
listings into a single record.

What you learn: reading data from applicant tracking systems, discovering employers,
combining different formats into one, and detecting duplicates.

This phase is complete when a job found on two sources is stored only once.

## Phase 3 — AI enrichment and the visa filter (not started)

Use AI to read each job description and tag it with two things: whether the employer is
likely to sponsor a visa, and whether the role qualifies for an Irish Critical Skills
Employment Permit. This is the most valuable feature in the project. We keep costs low by
running the AI only on new or changed jobs.

What you learn: structured AI output, processing only what has changed, controlling cost,
text embeddings, and searching by meaning.

This phase is complete when we can list Dublin jobs that both qualify for a Critical Skills
permit and show a positive sponsorship signal.

## Phase 4 — Irish job boards and public-sector roles (not started)

Add Irish job boards that publish jobs only as web pages, which we read by parsing the HTML:
IrishJobs, Jobs.ie, and Silicon Republic. Also add Dublin's universities, namely Trinity
College Dublin, UCD, and DCU, which often sponsor non-EU staff. Record PublicJobs.ie as
well, although most public-sector roles require Irish or EU residency and rarely sponsor
visas.

What you learn: parsing HTML, respecting robots.txt, and limiting how often we contact each
site.

## Phase 5 — Sites that need a real browser (not started)

Some sites load their content with JavaScript or actively block automated access. Where
there is no API and it is legal to do so, use a headless browser (Playwright) to read them.
LinkedIn and Indeed remain off-limits for direct scraping.

What you learn: headless browsers, anti-bot measures, and when scraping is the wrong choice.

## Phase 6 — Automation and a simple interface (not started)

Run the whole pipeline automatically on a schedule using GitHub Actions, watch for
breakages, drop expired jobs, and build a small Streamlit web page to search and filter the
results.

What you learn: scheduling, monitoring, and building a simple front end.

## How we measure success

There are two kinds of measurement, kept separate.

System health, such as how many jobs each source returns, how fresh they are, how many
duplicates are caught, and how much the AI costs, is tracked from Phase 1 onward. The full
list is in Project_dublin.md.

Personal job-hunt numbers, such as applications sent, interviews, and offers, are private.
They are kept in Notion and the `private/` folder, never in this public repository.
