# Project Dublin — A Dublin Job Search Tool

A personal tool to help with a job hunt in Dublin, Ireland. It gathers job postings from
several sources, stores them in one consistent format, and uses AI to highlight the roles
that are most useful to a non-EU graduate who needs visa sponsorship.

The project is built step by step. At each step we build working software and learn the
ideas behind it. The code lives in a public GitHub repository: the code is public, but the
job data and any secrets are not.

## 1. Who this is for

The tool is built for a non-EU graduate with a master's degree in artificial intelligence
who will need visa sponsorship to work in Ireland. It is a personal tool, written in
Python, and built to cover several kinds of job sources. We start with official APIs and
leave the hardest sources for last.

## 2. The overall approach: prefer APIs, scrape only when necessary

Most of this tool should not "scrape" web pages in the traditional sense. The better design
is to pull clean data from official APIs and structured feeds wherever possible, and to
scrape web pages only where there is no other option.

Scraping sites like LinkedIn and Indeed directly is against their terms of service and
requires constant maintenance as the sites change. Instead, we pull clean data from APIs
and aggregators, and we spend our effort on the part that adds real value: the layer that
enriches each job with useful information, especially the visa signal.

## 3. Legal and privacy

Because this project runs in the EU and handles job postings, a few rules matter.

| Concern | What we do |
|---|---|
| Terms of service | LinkedIn and Indeed forbid scraping, and LinkedIn enforces this in court. We avoid scraping them directly and use official APIs instead. |
| robots.txt | We respect it. If a site disallows a path, we do not crawl it. |
| Data protection (GDPR) | Job postings can contain personal data, such as a recruiter's name or email. We keep data minimal and private, and we remove personal details unless they are truly needed. |
| Public repository | We never commit the database, scraped data, or API keys. Secrets go in a local `.env` file that is never committed, and a `.env.example` file documents what is needed. |
| Copyright | Job descriptions are copyrighted. We store a summary and a link to the original rather than republishing the full text. |
| Being polite | We limit how often we contact each site, slow down when asked, and cache results, so we never overload a source. |

## 4. Where the jobs come from

We gather jobs from several kinds of sources. We favour sources that are dependable and
likely to lead to a visa-sponsored role, rather than trying to cover everything.

**Official job APIs and aggregators.** These are documented and relatively stable, so we
start here. We use Jooble and Careerjet, which both cover Ireland and offer a free tier.
Adzuna is a common choice elsewhere, but it has no Ireland endpoint and cannot search
Dublin, so we do not use it. Reed is mainly British and The Muse lists only a curated set of
companies, so both give weak Irish coverage.

**Public and semi-state employers.** Ireland's public sector is a large employer in Dublin,
but it splits into two very different groups for our purpose. Universities such as Trinity
College Dublin, UCD, and DCU are valuable, because their research and academic roles often
qualify for a Critical Skills permit and these institutions do sponsor non-EU staff. They
usually run on an older hiring system called CoreHR, which we read by parsing web pages.
PublicJobs.ie covers the civil service, the health service, and local government. It is
large, but most of its roles require Irish or EU citizenship or residency and rarely
sponsor visas, so we record these jobs but do not make them a priority.

**Company hiring systems with clean feeds.** Many companies post their jobs through
applicant tracking systems that publish the data in a clean, consistent format. Greenhouse,
Lever, Ashby, and SmartRecruiters are the easiest of these to read and give the best return
for the effort. We focus on Dublin technology employers such as Stripe, Intercom, HubSpot,
Amazon, Google, Meta, and Irish startups.

**Company hiring systems that are harder to read.** Larger enterprises in banking, aircraft
leasing, and pharmaceuticals often use Workday, SuccessFactors, or Taleo. These do not
offer one uniform feed. Each company's setup is slightly different and can require special
handling, so they are valuable but need more maintenance. Employers like this include AIB,
Bank of Ireland, ESB, and Ryanair.

**Irish job boards.** Some Irish boards only publish jobs as ordinary web pages, so we read
them by parsing HTML. Examples are IrishJobs, Jobs.ie, and Silicon Republic.

**Sites that actively resist automation.** A few sites load their content with JavaScript or
block automated access. We use a real browser to read these only where there is no API and
it is legal to do so. LinkedIn and Indeed stay off-limits for direct scraping.

**Company directories.** Techireland, Scale Ireland, and the company lists from Enterprise
Ireland and IDA Ireland are not job boards. They tell us which companies exist in Dublin. We
use them to decide whose hiring systems to check, and to build a list of employers that are
known to sponsor visas. That sponsor list feeds the visa feature described in section 7.

## 5. The technical building blocks

A few decisions matter more than the rest.

**One consistent format.** Every source describes a job differently. The main work of the
project is converting them all into a single shape with the same fields: title, company,
location, remote policy, salary range, seniority, posting date, source, link, description,
technologies, and a visa signal. This conversion is roughly half of the whole project.

**Removing duplicates.** The same job often appears on several sources. We first match jobs
by their title, company, and location, and later use AI text similarity to catch near
duplicates.

**Keeping the list fresh.** Filled or expired jobs should disappear. We track when each job
was first and last seen, and we re-check links over time.

**Storage.** We use Postgres, with an extension called pgvector that stores AI embeddings in
the same database. This keeps the ordinary data and the AI data in one place.

**Monitoring.** Scrapers break quietly. We watch each run and raise an alert if a source
suddenly returns no jobs.

**Tools.** We use httpx and Pydantic for APIs, BeautifulSoup for HTML, and Playwright for
sites that need a browser.

## 6. Where AI genuinely helps

AI is useful in a few specific places.

It can read a messy job description and pull out structured fields. We ask it to return a
fixed format, run it only on new or changed jobs, and use a cheap model to keep costs down.

It can create text embeddings, which let us find similar jobs, detect near-duplicate
postings, and match jobs to a CV.

It can classify and tag jobs by category, seniority, technology, and, most importantly,
visa relevance.

AI is the wrong tool in a couple of places. Having an AI agent click through each website
is slow, expensive, and unreliable, so we fetch pages in a fixed way and use AI only to
read them. And running AI over every job on every run wastes money, so we only process what
has changed.

## 7. The most important feature: finding jobs that lead to a visa

The goal of this feature is a list of Dublin jobs in AI, machine learning, data, and
software that realistically lead to an Irish Critical Skills Employment Permit. For a non-EU
graduate, this solves the real problem and is a strong portfolio feature.

A short note on the immigration path. A graduate on a Stamp 2 student visa can move to the
graduate scheme (Stamp 1G), which allows up to 24 months to find work, and then to a
Critical Skills or General Employment Permit.

### It is really three questions, not one

It is tempting to treat this as a single text-classification problem and train one model.
That is the wrong approach, because the question breaks into three parts, each best solved a
different way.

The first question is whether the role qualifies for a Critical Skills permit. This is
decided by an official list of eligible occupations and a salary threshold, around €38,000
for roles on the list and around €64,000 otherwise. These figures change each year. This is
a lookup against rules, not something to learn.

The second question is whether the employer sponsors visas. This is mostly a fact about the
employer, not the job description. A company that has sponsored before is a stronger signal
than any sentence in a posting, so a list of known sponsors is the most reliable input.

The third question is whether the job description itself signals sponsorship. This is the
only part that is genuinely a language problem, and it is harder than it looks because of
negatives. "We are unable to offer visa sponsorship" contains the words but means the
opposite, and "candidates must already have the right to work in Ireland" is a negative
signal with none of the obvious keywords.

### Why not just train a classifier first

Training a model needs hundreds of hand-labelled examples that we do not have. If we label
them using keywords, the model simply relearns the keywords. The better path is to start
with rules and AI, and to train a model only later, once labelled examples have built up for
free as a by-product of the AI's own decisions and our corrections.

### How it works: cheapest checks first

We run the checks in order, from cheapest to most expensive.

First, simple rules. We look up whether the occupation and salary qualify for a permit, we
check the employer against the known-sponsor list, and we scan the description for both
positive and negative wording. The keyword scan only flags jobs for a closer look; it does
not make the final decision.

Second, an AI reading. For the jobs that the rules cannot settle, we ask a cheap AI model
(Claude Haiku) to read the description and return a clear verdict: positive, neutral, or
negative, along with its confidence, the exact wording it relied on, and a guess at permit
eligibility. We run this only on new or changed jobs, and we cache the result.

Third, and only later, a trained model. Once the AI's labelled decisions and our corrections
have built up, we can train a small model to replace the AI and reduce cost. A
personal-scale tool may never need this step.

### What this means for earlier work

A few cheap decisions now save effort later. The jobs table already includes empty columns
for the sponsorship signal, the confidence, the supporting wording, permit eligibility, and
the time of enrichment, so we can fill them in later and process only the jobs that have
changed. We also plan a separate table of employers with a flag for known sponsors. The
occupation list and salary thresholds are kept as data we can update, not values written
into the code, because they change each year.

## 8. The biggest risks

The work of converting and de-duplicating jobs is larger and less glamorous than it looks,
and it is easy to underestimate. Scraping LinkedIn and Indeed leads to being blocked, so we
start with APIs. Running AI on everything on every run wastes money. Scrapers break quietly,
so we build alerts from the start. And committing data or keys to a public repository is a
real risk, which is why the `.gitignore` file is in place from the very first commit.

## 9. Building it in phases

The project is built in phases, and each one delivers working software. The detailed,
up-to-date plan is in PHASES.md. In short, the first phase sets up the foundations, the
next adds official APIs, then company hiring systems and duplicate removal, then the AI
enrichment and the visa feature, then Irish boards and sites that need a browser, and
finally automation and a simple web interface.

## 10. How we measure success

These are the qualities that keep the project easy to run and hard to break. The aim is a
system that runs by itself, tells us when something goes wrong, and is cheap to extend.

| What we track | How we measure it | Why it matters |
|---|---|---|
| Quality of the conversion to one format | The share of jobs with every key field filled in correctly, and how many need manual fixing | Clean, consistent data makes filtering, duplicate removal, the web page, and the visa feature simple. |
| Safe re-runs | Running the pipeline again adds no duplicate rows and never corrupts data | We can run it any time and retry safely, which is what makes the tool effortless to operate. |
| Accurate duplicate removal | We never merge two different jobs, and we rarely miss a true duplicate | The list stays clean as the number of sources grows. |
| Quick detection of breakages | A broken or empty source is noticed within one run, with no silent failures | The tool tells us when something breaks instead of quietly going stale. |
| Reliance on stable sources | The share of data that comes from stable APIs rather than fragile web pages | APIs break far less often, so maintenance stays low. |
| Politeness and resilience | Few or no rate-limit or block responses, and automatic recovery from temporary errors | The tool keeps working on flaky networks without supervision. |
| Controlled AI cost | The cost and run time stay roughly flat as the database grows, and we rarely re-process a job | The AI step stays affordable as the data grows. |
| Easy to extend | We can add a source or change the city by editing configuration, not code | New sources are quick to add. |
| Fresh listings | Few expired jobs remain visible, and the typical job is recent | The list stays useful and current. |
| Trustworthy visa signal | The visa and permit labels agree with our own spot checks | The headline feature is only useful if we can trust it. |
| Hands-off operation | The pipeline runs on a schedule with no manual steps | It keeps working while we are not looking. |

The three to get right first are the conversion to one format, safe re-runs, and quick
breakage detection. These are set up in the first phase that loads real data.

Personal job-hunt numbers, such as applications sent, interviews, and offers, are private.
They are kept in Notion and the `private/` folder, never in this public repository.
